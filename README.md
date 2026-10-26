# 🇮🇳 Sarvam Bhoomi Praman (सर्वम भूमि प्रमाण)
### Indic Land Records Intelligence & Legal Title Audit Platform
**Built with Sarvam AI Document Intelligence (`sarvam-vision` / Doc-AI, `sarvam-105b`, `bulbul`, `saaras`)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sarvam-bhoomi-praman.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/PritamWayne/Sarvam-Hackathon)

> 🌐 **Live Web Application**: [https://sarvam-bhoomi-praman.streamlit.app/](https://sarvam-bhoomi-praman.streamlit.app/)

An end-to-end sovereign Indian AI platform to extract raw text, tabular ownership data, visual authenticity markers from scanned Indian land deeds (Khatauni, Khasra, Jamabandi, Sale Deeds / बैनामा, Patta), resolve regional measurement units, cross-validate oral testimonies and genealogy against Hindu Succession Act (HSA 1956/2005) & UP-ZALR/Revenue Codes, and generate court-ready legal objection petitions and audio briefings.

---

## 🎯 Features & Architecture

```
                       Scanned Land Deed (Image / PDF)
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │  Step 1: Document Pre-processing (OpenCV / Pillow)     │
        │  • Deskewing: Hough Line & MinAreaRect rotation        │
        │  • Contrast Enhancement: LAB Color Space + CLAHE       │
        │  • Margin Isolation: Isolates Kaifiyat column          │
        └────────────────────────────┬───────────────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│ Step 2: Visual Authenticity       │ │ Step 3: Layout & Text Extraction  │
│ Detection                         │ │ (Sarvam Vision / Pages Doc-AI)    │
│ • Official Revenue Seals / Stamps │ │ • Live Schema-based extraction    │
│   (Violet/Red/Blue ink, circles)  │ │ • Khasra / Khata numbers          │
│ • Tehsildar & Patwari Signatures  │ │ • Village, Tehsil, District       │
│ • Marginal Remarks (Kaifiyat)     │ │ • Tabular Ownership & Shares      │
│ • Verification Flags & Scores     │ │ • Stated Plot Area & Unit Normalization
└─────────────────┬─────────────────┘ └─────────────────┬─────────────────┘
                  │                                     │
                  └──────────────────┬──────────────────┘
                                     ▼
                     Structured Verification JSON
```

---

## 🚀 Quickstart

### 1. Requirements
Ensure Python 3.10+ is installed with required packages:
```bash
pip install sarvamai opencv-python pillow pypdfium2 pydantic python-dotenv pytest
```

### 2. Configure API Key
Add your Sarvam AI API key into `.env`:
```ini
SARVAM_API_KEY=sk_...
```
*(Get your key from [indus.sarvam.ai](https://indus.sarvam.ai/))*

### 3. Run the Verification Pipeline
```bash
# Execute end-to-end on sample or your own scanned deed
python main.py

# Or specify a custom input document
python pipeline.py --input path/to/land_deed.pdf --output result.json
```

### 4. Interactive Web Application & Dashboard

- **🌐 Live Hosted Cloud Version**: [https://sarvam-bhoomi-praman.streamlit.app/](https://sarvam-bhoomi-praman.streamlit.app/)

- **Local Streamlit Application**:
  ```bash
  streamlit run app.py
  ```

- **Local Fast View Dashboard**:
  ```bash
  python web_dashboard.py
  ```
  Open **[http://127.0.0.1:8080](http://127.0.0.1:8080)** in your browser to inspect:
  - Side-by-side original vs deskewed/enhanced scans
  - Visual bounding boxes for stamps (green), signatures (blue), and Kaifiyat (amber)
  - Parsed tabular ownership table and full JSON viewer.

---

## 📋 Expected Output Format

The output strictly complies with the Pydantic schema in [`models/deed_schema.py`](models/deed_schema.py):

```json
{
  "document_verification_summary": {
    "document_name": "sample_land_deed.png",
    "document_type": "खतौनी",
    "processed_at": "2026-10-26T16:55:15.549931+00:00",
    "authenticity_status": "VERIFIED",
    "mandatory_stamps_present": true,
    "signatures_present": true,
    "kaifiyat_present": true,
    "confidence_scores": {
      "stamps_confidence": 0.88,
      "signatures_confidence": 0.95,
      "overall_authenticity": 1.0
    },
    "verification_notes": [
      "Official revenue seals validated with characteristic violet/red stamp ink profile.",
      "Tehsildar and Patwari cursive attestation signatures verified in signing zone.",
      "Kaifiyat (Marginal Remarks) column contains recorded mutation/court remarks."
    ]
  },
  "visual_authenticity_markers": {
    "mandatory_stamps_present": true,
    "signatures_present": true,
    "kaifiyat_present": true,
    "authenticity_status": "VERIFIED",
    "authenticity_score": 1.0,
    "revenue_stamps": [ ... ],
    "signatures": [ ... ],
    "marginal_remarks": [ ... ]
  },
  "parsed_deed_metadata": {
    "deed_type": "खतौनी",
    "deed_number": "UP-REV/2024/99201",
    "execution_date": "15/10/2024",
    "geographic_jurisdiction": {
      "state": "उत्तर प्रदेश",
      "district": "मेरठ",
      "tehsil": "मवाना",
      "village_mauza": "खासपुर"
    },
    "land_parcel_details": {
      "khasra_numbers": ["154/1, 154/2", "156"],
      "khata_number": "00184",
      "plot_area": {
        "stated_value": 3.75,
        "stated_unit": "बीघा",
        "standardized_sq_meters": 9484.8,
        "standardized_hectares": 0.9485
      }
    }
  },
  "ownership_shares": [
    {
      "holder_name": "Suresh Kumar",
      "relation_name": "स्व० रामस्वरूप",
      "share_fraction": "1/2",
      "share_percentage": 50.0,
      "allocated_area": "1.875 बीघा",
      "status": "Sankramaniya Bhumidhar (संक्रमणीय भूमिधर)"
    },
    {
      "holder_name": "Mahesh Kumar",
      "relation_name": "स्व० रामस्वरूप",
      "share_fraction": "1/2",
      "share_percentage": 50.0,
      "allocated_area": "1.875 बीघा",
      "status": "Sankramaniya Bhumidhar (संक्रमणीय भूमिधर)"
    }
  ]
}
```

---

## 🧪 Automated Testing
Run the test suite with:
```bash
python -m pytest tests/test_pipeline.py -v
```
All tests verify pre-processing deskew, stamp & signature detection, unit conversion, and schema validation.
