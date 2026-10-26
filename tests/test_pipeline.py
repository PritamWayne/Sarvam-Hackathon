"""
Unit and Integration Tests for Land Deed Ingestion & Document Verification.
"""

import os
import json
import pytest
from preprocessing.preprocessor import DocumentPreprocessor
from visual_verification.artifact_detector import VisualArtifactDetector
from sarvam_engine.sarvam_client import SarvamLandDeedExtractor
from pipeline import LandDeedVerificationPipeline


def test_preprocessing():
    assert os.path.exists("sample_land_deed.png"), "Sample deed does not exist"
    preprocessor = DocumentPreprocessor(output_debug_dir="output/test_preprocessed")
    result = preprocessor.process("sample_land_deed.png")

    assert result["raw_image"] is not None
    assert result["enhanced_image"] is not None
    assert "margin_info" in result
    assert result["margin_info"]["left_margin"]["has_notes"] is True


def test_visual_artifact_detector():
    preprocessor = DocumentPreprocessor(output_debug_dir="output/test_preprocessed")
    prep = preprocessor.process("sample_land_deed.png")

    detector = VisualArtifactDetector()
    report, overlay = detector.verify_document(prep["enhanced_image"], prep["margin_info"])

    assert report.mandatory_stamps_present is True
    assert report.signatures_present is True
    assert report.kaifiyat_present is True
    assert report.authenticity_status in ["VERIFIED", "FLAGGED_MISSING_MARKERS"]
    assert len(report.revenue_stamps) > 0
    assert len(report.signatures) > 0


def test_area_standardization():
    extractor = SarvamLandDeedExtractor()

    # Test Bigha conversion
    sq_m, hectares = extractor.standardize_area_unit(2.5, "Bigha")
    assert sq_m > 6000.0
    assert hectares > 0.6

    # Test Hectare conversion
    sq_m, hectares = extractor.standardize_area_unit(1.0, "Hectare")
    assert sq_m == 10000.0
    assert hectares == 1.0


def test_pipeline_e2e():
    pipeline = LandDeedVerificationPipeline(output_dir="output/test_run")
    output = pipeline.run("sample_land_deed.png")

    assert output.document_verification_summary.mandatory_stamps_present is True
    assert output.document_verification_summary.signatures_present is True
    assert output.parsed_deed_metadata.land_parcel_details.khata_number is not None
    assert len(output.ownership_shares) > 0

    # Ensure JSON schema compliance
    json_str = output.model_dump_json()
    parsed = json.loads(json_str)
    assert "document_verification_summary" in parsed
    assert "visual_authenticity_markers" in parsed
    assert "parsed_deed_metadata" in parsed
    assert "ownership_shares" in parsed


if __name__ == "__main__":
    pytest.main(["-v", "tests/test_pipeline.py"])
