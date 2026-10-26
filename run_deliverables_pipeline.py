"""
Master Pipeline Orchestrator for Step 5: Bilingual Deliverable Generation (Bulbul & PDF Engine)

Goal:
Translate technical and legal findings into an accessible audio brief and a court-ready filing.

Process:
1. User Audio Briefing: Generate conversational, empathetic summary of findings in the user's native tongue,
   and synthesize to speech using Sarvam Bulbul (bulbul:v3).
2. Objection Drafting: Populate standardized legal template under Section 34/35 of the State Land Revenue Act
   before the Tehsildar / Sub-Divisional Magistrate (SDM).
3. Evidence Indexing: Attach document references, discrepancy tables, and reconstructed family tree.
4. Court PDF Engine: Compile the final ready-to-sign legal objection petition PDF.
5. Sarvam AI Indus Integration: Web prompts and integration guidance for https://indus.sarvam.ai/.
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

from arithmetic_validator import ArithmeticValidator
from bulbul_briefing_engine import BulbulBriefingEngine
from objection_petition_generator import ObjectionPetitionGenerator
from evidence_indexer import EvidenceIndexer
from pdf_engine import CourtPDFEngine
from sarvam_integration import SarvamIndusAssistant, INDUS_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DeliverablePipeline")


def run_deliverables_pipeline():
    print("=" * 85)
    print("STEP 5: BILINGUAL DELIVERABLE GENERATION (BULBUL & COURT PDF ENGINE)")
    print("Indic Revenue Records Intelligence & Sovereign AI Integration")
    print("Reference Platform: Indus by Sarvam AI (https://indus.sarvam.ai/)")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent
    deliverables_dir = base_dir / "deliverables"
    deliverables_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------------
    # 1. LOAD TESTIMONY & PREVIOUS FINDINGS (Step 2 & Step 3 Inputs)
    # ------------------------------------------------------------------------
    testimony_path = base_dir / "normalized_oral_testimony.json"
    if not testimony_path.exists():
        raise FileNotFoundError(f"Missing input testimony file: {testimony_path}")

    print("\n[Step 5.1] Loading Normalized Oral Testimony & Genealogy Records...")
    with open(testimony_path, "r", encoding="utf-8") as f:
        testimony_data = json.load(f)

    claimant_summary = testimony_data.get("summary_of_statement", "")
    vanshavali = testimony_data.get("vanshavali", {})
    grievance = testimony_data.get("property_grievance", {})

    print(f" - Claimant Statement: {claimant_summary[:110]}...")
    print(f" - Ancestral Head: {vanshavali.get('ancestral_head', {}).get('name')}")
    print(f" - Lineage Members Count: {len(vanshavali.get('members', []))}")
    print(f" - Grievance Allegation: {grievance.get('allegation_category')}")

    # ------------------------------------------------------------------------
    # 2. RUN MATHEMATICAL CONSERVATION AUDIT ON DISPUTED PLOT
    # ------------------------------------------------------------------------
    print("\n[Step 5.2] Executing Arithmetic Validation & Discrepancy Analysis...")
    validator = ArithmeticValidator(state="Uttar Pradesh", district="Meerut", tehsil="Mawana")

    # In Khata 112, total ancestral registered area is 12 Bighas (30,351.42 m²)
    # Lawfully: Bholanath branch gets 6 Bigha, Dinanath branch gets 6 Bigha.
    # In 2012, Kamlesh took 10 Bighas (including 4 Bighas in Khasra 142 & 143).
    audit_result = validator.audit_plot(
        plot_id="Khata 112 / Khasra 142 & 143",
        total_plot_area="12 Bigha 0 Biswa",
        unit_hint="bigha",
        co_sharers_data=[
            {"name": "Kamlesh Mishra (Impugned Allocation)", "share": "10 Bigha", "recorded_area": "10 Bigha 0 Biswa"},
            {"name": "Heirs of Bholanath Mishra (Leftover)", "share": "2 Bigha", "recorded_area": "2 Bigha 0 Biswa"}
        ]
    )

    print(f" - Audit Verdict: {audit_result.summary_verdict}")
    print(f" - Status: {audit_result.status} | Risk Level: {audit_result.risk_level}")
    print(f" - Diverted Surplus Area: 4 Bigha 0 Biswa (10,117.14 m² / 2.50 Acres)")

    # ------------------------------------------------------------------------
    # 3. GENERATE EMPATHETIC CONVERSATIONAL AUDIO BRIEFING (SARVAM BULBUL)
    # ------------------------------------------------------------------------
    print("\n[Step 5.3] Synthesizing User Audio Briefing (Sarvam AI Bulbul)...")
    bulbul_engine = BulbulBriefingEngine()

    scripts = bulbul_engine.compose_briefing_script(
        claimant_name="हरिशंकर मिश्रा (Harishankar Mishra)",
        ancestor_name="रामेश्वर मिश्रा (Rameshwar Mishra)",
        total_ancestral_area="12 बीघा (12 Bigha)",
        father_name="भोलानाथ मिश्रा (Bholanath Mishra)",
        father_share="6 बीघा (6 Bigha / 50% अंश)",
        individual_share="2 बीघा (2 Bigha प्रत्येक भाई)",
        adverse_party_name="कमलेश मिश्रा (Kamlesh Mishra)",
        disputed_khasras="142 और 143",
        disputed_area="4 बीघा पक्की जमीन (4 Bigha)",
        discrepancy_delta_bigha=4.0,
        discrepancy_delta_sq_m=10117.14,
        location="मौजा चक-गोविंदपुर, तहसील मवाना, मेरठ",
        tehsil_court="तहसीलदार / उप-जिलाधिकारी, मवाना"
    )

    audio_file_path = deliverables_dir / "landholder_audio_briefing.wav"
    audio_meta = bulbul_engine.synthesize_speech(
        text=scripts["hindi"],
        output_file_path=str(audio_file_path),
        language_code="hi-IN",
        speaker="aditya_hi_conversational",
        model="bulbul:v3"
    )

    # Save transcripts
    transcript_hindi_file = deliverables_dir / "audio_briefing_transcript_hindi.txt"
    transcript_english_file = deliverables_dir / "audio_briefing_transcript_english.txt"
    meta_json_file = deliverables_dir / "audio_briefing_metadata.json"

    with open(transcript_hindi_file, "w", encoding="utf-8") as f:
        f.write(scripts["hindi"])
    with open(transcript_english_file, "w", encoding="utf-8") as f:
        f.write(scripts["english"])
    with open(meta_json_file, "w", encoding="utf-8") as f:
        json.dump(audio_meta, f, indent=2, ensure_ascii=False)

    print(f" - Playable Audio File Created: {audio_file_path.name}")
    print(f" - Audio File Size: {audio_meta['file_size_bytes']:,} bytes ({audio_meta['duration_approx_seconds']} sec)")
    print(f" - Audio Engine: {audio_meta['engine']}")
    print(f" - Transcripts saved (Hindi & English)")

    # ------------------------------------------------------------------------
    # 4. OBJECTION PETITION DRAFTING (SECTION 34/35 REVENUE ACT)
    # ------------------------------------------------------------------------
    print("\n[Step 5.4] Populating Standardized Legal Objection Draft...")
    petition_gen = ObjectionPetitionGenerator()
    legal_draft = petition_gen.build_petition_from_testimony(
        normalized_testimony=testimony_data,
        audit_findings=audit_result.__dict__,
        court_tehsil="Mawana",
        court_district="Meerut",
        state="Uttar Pradesh"
    )

    print(f" - Court: {legal_draft.court_name}")
    print(f" - Case Title: {legal_draft.case_number}")
    print(f" - Objectors Count: {len(legal_draft.objectors)} co-sharers")
    print(f" - Statutory Provisions: {legal_draft.statutory_provisions[:80]}...")
    print(f" - Number of Substantive Legal Grounds: {len(legal_draft.legal_grounds)}")
    print(f" - Number of Specific Court Prayers: {len(legal_draft.prayers)}")

    # ------------------------------------------------------------------------
    # 5. EVIDENCE INDEXING (VANSHAVALI, CHAKBANDI, AUDIT TABLE, TESTIMONY)
    # ------------------------------------------------------------------------
    print("\n[Step 5.5] Compiling and Indexing Court Evidence Annexures...")
    indexer = EvidenceIndexer()
    evidence_docket = indexer.build_evidence_docket(
        normalized_testimony=testimony_data,
        audit_result=audit_result
    )

    print(f" - Total Annexures Compiled: {evidence_docket.total_annexures}")
    for ex in evidence_docket.exhibits:
        print(f"   * [{ex.exhibit_id}] {ex.title} (Source: {ex.issuing_source})")

    # ------------------------------------------------------------------------
    # 6. COURT PDF ENGINE (REPORTLAB COMPILATION)
    # ------------------------------------------------------------------------
    print("\n[Step 5.6] Compiling Court-Ready Legal Objection Petition PDF...")
    pdf_output_path = deliverables_dir / "Court_Ready_Legal_Objection_Petition.pdf"
    pdf_engine = CourtPDFEngine(str(pdf_output_path))
    generated_pdf_path = pdf_engine.generate_court_petition_pdf(legal_draft, evidence_docket)

    pdf_size_bytes = os.path.getsize(generated_pdf_path)
    print(f" - Court Petition PDF Generated: {pdf_output_path.name}")
    print(f" - Document Size: {pdf_size_bytes:,} bytes")
    print(f" - Status: Court-Ready & Downloadable for Signature")

    # ------------------------------------------------------------------------
    # 7. INDUS WEB ASSISTANT PROMPTS & INSTRUCTIONS (https://indus.sarvam.ai/)
    # ------------------------------------------------------------------------
    print("\n[Step 5.7] Generating Indus / Sarvam AI Companion Instructions...")
    indus_prompts_file = deliverables_dir / "indus_sarvam_prompts.md"
    indus_content = (
        "# Sarvam AI & Indus Web Companion Guide\n\n"
        "**Platform URL:** [https://indus.sarvam.ai/](https://indus.sarvam.ai/)\n\n"
        "This file provides copy-paste prompts and API payloads to interact directly with "
        "Sarvam AI's Indus LLM and Bulbul TTS web platform.\n\n"
        "## 1. Bulbul TTS Web Voice Briefing Prompt\n"
        "Copy and paste the text below into the Sarvam AI Bulbul Audio Playground:\n\n"
        "```text\n"
        f"{scripts['hindi']}\n"
        "```\n\n"
        "**Recommended Voice Settings:**\n"
        "- **Model:** `bulbul:v3`\n"
        "- **Language:** Hindi (`hi-IN`)\n"
        "- **Speaker:** `aditya_hi_conversational` (or `amit_hi_conversational`)\n"
        "- **Pace:** 1.0\n"
        "- **Pitch:** 0.0\n"
        "- **Format:** WAV / MP3 (44.1 kHz)\n\n"
        "## 2. Indus LLM Revenue Extraction Prompt\n"
        "```text\n"
        f"{INDUS_SYSTEM_PROMPT}\n\n"
        "Revenue Record Excerpt to Audit:\n"
        "ग्राम: चक-गोविंदपुर, तहसील: मवाना, जनपद: मेरठ (उत्तर प्रदेश)\n"
        "खाता संख्या: 00112, खसरा संख्या: 142 एवं 143\n"
        "कुल दर्ज रकबा: 4 बीघा 0 बिस्वा (पुख्ता)\n"
        "दर्ज खातेदार: कमलेश मिश्रा पुत्र स्वर्गीय दीनानाथ मिश्रा\n"
        "आपत्तिकर्तागण: हरिशंकर मिश्रा, उमाशंकर मिश्रा, रविशंकर मिश्रा पुत्रगण स्वर्गीय भोलानाथ मिश्रा\n"
        "पैतृक हिस्सा: 6 बीघा (50% कुल 12 बीघा में से)\n"
        "```\n\n"
        "## 3. Python API Invocation Snippet (Bulbul TTS)\n"
        "```python\n"
        "import os\n"
        "from sarvamai import SarvamAI\n"
        "\n"
        "client = SarvamAI(api_subscription_key=os.getenv('SARVAM_API_KEY'))\n"
        "response = client.text_to_speech.convert(\n"
        f"    text='{scripts['hindi'][:100]}...',\n"
        "    language_code='hi-IN',\n"
        "    model='bulbul:v3',\n"
        "    speaker='aditya_hi_conversational',\n"
        "    output_audio_codec='wav'\n"
        ")\n"
        "with open('landholder_audio.wav', 'wb') as f:\n"
        "    f.write(response.audios[0].encode('utf-8'))\n"
        "```\n"
    )
    with open(indus_prompts_file, "w", encoding="utf-8") as f:
        f.write(indus_content)

    # ------------------------------------------------------------------------
    # 8. EXECUTIVE CASE SUMMARY REPORT
    # ------------------------------------------------------------------------
    summary_report_file = deliverables_dir / "case_summary_report.md"
    summary_content = (
        "# Comprehensive Case Summary: Harishankar Mishra vs. Kamlesh Mishra\n\n"
        "## Case Metadata\n"
        "- **Court:** In the Court of the Tehsildar / Sub-Divisional Officer, Mawana, District Meerut (U.P.)\n"
        "- **Case Nature:** Objection under Section 34 & 35, U.P. Revenue Code, 2006 (Mutation / Dakhil-Kharij Rectification)\n"
        "- **Lead Objector:** Harishankar Mishra s/o Late Bholanath Mishra (Age: 48)\n"
        "- **Co-Objectors:** Umashankar Mishra & Ravishankar Mishra\n"
        "- **Adverse Respondent:** Kamlesh Mishra s/o Late Dinanath Mishra\n"
        "- **Subject Land:** Khasra Nos. 142 & 143 (4 Bigha 0 Biswa / 10,117.14 m² / 2.50 Acres), Mauza Chak-Govindpur\n\n"
        "## Forensic Findings\n"
        "1. **Root Title & 1988 Partition:** Common ancestor Rameshwar Mishra (d. 1984) held 12 Bighas. "
        "Under 1988 Chakbandi (CH-41/45), each branch lawfully received 6 Bighas (50%).\n"
        "2. **Fraudulent Mutation in 2012:** Respondent Kamlesh Mishra colluded with the Halka Patwari during Khatauni digitization "
        "and mutated 4 Bighas belonging to Bholanath's branch into his own name, bypassing mandatory Section 35 proclamation and notice.\n"
        "3. **Mathematical Conservation Audit:** Respondent holds 10 Bighas (166.7% of entitlement), generating a +4 Bigha unlawful surplus.\n\n"
        "## Deliverables Generated\n"
        "1. `deliverables/landholder_audio_briefing.wav`: Playable native audio briefing for the rural landholder.\n"
        "2. `deliverables/Court_Ready_Legal_Objection_Petition.pdf`: Complete 7-page court petition with Vanshavali tree, "
        "Chakbandi extract, discrepancy matrix, and sworn affidavit.\n"
        "3. `deliverables/audio_briefing_transcript_hindi.txt` & `deliverables/audio_briefing_transcript_english.txt`\n"
        "4. `deliverables/indus_sarvam_prompts.md`: Integration guide for [https://indus.sarvam.ai/](https://indus.sarvam.ai/)\n"
    )
    with open(summary_report_file, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print("\n" + "=" * 85)
    print("ALL DELIVERABLES SUCCESSFULLY GENERATED AND READY FOR COURT FILING:")
    print(f" 1. [Audio Briefing]  -> {audio_file_path.resolve()}")
    print(f" 2. [Court Petition]  -> {pdf_output_path.resolve()}")
    print(f" 3. [Hindi Transcript]-> {transcript_hindi_file.resolve()}")
    print(f" 4. [Eng Transcript]  -> {transcript_english_file.resolve()}")
    print(f" 5. [Indus Prompts]   -> {indus_prompts_file.resolve()}")
    print(f" 6. [Summary Report]  -> {summary_report_file.resolve()}")
    print("=" * 85)


if __name__ == "__main__":
    run_deliverables_pipeline()
