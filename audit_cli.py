"""
Command-Line Interface for Step 3: Area Unit Normalization & Arithmetic Validation.
Supports JSON file input, interactive terminal queries, demo executions,
and Indus prompt export for https://indus.sarvam.ai/.
"""

import sys
import os
import argparse
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from arithmetic_validator import ArithmeticValidator
from sarvam_integration import SarvamIndusAssistant
from run_audit_demo import run_all_demonstrations


def audit_from_file(file_path: str, output_format: str = "markdown"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = ArithmeticValidator(
        state=data.get("state"),
        district=data.get("district"),
        tehsil=data.get("tehsil")
    )

    result = validator.audit_plot(
        plot_id=data.get("plot_id", "Plot-Input"),
        total_plot_area=data.get("total_registered_area"),
        unit_hint=data.get("unit_hint"),
        co_sharers_data=data.get("co_sharers", [])
    )

    if output_format == "json":
        print(validator.generate_json_report(result))
    else:
        print(validator.generate_markdown_report(result))


def interactive_audit():
    print("\n--- Interactive Land Record Arithmetic Audit ---")
    state = input("State (e.g. Uttar Pradesh, Punjab, Maharashtra) [default: Uttar Pradesh]: ").strip() or "Uttar Pradesh"
    district = input("District (e.g. Meerut, Jalandhar, Pune) [default: Meerut]: ").strip() or "Meerut"
    tehsil = input("Tehsil / Taluka [default: Mawana]: ").strip() or "Mawana"
    plot_id = input("Plot / Khasra / Gat Number [default: Khasra 101]: ").strip() or "Khasra 101"
    total_area = input("Total Registered Area (e.g. '2 Bigha 10 Biswa', '8 Kanal', '1 Ha 20 R'): ").strip()
    
    if not total_area:
        print("Total registered area is required.")
        return

    print("\nEnter Co-Sharers (Press Enter on empty name when finished):")
    co_sharers = []
    idx = 1
    while True:
        name = input(f" Co-sharer #{idx} Name (or Enter to finish): ").strip()
        if not name:
            break
        share = input(f" Co-sharer #{idx} Share (e.g. '1/3', '4 Annas', '25%', or '1 Bigha'): ").strip()
        co_sharers.append({"name": name, "share": share})
        idx += 1

    validator = ArithmeticValidator(state=state, district=district, tehsil=tehsil)
    result = validator.audit_plot(
        plot_id=plot_id,
        total_plot_area=total_area,
        co_sharers_data=co_sharers
    )

    print("\n" + "=" * 80)
    print(validator.generate_markdown_report(result))
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Step 3: Area Unit Normalization & Arithmetic Validation Engine"
    )
    parser.add_argument("--demo", action="store_true", help="Run multi-state revenue record audit demonstrations")
    parser.add_argument("--file", type=str, help="Path to input JSON file containing land record details")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output report format")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive audit session")
    parser.add_argument("--indus-prompt", action="store_true", help="Display Indus Sarvam AI prompt template")

    args = parser.parse_args()

    if args.demo:
        run_all_demonstrations()
    elif args.file:
        audit_from_file(args.file, args.format)
    elif args.interactive:
        interactive_audit()
    elif args.indus_prompt:
        sample_doc = "Khatauni Extract: Meerut District, Tehsil Mawana. Khasra 248, Total Area 2 Bigha 10 Biswa. Co-sharers: Ram Swaroop (1 Bigha), Shyam Lal (1 Bigha), Mohan Lal (1 Bigha)."
        print(SarvamIndusAssistant.get_indus_web_prompt(sample_doc))
    else:
        # Default run demo
        run_all_demonstrations()


if __name__ == "__main__":
    main()
