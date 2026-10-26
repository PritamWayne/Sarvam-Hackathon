"""
Main Land Deed Ingestion & Document Verification Pipeline.
Integrates:
- Pre-processing (Deskewing, Contrast Enhancement, Margin Isolation)
- Visual Authenticity Markers Detection (Stamps, Signatures, Kaifiyat)
- Sarvam AI Document Intelligence (Sarvam Vision / Pages Extract)
- Structured JSON Generation adhering to LandDeedVerificationOutput schema
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
import cv2
import numpy as np

from preprocessing.preprocessor import DocumentPreprocessor
from visual_verification.artifact_detector import VisualArtifactDetector
from sarvam_engine.sarvam_client import SarvamLandDeedExtractor
from models.deed_schema import (
    LandDeedVerificationOutput,
    DocumentVerificationSummary,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class LandDeedVerificationPipeline:
    def __init__(self, sarvam_api_key: str = None, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.preprocessor = DocumentPreprocessor(output_debug_dir=os.path.join(output_dir, "preprocessed"))
        self.artifact_detector = VisualArtifactDetector(debug_dir=os.path.join(output_dir, "artifacts"))
        self.sarvam_extractor = SarvamLandDeedExtractor(api_key=sarvam_api_key)

    def run(
        self,
        input_file: str,
        save_visual_overlay: bool = True,
        output_json_path: str = None,
    ) -> LandDeedVerificationOutput:
        """
        Executes the 3-step pipeline on an uploaded scanned land deed:
        1. Pre-process (Deskew, Enhance Contrast, Isolate Margins)
        2. Detect Visual Authenticity Markers (Stamps, Signatures, Kaifiyat)
        3. Extract Layout & Text Data (Sarvam Vision / Doc-AI)
        """
        print("=" * 70)
        print("LAND DEED INGESTION & DOCUMENT VERIFICATION PIPELINE")
        print(f"Target Document: {input_file}")
        print("=" * 70)

        # -------------------------------------------------------------
        # STEP 1: Pre-processing (Deskew, Enhance Contrast, Isolate Margins)
        # -------------------------------------------------------------
        print("\n[Step 1/3] Pre-processing Document...")
        prep_results = self.preprocessor.process(input_file, save_debug=True)

        raw_img = prep_results["raw_image"]
        enhanced_img = prep_results["enhanced_image"]
        skew_angle = prep_results["skew_angle"]
        margin_info = prep_results["margin_info"]
        enhanced_file_path = prep_results["enhanced_path"]

        print(f"  ✓ Deskewing complete: Detected skew = {skew_angle:+.2f}° (Rotated & Border-Preserved)")
        print(f"  ✓ Contrast enhanced: CLAHE + illumination leveling applied.")
        print(f"  ✓ Marginal notes isolated: Left Kaifiyat column activity detected = {margin_info['left_margin']['has_notes']}")

        # -------------------------------------------------------------
        # STEP 2: Visual Authenticity Markers Detection
        # -------------------------------------------------------------
        print("\n[Step 2/3] Detecting Visual Authenticity Markers...")
        visual_report, annotated_overlay = self.artifact_detector.verify_document(
            enhanced_img, margin_info=margin_info
        )

        base_name = os.path.splitext(os.path.basename(input_file))[0]
        overlay_path = None
        if save_visual_overlay:
            overlay_path = os.path.join(self.output_dir, f"{base_name}_verified_overlay.png")
            cv2.imwrite(overlay_path, annotated_overlay)
            print(f"  ✓ Visual verification overlay saved at: {overlay_path}")

        print(f"  ✓ Official Revenue Stamps: {len(visual_report.revenue_stamps)} detected "
              f"(Mandatory Present: {visual_report.mandatory_stamps_present})")
        print(f"  ✓ Signatures (Tehsildar/Patwari): {len(visual_report.signatures)} detected "
              f"(Mandatory Present: {visual_report.signatures_present})")
        print(f"  ✓ Marginal Remarks (Kaifiyat): {len(visual_report.marginal_remarks)} detected "
              f"(Present: {visual_report.kaifiyat_present})")
        print(f"  ✓ Document Authenticity Status: {visual_report.authenticity_status} "
              f"(Authenticity Score: {visual_report.authenticity_score * 100:.1f}%)")

        # -------------------------------------------------------------
        # STEP 3: Layout & Text Extraction (Sarvam Vision / Doc-AI)
        # -------------------------------------------------------------
        print("\n[Step 3/3] Running Layout & Text Extraction via Sarvam Vision API...")

        # Submit enhanced document to Sarvam Document AI
        sarvam_raw_response = self.sarvam_extractor.extract_with_sarvam_api(
            file_path=enhanced_file_path or input_file
        )

        # Parse into validated Deed Metadata and Tabular Tenure Holders
        metadata, ownership_shares = self.sarvam_extractor.parse_to_schema(sarvam_raw_response)

        print(f"  ✓ Deed Type: {metadata.deed_type}")
        print(f"  ✓ Khasra / Khata: Khasra {metadata.land_parcel_details.khasra_numbers} | Khata {metadata.land_parcel_details.khata_number}")
        print(f"  ✓ Location: Village {metadata.geographic_jurisdiction.village_mauza}, "
              f"Tehsil {metadata.geographic_jurisdiction.tehsil}, {metadata.geographic_jurisdiction.district}")
        print(f"  ✓ Plot Area: {metadata.land_parcel_details.plot_area.stated_value} {metadata.land_parcel_details.plot_area.stated_unit} "
              f"({metadata.land_parcel_details.plot_area.standardized_sq_meters} Sq. Meters / {metadata.land_parcel_details.plot_area.standardized_hectares} Hectares)")
        print(f"  ✓ Recorded Tenure Holders: {len(ownership_shares)} co-sharers parsed.")

        # -------------------------------------------------------------
        # Summary & JSON Output Packaging
        # -------------------------------------------------------------
        confidence_map = {
            "stamps_confidence": max([s.confidence for s in visual_report.revenue_stamps], default=0.0),
            "signatures_confidence": max([s.confidence for s in visual_report.signatures], default=0.0),
            "overall_authenticity": visual_report.authenticity_score,
        }

        notes = []
        if visual_report.mandatory_stamps_present:
            notes.append("Official revenue seals validated with characteristic violet/red stamp ink profile.")
        else:
            notes.append("WARNING: Missing required official revenue seal or stamp paper header.")

        if visual_report.signatures_present:
            notes.append("Tehsildar and Patwari cursive attestation signatures verified in signing zone.")
        else:
            notes.append("WARNING: No recognized official signatures detected.")

        if visual_report.kaifiyat_present:
            notes.append("Kaifiyat (Marginal Remarks) column contains recorded mutation/court remarks.")

        summary = DocumentVerificationSummary(
            document_name=os.path.basename(input_file),
            document_type=metadata.deed_type,
            processed_at=datetime.now(timezone.utc).isoformat(),
            authenticity_status=visual_report.authenticity_status,
            mandatory_stamps_present=visual_report.mandatory_stamps_present,
            signatures_present=visual_report.signatures_present,
            kaifiyat_present=visual_report.kaifiyat_present,
            confidence_scores=confidence_map,
            verification_notes=notes,
        )

        final_output = LandDeedVerificationOutput(
            document_verification_summary=summary,
            visual_authenticity_markers=visual_report,
            parsed_deed_metadata=metadata,
            ownership_shares=ownership_shares,
            raw_extracted_text_preview=metadata.marginal_remarks_kaifiyat_text,
        )

        # Save JSON output
        if not output_json_path:
            output_json_path = os.path.join(self.output_dir, f"{base_name}_verification_result.json")

        with open(output_json_path, "w", encoding="utf-8") as f:
            f.write(final_output.model_dump_json(indent=2))

        print(f"\n[Result] Structured JSON Output generated at: {output_json_path}")
        print("=" * 70)
        return final_output


def main():
    parser = argparse.ArgumentParser(description="Sarvam Land Deed Ingestion & Document Verification")
    parser.add_argument("--input", default="sample_land_deed.png", help="Path to scanned land deed image or PDF")
    parser.add_argument("--output", default=None, help="Output JSON path")
    parser.add_argument("--api-key", default=None, help="Sarvam AI API Subscription Key")
    args = parser.parse_args()

    pipeline = LandDeedVerificationPipeline(sarvam_api_key=args.api_key)
    result = pipeline.run(args.input, output_json_path=args.output)

    # Print JSON preview
    print("\n--- STRUCTURED OUTPUT JSON (PREVIEW) ---")
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False)[:2500] + "\n... [Full JSON saved in output file]")


if __name__ == "__main__":
    main()
