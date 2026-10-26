"""
Test and Demonstration script for Step 2: Oral Testimony Parsing & Normalization (Saaras + Sarvam-105B).
"""

import json
from pathlib import Path
from oral_testimony_pipeline import OralTestimonyParser, print_vanshavali_tree, get_sample_regional_testimony
from schema import OralTestimonyNormalizedSchema

def run_step2_demo():
    print("=" * 70)
    print("  STEP 2: ORAL TESTIMONY PARSING & NORMALIZATION (SAARAS + INDUS)")
    print("=" * 70)

    parser = OralTestimonyParser()
    sample_text = get_sample_regional_testimony()

    print("\n[1] INPUT VERBATIM ORAL TESTIMONY (Spoken Regional Dialect):")
    print("-" * 70)
    print(sample_text)
    print("-" * 70)

    # Process testimony
    print("\n[2] PROCESSING VIA SAARAS & SARVAM-105B (INDUS)...")
    normalized_data = parser.process_oral_testimony(transcript_text=sample_text)

    # Validate with Pydantic model
    assert isinstance(normalized_data, OralTestimonyNormalizedSchema)

    # Display Reconstructed Vanshavali
    print_vanshavali_tree(normalized_data.vanshavali)

    # Display Succession Order
    print("STATED SUCCESSION ORDER (CHRONOLOGICAL DEVOTION):")
    print("-" * 70)
    for step in normalized_data.stated_succession_order:
        status_tag = "[CONTESTED / DISPUTED]" if step.contested else "[UNCONTESTED]"
        print(f"Step {step.step_order} ({step.approximate_year_or_era}) {status_tag}:")
        print(f"  From Ancestor: {step.from_person_id}")
        print(f"  To Successors: {', '.join(step.to_person_ids)}")
        print(f"  Basis: {step.basis_of_succession}")
        print()

    # Display Property Grievance
    print("SPECIFIC PROPERTY GRIEVANCE ALLEGED:")
    print("-" * 70)
    g = normalized_data.property_grievance
    print(f"Allegation Category : {g.allegation_category}")
    print(f"Disputed Asset      : {g.disputed_asset_description}")
    print(f"Location            : {g.location_details}")
    print(f"Claimed Share       : {g.claimed_share}")
    print(f"Adverse Party (IDs) : {', '.join(g.adverse_party_ids)}")
    print(f"Grievance Narrative :\n  {g.grievance_narrative}")
    print(f"Relief Sought       :\n  {g.relief_sought}")

    # Display Chronological Timeline
    print("\n" + "-" * 70)
    print("CHRONOLOGICAL TIMELINE OF HISTORICAL EVENTS:")
    print("-" * 70)
    for event in normalized_data.chronological_timeline:
        print(f"• [{event.temporal_anchor}] {event.description}")

    # Output file verification
    output_file = Path("normalized_oral_testimony.json")
    print(f"\n[3] Full Normalized JSON Schema exported to: {output_file.resolve()} ({output_file.stat().st_size} bytes)")
    print("=" * 70)

if __name__ == "__main__":
    run_step2_demo()
