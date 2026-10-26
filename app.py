"""
Sarvam Indic Land Records Intelligence & Verification Engine (Streamlit Web Application)
A sovereign Indian AI platform powered by Sarvam AI:
- Sarvam Vision / Pages: Document Preprocessing & Visual Authenticity Verification
- Saaras & Sarvam-105B: Oral Testimony Parsing & Genealogical Vanshavali Reconstruction
- Indic Area Normalizer: Regional Measurement Systems & Mathematical Conservation Audit
- Title Audit Engine: Succession Law & Discrepancy Matrix Analysis
- Sarvam Bulbul & PDF Engine: Empathetic Audio Briefings & Court-Ready Legal Objection Petitions
"""

import os
import sys
import json
import base64
from pathlib import Path
from fractions import Fraction
from datetime import datetime
import streamlit as st
from PIL import Image

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 standard on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import core system modules
from regional_standards import REGIONAL_STANDARDS, resolve_regional_standard, SQ_M_PER_ACRE, SQ_M_PER_HECTARE
from area_normalizer import AreaNormalizer
from arithmetic_validator import ArithmeticValidator, PlotAuditResult
from pipeline import LandDeedVerificationPipeline
from oral_testimony_pipeline import OralTestimonyParser, get_sample_regional_testimony, generate_sample_normalized_schema
from title_audit_engine import TitleAuditEngine
from bulbul_briefing_engine import BulbulBriefingEngine
from objection_petition_generator import ObjectionPetitionGenerator
from evidence_indexer import EvidenceIndexer
from pdf_engine import CourtPDFEngine
from run_deliverables_pipeline import run_deliverables_pipeline

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="भूमि-प्रमाण | Sarvam Indic Land Records Intelligence",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern Indic Legal AI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        padding: 24px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
    }
    .main-header p {
        margin-top: 6px;
        font-size: 1.05rem;
        color: #c7d2fe;
    }
    .badge-sarvam {
        background: #f59e0b;
        color: #1e1b4b;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 8px;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .status-badge {
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
    }
    .status-conserved { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .status-surplus { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .status-deficit { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .tree-node {
        background-color: #f1f5f9;
        border-left: 4px solid #4f46e5;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.svg", width=42)
    st.markdown("## **भूमि-प्रमाण**")
    st.caption("Sarvam Indic Land Records Intelligence Platform")

    module = st.radio(
        "Select Pipeline Stage:",
        [
            "📄 1. Document Ingestion & Verification",
            "🎙️ 2. Oral Testimony & Vanshavali",
            "📐 3. Area Normalization & Audit",
            "🔍 4. Title Discrepancy Matrix",
            "⚖️ 5. Legal Brief & Court Petition"
        ]
    )

    st.markdown("---")
    st.markdown("### 🤖 **Sarvam AI Models**")
    st.markdown("""
    - **Vision / Pages**: Doc-AI & Stamps
    - **Saaras:v4**: Dialect-Aware STT
    - **Sarvam-105B**: Indic Legal Reasoning
    - **Bulbul:v3**: Conversational TTS
    """)

    st.markdown("---")
    st.markdown("### ⚙️ **System Environment**")
    api_key = os.getenv("SARVAM_API_KEY", "")
    if api_key and not api_key.startswith("sk_placeholder"):
        st.success("API Key Active (Indus)")
    else:
        st.info("Operating Mode: Hybrid (Live + Resilient Offline Engine)")

    st.caption("Version: 1.0.0 | Sarvam Indic Pipeline")


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_file_download_bytes(file_path: Path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            return f.read()
    return None


# -----------------------------------------------------------------------------
# Header Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>भूमि-प्रमाण : Indic Land Records Intelligence & Verification</h1>
    <p>End-to-End Sovereign AI Platform for Scanned Deeds, Oral Vanshavali, Regional Area Auditing & Legal Petition Generation</p>
    <span class="badge-sarvam">POWERED BY SARVAM AI (INDUS • VISION • SAARAS • BULBUL)</span>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MODULE 1: LAND DEED INGESTION & DOCUMENT VERIFICATION
# =============================================================================
if module == "📄 1. Document Ingestion & Verification":
    st.subheader("📄 Step 1: Scanned Land Deed Ingestion & Visual Authenticity")
    st.write(
        "Extract raw text, tabular ownership data, and visual authenticity markers "
        "(Official Revenue Seals, Patwari/Tehsildar Signatures, and Marginal Kaifiyat Remarks) "
        "from scanned Indian land deeds (Khatauni, Khasra, Jamabandi, Sale Deed)."
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Input Scanned Deed")
        input_choice = st.radio(
            "Choose Document Source:",
            ["Default Verified Sample Deed (UP Khatauni)", "Upload Custom Deed (PNG/JPG/PDF)"]
        )

        sample_path = BASE_DIR / "sample_land_deed.png"
        target_path = sample_path

        if input_choice == "Upload Custom Deed (PNG/JPG/PDF)":
            uploaded_file = st.file_uploader("Upload Deed", type=["png", "jpg", "jpeg", "pdf"])
            if uploaded_file is not None:
                upload_dir = BASE_DIR / "output" / "uploads"
                upload_dir.mkdir(parents=True, exist_ok=True)
                target_path = upload_dir / uploaded_file.name
                with open(target_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved: {uploaded_file.name}")
        
        run_btn = st.button("🚀 Run Verification Pipeline", type="primary", use_container_width=True)

    # Execute or Load Cached Result
    output_json = BASE_DIR / "output" / f"{target_path.stem}_verification_result.json"
    output_overlay = BASE_DIR / "output" / f"{target_path.stem}_verified_overlay.png"
    enhanced_img = BASE_DIR / "output" / "preprocessed" / f"{target_path.stem}_enhanced.png"

    if run_btn:
        with st.spinner("Processing document through OpenCV deskewing, CLAHE contrast enhancement & Sarvam AI Doc-AI..."):
            pipeline = LandDeedVerificationPipeline(output_dir=str(BASE_DIR / "output"))
            pipeline.run(str(target_path))
            st.success("Verification Pipeline Execution Completed!")

    with col2:
        if output_json.exists():
            with open(output_json, "r", encoding="utf-8") as f:
                res = json.load(f)

            summary = res.get("document_verification_summary", {})
            markers = res.get("visual_authenticity_markers", {})
            metadata = res.get("parsed_deed_metadata", {})
            shares = res.get("ownership_shares", [])

            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                status = summary.get("authenticity_status", "VERIFIED")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Authenticity Status</div>
                    <div class="metric-value" style="color: {'#16a34a' if status == 'VERIFIED' else '#dc2626'};">{status}</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                conf = summary.get("confidence_scores", {}).get("overall_authenticity", 1.0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Authenticity Score</div>
                    <div class="metric-value">{int(conf * 100)}%</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                stamps = len(markers.get("revenue_stamps", []))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Revenue Stamps</div>
                    <div class="metric-value" style="color: #10b981;">{stamps} Verified</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                sigs = len(markers.get("signatures", []))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Signatures</div>
                    <div class="metric-value" style="color: #3b82f6;">{sigs} Verified</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### 📌 Verification Notes")
            for note in summary.get("verification_notes", []):
                st.info(f"✓ {note}")
        else:
            st.info("Click 'Run Verification Pipeline' to analyze the document.")

    # Visual Inspection & Tabs
    if output_json.exists():
        st.markdown("---")
        t1, t2, t3, t4 = st.tabs(["🔍 Visual Verification Overlay", "📑 Parsed Deed Metadata", "👥 Tabular Ownership Shares", "💾 Raw JSON Data"])

        with t1:
            st.markdown("###### Bounding Box Legend: 🟢 **Green**: Official Revenue Stamps | 🔵 **Blue**: Cursive Signatures | 🟡 **Amber**: Kaifiyat Margin Remarks")
            img_c1, img_c2, img_c3 = st.columns(3)
            with img_c1:
                st.caption("**1. Visual Overlay with Authenticity Bounding Boxes**")
                if output_overlay.exists():
                    st.image(str(output_overlay), use_container_width=True)
            with img_c2:
                st.caption("**2. Deskewed & Contrast Enhanced (CLAHE)**")
                if enhanced_img.exists():
                    st.image(str(enhanced_img), use_container_width=True)
            with img_c3:
                st.caption("**3. Original Scanned Input**")
                if target_path.exists() and target_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    st.image(str(target_path), use_container_width=True)

        with t2:
            st.markdown("##### 🏛️ Extracted Revenue Jurisdiction & Parcel Details")
            jur = metadata.get("geographic_jurisdiction", {})
            parcel = metadata.get("land_parcel_details", {})
            area = parcel.get("plot_area", {})

            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.write(f"**Deed Type:** {metadata.get('deed_type', 'खतौनी')}")
                st.write(f"**Deed / Khatauni Number:** `{metadata.get('deed_number', 'N/A')}`")
                st.write(f"**Execution Date:** {metadata.get('execution_date', 'N/A')}")
                st.write(f"**State:** {jur.get('state', 'N/A')}")
                st.write(f"**District:** {jur.get('district', 'N/A')}")
                st.write(f"**Tehsil:** {jur.get('tehsil', 'N/A')}")
                st.write(f"**Village / Mauza:** {jur.get('village_mauza', 'N/A')}")

            with col_meta2:
                st.write(f"**Khata Number:** `{parcel.get('khata_number', 'N/A')}`")
                st.write(f"**Khasra Numbers:** `{', '.join(parcel.get('khasra_numbers', []))}`")
                st.write(f"**Stated Area:** `{area.get('stated_value', 'N/A')} {area.get('stated_unit', '')}`")
                st.write(f"**Standardized SI Area:** `{area.get('standardized_sq_meters', 0.0):,.2f} m²`")
                st.write(f"**Standardized Hectares:** `{area.get('standardized_hectares', 0.0):.4f} Ha`")
                st.write(f"**Standardized Imperial Area:** `{(area.get('standardized_sq_meters', 0.0) / SQ_M_PER_ACRE):.4f} Acres`")

        with t3:
            st.markdown("##### 👥 Co-Sharers (Hissedari Distribution)")
            if shares:
                share_rows = []
                for s in shares:
                    share_rows.append({
                        "Holder Name": s.get("holder_name"),
                        "Parentage / Relation": s.get("relation_name"),
                        "Share Fraction": s.get("share_fraction"),
                        "Share %": f"{s.get('share_percentage', 0.0):.2f}%",
                        "Allocated Area": s.get("allocated_area"),
                        "Tenure Status": s.get("status")
                    })
                st.dataframe(share_rows, use_container_width=True)
            else:
                st.write("No co-sharers parsed.")

        with t4:
            st.json(res)
            st.download_button(
                "⬇️ Download Structured Verification JSON",
                data=json.dumps(res, indent=2, ensure_ascii=False),
                file_name=f"{target_path.stem}_verification_result.json",
                mime="application/json"
            )


# =============================================================================
# MODULE 2: ORAL TESTIMONY & VANSHAVALI RECONSTRUCTION
# =============================================================================
elif module == "🎙️ 2. Oral Testimony & Vanshavali":
    st.subheader("🎙️ Step 2: Oral Testimony Parsing & Genealogical Vanshavali")
    st.write(
        "Transcribe spoken regional Indian dialects (Bhojpuri, Awadhi, Maithili, Hindi) "
        "and reconstruct the genealogical family tree (Vanshavali), customary succession steps, "
        "and disputed property grievances using **Sarvam Saaras & Sarvam-105B (Indus)**."
    )

    t_col1, t_col2 = st.columns([1, 1])
    with t_col1:
        st.markdown("#### Spoken Oral Testimony")
        sample_testimony = get_sample_regional_testimony()
        user_transcript = st.text_area(
            "Oral Testimony Transcript (Regional Dialect):",
            value=sample_testimony,
            height=260
        )

        parse_btn = st.button("🧬 Analyze & Reconstruct Vanshavali", type="primary", use_container_width=True)

    testimony_json_path = BASE_DIR / "normalized_oral_testimony.json"
    
    if parse_btn:
        with st.spinner("Extracting lineage entities, kinship relationships, and succession order via Sarvam AI..."):
            parser = OralTestimonyParser()
            normalized_obj = parser.process_oral_testimony(
                transcript_text=user_transcript,
                use_fallback_if_unauthorized=True
            )
            with open(testimony_json_path, "w", encoding="utf-8") as f:
                json.dump(normalized_obj.model_dump(), f, indent=2, ensure_ascii=False)
            st.success("Vanshavali Reconstruction Completed!")

    with t_col2:
        if testimony_json_path.exists():
            with open(testimony_json_path, "r", encoding="utf-8") as f:
                testimony_data = json.load(f)

            st.markdown("#### 📜 Claimant Statement Summary")
            st.info(testimony_data.get("summary_of_statement", "No summary available."))

            grievance = testimony_data.get("property_grievance", {})
            st.markdown("#### ⚖️ Property Grievance Summary")
            g_c1, g_c2 = st.columns(2)
            with g_c1:
                st.write(f"**Allegation:** `{grievance.get('allegation_category', 'N/A')}`")
                st.write(f"**Claimed Share:** `{grievance.get('claimed_share', 'N/A')}`")
                st.write(f"**Disputed Asset:** {grievance.get('disputed_asset_description', 'N/A')}")
            with g_c2:
                st.write(f"**Location:** {grievance.get('location_details', 'N/A')}")
                st.write(f"**Adverse Party:** `{', '.join(grievance.get('adverse_party_ids', []))}`")
                st.write(f"**Relief Sought:** {grievance.get('relief_sought', 'N/A')}")

    # Reconstructed Vanshavali View
    if testimony_json_path.exists():
        st.markdown("---")
        v_tab1, v_tab2, v_tab3 = st.tabs(["🌳 Reconstructed Family Tree (Vanshavali)", "⏳ Chronological Devolution Steps", "💾 Normalized JSON"])

        with v_tab1:
            st.markdown("##### 🌳 Ancestral Lineage & Kinship Hierarchy")
            vanshavali = testimony_data.get("vanshavali", {})
            members = vanshavali.get("members", [])
            members_by_gen = {}
            for m in members:
                gen = m.get("generation_level", 0)
                members_by_gen.setdefault(gen, []).append(m)

            for gen_idx in sorted(members_by_gen.keys()):
                gen_name = "Ancestral Head (Patriarch)" if gen_idx == 0 else f"Generation {gen_idx}"
                st.markdown(f"**{gen_name}**")
                cols = st.columns(len(members_by_gen[gen_idx]))
                for idx, m in enumerate(members_by_gen[gen_idx]):
                    with cols[idx]:
                        is_c = m.get("is_claimant", False)
                        is_h = m.get("is_ancestral_head", False)
                        border_color = "#f59e0b" if is_c else ("#4f46e5" if is_h else "#94a3b8")
                        badge_text = "⭐ ACTIVE CLAIMANT" if is_c else ("👑 ANCESTRAL HEAD" if is_h else m.get("status", "").upper())
                        st.markdown(f"""
                        <div style="background: #ffffff; border: 2px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: {border_color};">{badge_text}</div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b; margin: 4px 0;">{m.get('name')} ({m.get('person_id')})</div>
                            <div style="font-size: 0.85rem; color: #64748b;">Status: {m.get('status')} | {m.get('date_marker', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

        with v_tab2:
            st.markdown("##### ⏳ Stated Devolution Steps & Historical Timeline")
            steps = testimony_data.get("stated_succession_order", [])
            for s in steps:
                contested = s.get("contested", False)
                status_color = "#dc2626" if contested else "#16a34a"
                status_text = "⚠️ CONTESTED / DISPUTED" if contested else "✅ UNCONTESTED"
                st.markdown(f"""
                <div class="tree-node" style="border-left-color: {status_color};">
                    <span style="color: {status_color}; font-weight: 700;">{status_text}</span> — <b>Step {s.get('step_order')}: {s.get('approximate_year_or_era')}</b><br>
                    <b>From:</b> {s.get('from_person_id')} ➔ <b>To:</b> {', '.join(s.get('to_person_ids', []))}<br>
                    <b>Basis:</b> {s.get('basis_of_succession')}
                </div>
                """, unsafe_allow_html=True)

        with v_tab3:
            st.json(testimony_data)
            st.download_button(
                "⬇️ Download Reconstructed Vanshavali JSON",
                data=json.dumps(testimony_data, indent=2, ensure_ascii=False),
                file_name="normalized_oral_testimony.json",
                mime="application/json"
            )


# =============================================================================
# MODULE 3: AREA UNIT NORMALIZATION & MATHEMATICAL CONSERVATION AUDIT
# =============================================================================
elif module == "📐 3. Area Normalization & Audit":
    st.subheader("📐 Step 3: Indic Area Normalization & Conservation Audit")
    st.write(
        "Standardize localized Indic area measurements (Bigha, Biswa, Kanal, Marla, Guntha, Are, Anna-Pai) "
        "and perform strict mathematical conservation audits to detect **Surplus Defects** (land created out of thin air) "
        "and **Deficit Defects** (unaccounted / omitted co-sharers)."
    )

    # Preset Scenarios
    st.markdown("##### ⚡ Quick Benchmark Scenarios")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    
    preset = None
    with sc1:
        if st.button("Case 1: Punjab Jamabandi\n(Balanced)", use_container_width=True):
            preset = "case1"
    with sc2:
        if st.button("Case 2: UP Pucca Bigha\n(Surplus Anomaly)", use_container_width=True):
            preset = "case2"
    with sc3:
        if st.button("Case 3: Maharashtra 7/12\n(Deficit Anomaly)", use_container_width=True):
            preset = "case3"
    with sc4:
        if st.button("Case 4: Rajasthan Anna-Pai\n(Conserved)", use_container_width=True):
            preset = "case4"
    with sc5:
        if st.button("Case 5: Mishra Estate\n(Disputed Mutation)", use_container_width=True):
            preset = "case5"

    st.markdown("---")
    c_cfg1, c_cfg2, c_cfg3 = st.columns(3)

    # Defaults
    def_state = "Uttar Pradesh"
    def_district = "Meerut"
    def_tehsil = "Mawana"
    def_plot_id = "Khata 112 / Khasra 142 & 143"
    def_total_area = "12 Bigha 0 Biswa"
    def_co_sharers = "Kamlesh Mishra (Impugned Allocation): 10 Bigha\nHeirs of Bholanath Mishra (Leftover): 2 Bigha"

    if preset == "case1":
        def_state = "Punjab"
        def_district = "Jalandhar"
        def_tehsil = "Nakodar"
        def_plot_id = "Khasra 14//5 (Khewat 42)"
        def_total_area = "8 Kanal 0 Marla"
        def_co_sharers = "Baldev Singh s/o Harbhajan Singh: 1/2\nGurpreet Kaur w/o Jagtar Singh: 1/4\nHarinder Singh s/o Jagtar Singh: 1/8\nManpreet Singh s/o Jagtar Singh: 1/8"
    elif preset == "case2":
        def_state = "Uttar Pradesh"
        def_district = "Meerut"
        def_tehsil = "Mawana"
        def_plot_id = "Khata 112 / Khasra 248"
        def_total_area = "2 Bigha 10 Biswa"
        def_co_sharers = "Ram Swaroop s/o Mangal Singh: 1 Bigha\nShyam Lal s/o Mangal Singh: 1 Bigha\nMohan Lal s/o Mangal Singh: 1 Bigha"
    elif preset == "case3":
        def_state = "Maharashtra"
        def_district = "Pune"
        def_tehsil = "Haveli"
        def_plot_id = "Gat No. 89"
        def_total_area = "1 Ha 20 R"
        def_co_sharers = "Dnyaneshwar Vitthal Patil: 40/120\nTukaram Vitthal Patil: 50/120"
    elif preset == "case4":
        def_state = "Rajasthan"
        def_district = "Jaipur"
        def_tehsil = "Sanganer"
        def_plot_id = "Khasra 502/1"
        def_total_area = "5 Bigha"
        def_co_sharers = "Girdhari Lal Sharma: 8 Annas\nBrijesh Sharma: 4 Annas\nRadha Raman Sharma: 4 Annas"
    elif preset == "case5":
        def_state = "Uttar Pradesh"
        def_district = "Meerut"
        def_tehsil = "Mawana"
        def_plot_id = "Mauza Chak-Govindpur (Estate of Late Rameshwar Mishra)"
        def_total_area = "12 Bigha"
        def_co_sharers = "Kamlesh Mishra (Adverse Party claimed holding): 10 Bigha\nHarishankar Mishra (Claimant asserted rightful share): 2 Bigha\nUmashankar Mishra (Brother share): 2 Bigha\nRavishankar Mishra (Brother share): 2 Bigha"

    with c_cfg1:
        state_in = st.selectbox(
            "State:",
            ["Uttar Pradesh", "Punjab", "Maharashtra", "Rajasthan", "Haryana", "Gujarat"],
            index=["Uttar Pradesh", "Punjab", "Maharashtra", "Rajasthan", "Haryana", "Gujarat"].index(def_state)
        )
    with c_cfg2:
        district_in = st.text_input("District:", value=def_district)
    with c_cfg3:
        tehsil_in = st.text_input("Tehsil / Taluka:", value=def_tehsil)

    # Standard formula card
    std_info = resolve_regional_standard(state=state_in, district=district_in, tehsil=tehsil_in)
    st.info(f"📍 **Applied Standard:** {std_info['name']} | **Formula:** {std_info['description']}")

    # Inputs for Plot & Co-sharers
    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        plot_id_in = st.text_input("Plot / Khasra Identifier:", value=def_plot_id)
        total_area_in = st.text_input("Registered Total Plot Area:", value=def_total_area)
        run_audit_btn = st.button("🔍 Execute Arithmetic Audit", type="primary", use_container_width=True)

    with p_col2:
        st.caption("Enter Co-Sharers (One per line formatted as: `Name: Share/Area`)")
        co_sharers_raw = st.text_area(
            "Co-Sharers List:",
            value=def_co_sharers,
            height=125
        )

    # Parse Co-sharers
    co_sharers_list = []
    for line in co_sharers_raw.strip().split("\n"):
        if ":" in line:
            parts = line.split(":", 1)
            co_sharers_list.append({"name": parts[0].strip(), "share": parts[1].strip()})
        elif line.strip():
            co_sharers_list.append({"name": line.strip(), "share": "1/2"})

    if run_audit_btn or preset is not None:
        validator = ArithmeticValidator(state=state_in, district=district_in, tehsil=tehsil_in)
        audit_res: PlotAuditResult = validator.audit_plot(
            plot_id=plot_id_in,
            total_plot_area=total_area_in,
            co_sharers_data=co_sharers_list
        )

        st.markdown("---")
        st.markdown("### 📊 Forensic Audit Results")

        # Metric Badges
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            status_cls = "status-conserved" if audit_res.status == "CONSERVED" else ("status-surplus" if audit_res.status == "SURPLUS_ALERT" else "status-deficit")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Audit Status</div>
                <div class="status-badge {status_cls}" style="margin-top: 6px;">{audit_res.status}</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Registered Plot Area</div>
                <div class="metric-value">{audit_res.total_area_sq_m:,.2f} m²</div>
                <div style="font-size: 0.8rem; color: #64748b;">({audit_res.total_area_acres:.4f} Acres)</div>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cumulative Co-Sharer Area</div>
                <div class="metric-value">{audit_res.sum_co_sharer_area_sq_m:,.2f} m²</div>
                <div style="font-size: 0.8rem; color: #64748b;">(Allocated: {audit_res.sum_shares_percentage:.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        with r4:
            delta_color = "#16a34a" if audit_res.area_delta_sq_m == 0 else "#dc2626"
            sign = "+" if audit_res.area_delta_sq_m > 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Area Variance / Delta</div>
                <div class="metric-value" style="color: {delta_color};">{sign}{audit_res.area_delta_sq_m:,.2f} m²</div>
                <div style="font-size: 0.8rem; color: {delta_color};">({sign}{audit_res.area_delta_acres:.4f} Acres)</div>
            </div>
            """, unsafe_allow_html=True)

        # Detailed Breakdown Table
        st.markdown("##### 👥 Co-Sharer Allocated Distribution")
        table_rows = []
        for s in audit_res.co_sharers:
            table_rows.append({
                "Co-Sharer Name": s.name,
                "Stated Share": s.raw_share,
                "Fraction": str(s.parsed_fraction),
                "Share %": f"{s.percentage:.3f}%",
                "Allocated Area (m²)": f"{s.computed_sq_m:,.2f}",
                "Allocated Area (Acres)": f"{s.computed_acres:.4f}",
                "Variance / Note": f"{s.variance_sq_m:+.2f} m²" if s.variance_sq_m else "-"
            })
        st.dataframe(table_rows, use_container_width=True)

        st.markdown("##### ⚖️ Forensic Revenue Findings & Conclusion")
        st.warning(f"**Conclusion:** {audit_res.summary_verdict}")
        for obs in audit_res.observations:
            st.markdown(f"- {obs}")

        # Download Report
        report_md = audit_res.generate_markdown_report()
        st.download_button(
            "⬇️ Download Forensic Arithmetic Audit Report (Markdown)",
            data=report_md,
            file_name=f"audit_report_{plot_id_in.replace(' ', '_')}.md",
            mime="text/markdown"
        )


# =============================================================================
# MODULE 4: TITLE DISCREPANCY MATRIX (SARVAM-105B ENGINE)
# =============================================================================
elif module == "🔍 4. Title Discrepancy Matrix":
    st.subheader("🔍 Step 4: Discrepancy & Forensic Title Audit Matrix")
    st.write(
        "Cross-examine official land records against oral testimony Vanshavali and "
        "statutory Hindu Succession rules (HSA 1956 / 2005) to detect legal defects: "
        "**Omitted Class-I legal heirs**, **Minority alienations**, and **Area conveyance in excess of title**."
    )

    matrix_json_path = BASE_DIR / "title_audit_matrix_report.json"
    matrix_md_path = BASE_DIR / "title_audit_matrix_report.md"

    if matrix_json_path.exists():
        with open(matrix_json_path, "r", encoding="utf-8") as f:
            m_data = json.load(f)

        # Top Executive Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Audit Identifier</div>
                <div class="metric-value" style="font-size: 1.1rem;">{m_data.get('audit_id')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Identified Claimant</div>
                <div class="metric-value" style="font-size: 1.2rem; color: #4f46e5;">{m_data.get('claimant_name')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Statutory Entitlement</div>
                <div class="metric-value" style="color: #16a34a;">{m_data.get('claimant_theoretical_share')}</div>
                <div style="font-size: 0.8rem; color: #dc2626;">Recorded: {m_data.get('claimant_recorded_share')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Deprived Land Area</div>
                <div class="metric-value" style="color: #dc2626;">{m_data.get('claimant_deprived_area_acres', 0.0):.4f} ac</div>
                <div style="font-size: 0.8rem; color: #64748b;">({m_data.get('claimant_deprived_area_sq_m', 0.0):,.2f} m²)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⚠️ Flagged Legal Irregularities & Defect Line Items")
        discrepancies = m_data.get("discrepancies", [])
        
        for d in discrepancies:
            sev = d.get("severity", "MEDIUM")
            sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else "#ca8a04")
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {sev_color}; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="background: {sev_color}20; color: {sev_color}; font-weight: 700; padding: 3px 10px; border-radius: 9999px; font-size: 0.8rem;">{sev} SEVERITY</span>
                    <span style="font-family: monospace; font-size: 0.85rem; color: #64748b;">Defect ID: {d.get('item_id')} | Category: {d.get('category')}</span>
                </div>
                <h4 style="margin: 8px 0 4px 0; color: #1e293b;">{d.get('title')}</h4>
                <p style="color: #475569; font-size: 0.95rem; margin-bottom: 8px;">{d.get('description')}</p>
                <div style="font-size: 0.85rem; color: #1e1b4b; background: #e0e7ff; padding: 6px 10px; border-radius: 4px;">
                    📜 <b>Statutory Citation:</b> {d.get('statutory_provision', 'N/A')}
                </div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">
                    🎯 <b>Recommended Action:</b> {d.get('action_recommended', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Statutory Heir Table
        st.markdown("##### 👥 Statutory Heir Succession Distribution (Hindu Succession Act)")
        heirs = m_data.get("statutory_heir_shares", [])
        heir_rows = []
        for h in heirs:
            heir_rows.append({
                "Person ID": h.get("person_id"),
                "Name": h.get("name"),
                "Relationship": h.get("relationship_to_deceased"),
                "Class": h.get("heir_class"),
                "Statutory Share": h.get("statutory_fraction_str"),
                "Theoretical Area (Acres)": f"{h.get('theoretical_area_acres', 0.0):.4f}",
                "Recorded Share": h.get("recorded_share_fraction_str") or "0",
                "Status": h.get("status")
            })
        st.dataframe(heir_rows, use_container_width=True)

        # Download Actions
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "⬇️ Download Discrepancy Matrix (JSON)",
                data=json.dumps(m_data, indent=2),
                file_name="title_audit_matrix_report.json",
                mime="application/json",
                use_container_width=True
            )
        with col_d2:
            if matrix_md_path.exists():
                with open(matrix_md_path, "r", encoding="utf-8") as f:
                    md_text = f.read()
                st.download_button(
                    "⬇️ Download Discrepancy Report (Markdown)",
                    data=md_text,
                    file_name="title_audit_matrix_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        st.info("Execute Step 4 pipeline to generate Title Discrepancy Matrix.")


# =============================================================================
# MODULE 5: BILINGUAL DELIVERABLES & COURT PETITION PDF
# =============================================================================
elif module == "⚖️ 5. Legal Brief & Court Petition":
    st.subheader("⚖️ Step 5: Bilingual Deliverables & Court-Ready Legal Objection Petition")
    st.write(
        "Synthesize technical and legal findings into an **empathetic native audio briefing (Sarvam Bulbul)** "
        "and a **Court-Ready Legal Objection Petition PDF** formatted under Section 34/35 of the State Land Revenue Act "
        "before the Learned Tehsildar / Sub-Divisional Officer (SDO)."
    )

    deliv_dir = BASE_DIR / "deliverables"
    audio_file = deliv_dir / "landholder_audio_briefing.wav"
    pdf_file = deliv_dir / "Court_Ready_Legal_Objection_Petition.pdf"
    hi_transcript = deliv_dir / "audio_briefing_transcript_hindi.txt"
    en_transcript = deliv_dir / "audio_briefing_transcript_english.txt"
    indus_prompts = deliv_dir / "indus_sarvam_prompts.md"

    # Action to Regenerate Deliverables
    if st.button("🔄 Regenerate Bilingual Deliverables & Court PDF", type="secondary"):
        with st.spinner("Generating Bulbul Audio Briefing & Compiling Court Petition PDF..."):
            run_deliverables_pipeline()
            st.success("Deliverables Successfully Updated!")

    st.markdown("---")
    
    # 1. AUDIO BRIEFING SECTION
    st.markdown("### 🎙️ 1. Conversational Audio Briefing (Sarvam AI Bulbul)")
    st.write(
        "A 30-second conversational summary delivered in the landholder's native tongue "
        "explaining their lawful entitlement, the exact 4-Bigha diverted deficit, and the court remedy."
    )

    if audio_file.exists():
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/wav")
    else:
        st.warning("Audio file not found. Click 'Regenerate Deliverables' above.")

    # Side-by-Side Transcripts
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("##### 🇮🇳 Spoken Audio Transcript (Hindi / Purvanchal)")
        if hi_transcript.exists():
            with open(hi_transcript, "r", encoding="utf-8") as f:
                st.text_area("Hindi Audio Brief:", value=f.read(), height=220, disabled=True)
    with t_c2:
        st.markdown("##### 🌐 Translated Transcript (English)")
        if en_transcript.exists():
            with open(en_transcript, "r", encoding="utf-8") as f:
                st.text_area("English Translation:", value=f.read(), height=220, disabled=True)

    st.markdown("---")

    # 2. COURT PETITION PDF & PREVIEW
    st.markdown("### 📜 2. Court-Ready Legal Objection Petition (Section 34 & 35)")
    st.write(
        "Standardized legal objection petition drafted for filing before the Revenue Court "
        "of the Learned Tehsildar / Sub-Divisional Officer (SDO), Mawana, District Meerut."
    )

    pdf_c1, pdf_c2 = st.columns([2, 1])
    with pdf_c1:
        st.markdown("""
        **Statutory Framework:**
        - Objection under Sections 34 & 35 of the Uttar Pradesh Revenue Code, 2006.
        - Certified under Hindu Succession Act, 1956 (Section 6 & 8 Coparcenary Devolution).
        - Grounded in 1988 Consolidation Settlement (Chakbandi Batwara) records.
        """)

        st.markdown("##### 📁 Attached Court Evidence Annexures:")
        st.markdown("""
        - **Annexure P-1:** Reconstructed Genealogical Family Tree (Vanshavali)
        - **Annexure P-2:** Consolidation Settlement Extract (Chakbandi 1988)
        - **Annexure P-3:** Forensic Area Discrepancy & Mathematical Conservation Audit Matrix
        - **Annexure P-4:** Certified Spoken Testimony Transcript (Saaras:v4 Verbatim)
        """)

    with pdf_c2:
        if pdf_file.exists():
            pdf_bytes = get_file_download_bytes(pdf_file)
            st.markdown("#### 📥 Court Filing PDF")
            st.download_button(
                "⬇️ Download Ready-to-Sign Court Petition (PDF)",
                data=pdf_bytes,
                file_name="Court_Ready_Legal_Objection_Petition.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.caption(f"File Size: {len(pdf_bytes):,} bytes | Format: A4 Standard Legal Court Paper")
        else:
            st.warning("Petition PDF not yet compiled.")

    st.markdown("---")

    # 3. INDUS COMPANION PROMPTS
    st.markdown("### 🇮🇳 3. Sarvam AI Indus Companion Integration")
    st.caption("Copy-paste ready prompts for interactive legal assistance on https://indus.sarvam.ai/")
    if indus_prompts.exists():
        with open(indus_prompts, "r", encoding="utf-8") as f:
            st.code(f.read(), language="markdown")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 12px 0;">
    भूमि-प्रमाण Indic Land Records Intelligence Platform • Built with Sarvam AI Sovereign Models<br>
    Document Vision • Saaras STT • Sarvam-105B Reasoning • Bulbul Acoustic Speech
</div>
""", unsafe_allow_html=True)
