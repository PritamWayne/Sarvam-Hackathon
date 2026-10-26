"""
Demonstration and Verification Suite for Step 3: Area Unit Normalization & Arithmetic Validation.
Executes end-to-end normalization, fraction evaluation, and mathematical conservation audits
across diverse Indian revenue regimes (UP Bigha-Biswa, Punjab Kanal-Marla, Maharashtra Ha-R, and Anna-Pai).
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from arithmetic_validator import ArithmeticValidator
from sarvam_integration import SarvamIndusAssistant


def run_all_demonstrations():
    print("=" * 80)
    print("STEP 3: AREA UNIT NORMALIZATION & ARITHMETIC VALIDATION AUDIT SUITE")
    print("Engine: Indic Revenue Records Conservation & Forensic Audit System")
    print("Reference: Indus by Sarvam AI (https://indus.sarvam.ai/)")
    print("=" * 80)

    # ------------------------------------------------------------------------
    # CASE 1: Punjab Jamabandi - Kanal & Marla System (Mathematical Conservation)
    # ------------------------------------------------------------------------
    print("\n>>> CASE 1: Punjab Jamabandi (Kanal-Marla System)")
    print("Scenario: Khewat No. 42 / Khasra No. 14//5, Tehsil Nakodar, District Jalandhar, Punjab")
    validator_punjab = ArithmeticValidator(state="Punjab", district="Jalandhar", tehsil="Nakodar")

    audit_1 = validator_punjab.audit_plot(
        plot_id="Khasra 14//5 (Khewat 42)",
        total_plot_area="8 Kanal 0 Marla",  # Exactly 1 Acre = 4,046.856 m^2
        unit_hint="kanal",
        co_sharers_data=[
            {"name": "Baldev Singh s/o Harbhajan Singh", "share": "1/2"},
            {"name": "Gurpreet Kaur w/o Jagtar Singh", "share": "1/4"},
            {"name": "Harinder Singh s/o Jagtar Singh", "share": "1/8"},
            {"name": "Manpreet Singh s/o Jagtar Singh", "share": "1/8"}
        ]
    )

    report_1 = validator_punjab.generate_markdown_report(audit_1)
    print(report_1)

    # ------------------------------------------------------------------------
    # CASE 2: Uttar Pradesh Khatauni - Pucca Bigha (SURPLUS ALERT: Land Created Out of Thin Air)
    # ------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(">>> CASE 2: Uttar Pradesh Khatauni (Pucca Bigha - SURPLUS FRAUD / ANOMALY)")
    print("Scenario: Khata No. 112, Khasra No. 248, Tehsil Mawana, District Meerut, UP")
    validator_up = ArithmeticValidator(state="Uttar Pradesh", district="Meerut", tehsil="Mawana")

    # Registered plot area is 2 Bigha 10 Biswa (2.5 Bigha = 6,323.21 m^2)
    # But 3 brothers each claim 1 Bigha (Total = 3 Bigha = 120%)
    audit_2 = validator_up.audit_plot(
        plot_id="Khata 112 / Khasra 248",
        total_plot_area="2 Bigha 10 Biswa",
        unit_hint="bigha",
        co_sharers_data=[
            {"name": "Ram Swaroop s/o Mangal Singh", "share": "1 Bigha", "recorded_area": "1 Bigha 0 Biswa"},
            {"name": "Shyam Lal s/o Mangal Singh", "share": "1 Bigha", "recorded_area": "1 Bigha 0 Biswa"},
            {"name": "Mohan Lal s/o Mangal Singh", "share": "1 Bigha", "recorded_area": "1 Bigha 0 Biswa"}
        ]
    )

    report_2 = validator_up.generate_markdown_report(audit_2)
    print(report_2)

    # ------------------------------------------------------------------------
    # CASE 3: Maharashtra 7/12 Extract (DEFICIT ALERT: Missing / Unallocated Land)
    # ------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(">>> CASE 3: Maharashtra 7/12 (Metric Ha-R - DEFICIT ANOMALY)")
    print("Scenario: Gat No. 89, Taluka Haveli, District Pune, Maharashtra")
    validator_mh = ArithmeticValidator(state="Maharashtra", district="Pune", tehsil="Haveli")

    # Total Area: 1 Hectare 20 Are (12,000 m^2)
    # Co-sharers only account for 90 Are (75%), leaving 30 Are unaccounted
    audit_3 = validator_mh.audit_plot(
        plot_id="Gat No. 89",
        total_plot_area="1 Ha 20 R",
        unit_hint="hectare",
        co_sharers_data=[
            {"name": "Dnyaneshwar Vitthal Patil", "share": "40/120"},  # 40 Are
            {"name": "Tukaram Vitthal Patil", "share": "50/120"}       # 50 Are
            # Remaining 30/120 is missing from record
        ]
    )

    report_3 = validator_mh.generate_markdown_report(audit_3)
    print(report_3)

    # ------------------------------------------------------------------------
    # CASE 4: Traditional Anna-Pai Revenue Notation (Rajasthan / UP)
    # ------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(">>> CASE 4: Traditional Anna-Pai Revenue Notation (16 Annas = 1 Rupee = 100%)")
    validator_raj = ArithmeticValidator(state="Rajasthan", district="Jaipur", tehsil="Sanganer")

    audit_4 = validator_raj.audit_plot(
        plot_id="Khasra 502/1",
        total_plot_area="5 Bigha",
        unit_hint="bigha",
        co_sharers_data=[
            {"name": "Girdhari Lal Sharma", "share": "8 Annas"},      # 50.0%
            {"name": "Brijesh Sharma", "share": "4 Annas"},           # 25.0%
            {"name": "Radha Raman Sharma", "share": "4 Annas"}        # 25.0%
        ]
    )

    report_4 = validator_raj.generate_markdown_report(audit_4)
    print(report_4)

    # Save reports to files
    with open("audit_report_case1_punjab.md", "w", encoding="utf-8") as f:
        f.write(report_1)
    with open("audit_report_case2_up_surplus.md", "w", encoding="utf-8") as f:
        f.write(report_2)
    with open("audit_report_case3_mh_deficit.md", "w", encoding="utf-8") as f:
        f.write(report_3)

    print("\n" + "=" * 80)
    print("AUDIT REPORTS SUCCESSFULLY GENERATED AND SAVED:")
    print(" - audit_report_case1_punjab.md")
    print(" - audit_report_case2_up_surplus.md")
    print(" - audit_report_case3_mh_deficit.md")
    print("=" * 80)


if __name__ == "__main__":
    run_all_demonstrations()
