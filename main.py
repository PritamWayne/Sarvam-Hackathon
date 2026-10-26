"""
Main entry point for Step 1: Ingestion & Document Verification (Sarvam Vision / Pages).
Extracts raw text, tabular ownership data, and visual authenticity markers from scanned land deeds.
"""

import os
import sys
import json
from dotenv import load_dotenv
from pipeline import LandDeedVerificationPipeline
from generator.sample_generator import generate_scanned_land_deed

load_dotenv()

def main():
    sample_deed = "sample_land_deed.png"
    if not os.path.exists(sample_deed):
        print("[*] Generating authentic scanned Indian Land Deed sample...")
        generate_scanned_land_deed(output_path=sample_deed)

    # Initialize and execute pipeline
    pipeline = LandDeedVerificationPipeline(output_dir="output")
    result = pipeline.run(sample_deed)

    print("\n" + "=" * 70)
    print(" PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f" Output JSON: output/{os.path.splitext(sample_deed)[0]}_verification_result.json")
    print(f" Visual Verification Overlay: output/{os.path.splitext(sample_deed)[0]}_verified_overlay.png")
    print("\nTo view the interactive visual dashboard, run:")
    print("   python web_dashboard.py")
    print("   Open http://127.0.0.1:8080 in your browser.")
    print("=" * 70)

if __name__ == "__main__":
    main()
