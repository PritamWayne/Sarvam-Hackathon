"""
Test and Demonstration Script for Step 3: Area Unit Normalization & Arithmetic Validation.
Directly aligns with Step 2 (Oral Testimony & Vanshavali) and feeds into Step 4 (Title Audit Matrix).
"""

import sys
import os
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from arithmetic_validator import ArithmeticValidator
from area_normalizer import AreaNormalizer
from regional_standards import resolve_regional_standard, SQ_M_PER_ACRE


def run_step3_demonstration():
    print("=" * 75)
    print("  STEP 3: AREA UNIT NORMALIZATION & ARITHMETIC VALIDATION")
    print("  (Standardize Localized Measurements & Verify Mathematical Integrity)")
    print("  Reference: Indus by Sarvam AI (https://indus.sarvam.ai/)")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # PART 1: REGIONAL UNIT STANDARDIZATION
    # -------------------------------------------------------------------------
    print("\n[PART 1] LOCAL MEASUREMENT STANDARD DETERMINATION (District / Tehsil):")
    print("-" * 75)
    
    test_locations = [
        ("Uttar Pradesh", "Meerut", "Mawana", "Pucca Bigha (Western UP standard)"),
        ("Uttar Pradesh", "Bijnor", "Najibabad", "Kuchha Bigha standard"),
        ("Punjab", "Jalandhar", "Nakodar", "Kanal-Marla (Standard Karam 66 in)"),
        ("Maharashtra", "Pune", "Haveli", "Metric System (Hectare - Are - Guntha)"),
        ("Rajasthan", "Jaipur", "Sanganer", "Bigha-Biswa (Pucca standard)")
    ]

    for state, dist, tehsil, desc in test_locations:
        std = resolve_regional_standard(state=state, district=dist, tehsil=tehsil)
        print(f"• Location: {tehsil}, {dist}, {state}")
        print(f"  Standard: {std['name']}")
        print(f"  Formula : {std['description']}")
        print()

    # -------------------------------------------------------------------------
    # PART 2: CONNECTING WITH STEP 2 TESTIMONY (Mishra Ancestral Estate Audit)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("[PART 2] ARITHMETIC AUDIT OF DISPUTED PARCEL (Mauza Chak-Govindpur):")
    print("-" * 75)
    print("Case: Estate of Late Rameshwar Mishra (12 Bighas Ancestral Land)")
    print("Claimed partition: Bholanath branch (6 Bighas) vs Dinanath branch (6 Bighas)")
    print("Disputed Mutation: Kamlesh Mishra mutated 10 Bighas while 3 brothers claim 6 Bighas.")
    
    validator_up = ArithmeticValidator(state="Uttar Pradesh", district="Varanasi", tehsil="Pindra")
    
    # Audit Scenario A: Customary Lawful Succession (Conserved 100%)
    print("\n>>> Scenario 2A: Lawful Coparcenary Succession (Batwara as per Vanshavali)")
    audit_lawful = validator_up.audit_plot(
        plot_id="Mauza Chak-Govindpur (Holding 01)",
        total_plot_area="12 Bigha",
        unit_hint="bigha",
        co_sharers_data=[
            {"name": "Harishankar Mishra s/o Bholanath (Claimant)", "share": "2 Bigha"},
            {"name": "Umashankar Mishra s/o Bholanath", "share": "2 Bigha"},
            {"name": "Ravishankar Mishra s/o Bholanath", "share": "2 Bigha"},
            {"name": "Kamlesh Mishra s/o Dinanath", "share": "6 Bigha"}
        ]
    )
    print(validator_up.generate_markdown_report(audit_lawful))

    # Audit Scenario B: Disputed Record (Surplus Anomaly / Land Created Out of Thin Air)
    print("\n>>> Scenario 2B: Disputed Record with Fraudulent Mutation Claim (Surplus Defect)")
    audit_disputed = validator_up.audit_plot(
        plot_id="Mauza Chak-Govindpur (Disputed Record)",
        total_plot_area="12 Bigha",
        unit_hint="bigha",
        co_sharers_data=[
            {"name": "Kamlesh Mishra (Adverse Party claimed holding)", "share": "10 Bigha", "recorded_area": "10 Bigha"},
            {"name": "Harishankar Mishra (Claimant asserted rightful share)", "share": "2 Bigha", "recorded_area": "2 Bigha"},
            {"name": "Umashankar Mishra (Brother share)", "share": "2 Bigha", "recorded_area": "2 Bigha"},
            {"name": "Ravishankar Mishra (Brother share)", "share": "2 Bigha", "recorded_area": "2 Bigha"}
        ]
    )
    print(validator_up.generate_markdown_report(audit_disputed))

    # Save output audit report
    out_path = "audit_report_step3_mishra_estate.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Step 3: Area Unit Normalization & Arithmetic Validation Report\n\n")
        f.write("## Lawful Baseline\n\n")
        f.write(validator_up.generate_markdown_report(audit_lawful))
        f.write("\n\n---\n\n## Disputed Record Analysis\n\n")
        f.write(validator_up.generate_markdown_report(audit_disputed))

    print(f"\n[3] Forensic Arithmetic Audit Report saved to: {out_path}")
    print("=" * 75)


if __name__ == "__main__":
    run_step3_demonstration()
