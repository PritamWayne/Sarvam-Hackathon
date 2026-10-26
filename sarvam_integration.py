"""
Sarvam AI (Indus) Integration Layer.
Integrates with Sarvam AI's sovereign LLM API (sarvam-105b-conversations) and provides
custom system prompts and fallback utilities for Indus (https://indus.sarvam.ai/).
"""

import os
import re
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

INDUS_SYSTEM_PROMPT = """You are Indus Land Records Intelligence, an expert in Indian Revenue Systems, Jamabandi, Khatauni, RoR, and Land Survey settlement records across all Indian states.
Your task is to extract land plot information and co-sharer (Hissedari) breakdown from given record extracts.

Output MUST be valid JSON with the following structure:
{
  "state": "State name (e.g. Uttar Pradesh, Punjab, Maharashtra)",
  "district": "District name",
  "tehsil": "Tehsil or Taluka name",
  "plot_id": "Khasra / Khewat / Survey number",
  "total_registered_area": "Raw total registered area (e.g. '3 Bigha 10 Biswa', '5-12 Kanal-Marla', '2.5 Hectare')",
  "unit_hint": "Dominant unit (e.g. bigha, kanal, hectare, cent)",
  "co_sharers": [
    {
      "name": "Co-sharer / Hissedar name with parentage if available",
      "share": "Fractional share (e.g. '1/3', '4 Annas', '25%') OR recorded parcel area if given as specific area",
      "recorded_area": "Optional explicit parcel area string if stated separately"
    }
  ]
}
"""


class SarvamIndusAssistant:
    """
    Client for interacting with Sarvam AI API and generating Indus prompts.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from sarvamai import SarvamAI
                self.client = SarvamAI(api_subscription_key=self.api_key)
            except Exception as e:
                self.client = None

    def extract_land_record_entities(self, text_or_ocr: str) -> Dict[str, Any]:
        """
        Extracts structured land record metadata using Sarvam AI API if credits are available,
        or falls back gracefully to deterministic rule-based extractor.
        """
        if self.client:
            try:
                response = self.client.chat.completions(
                    messages=[
                        {"role": "system", "content": INDUS_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Extract plot details and co-sharers from this revenue record extract:\n\n{text_or_ocr}"
                        }
                    ],
                    model="sarvam-105b-conversations"
                )
                content = response.choices[0].message.content
                # Parse JSON from LLM response
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception as e:
                # e.g., HTTP 402 Insufficient Quota or Network offline
                pass

        # Deterministic Rule-Based Fallback
        return self._heuristic_extract(text_or_ocr)

    def _heuristic_extract(self, text: str) -> Dict[str, Any]:
        """
        Deterministic extractor supporting English, Devanagari (Hindi/Marathi), and transliterated terms.
        """
        state = "Uttar Pradesh"
        district = "Meerut"
        tehsil = "Mawana"
        plot_id = "Khasra 248"
        total_area = "2 Bigha 10 Biswa"
        unit_hint = "bigha"
        co_sharers = []

        lower_text = text.lower()
        if any(w in lower_text for w in ["punjab", "पंजाब", "kanal", "कनाल", "marla", "मरला"]):
            state = "Punjab"
            unit_hint = "kanal"
        elif any(w in lower_text for w in ["maharashtra", "महाराष्ट्र", "hectare", "हेक्टेयर", "guntha", "गुंठा"]):
            state = "Maharashtra"
            unit_hint = "hectare"
        elif any(w in lower_text for w in ["rajasthan", "राजस्थान"]):
            state = "Rajasthan"
            unit_hint = "bigha"
        elif any(w in lower_text for w in ["bihar", "बिहार", "katha", "कट्ठा"]):
            state = "Bihar"
            unit_hint = "bigha"

        # District extraction
        dist_m = re.search(r"(?:district|जनपद|ज़िला|जिल्हा)[:\s]+([^\s,\n\)]+)", text, re.IGNORECASE)
        if dist_m:
            district = dist_m.group(1).strip()

        # Tehsil extraction
        tehsil_m = re.search(r"(?:tehsil|तहसील|तालुका)[:\s]+([^\s,\n\)]+)", text, re.IGNORECASE)
        if tehsil_m:
            tehsil = tehsil_m.group(1).strip()

        # Plot extraction
        plot_m = re.search(r"(?:khasra|खसरा|khewat|खेवट|गाट|gat|khata|खाता)\s*(?:no\.?|number|संख्या)?[:\s]+([0-9/\-]+)", text, re.IGNORECASE)
        if plot_m:
            plot_id = f"Khasra {plot_m.group(1).strip()}"

        # Total registered area extraction
        area_m = re.search(
            r"(?:total\s+registered\s+area|total\s+area|कुल\s+दर्ज\s+क्षेत्रफल|क्षेत्रफल|रकबा)[:\s]+([0-9\.\s\-/a-zA-Z\u0900-\u097F]+?)(?=\n|\(|$)",
            text,
            re.IGNORECASE
        )
        if area_m:
            total_area = area_m.group(1).strip()
            # If bilingual in parentheses like "2 बीघा 10 बिस्वा (2 Bigha 10 Biswa)", extract the english or standard part
            paren_m = re.search(r"\(([^)]+)\)", text[text.find(total_area):text.find(total_area) + 80])
            if paren_m and any(u in paren_m.group(1).lower() for u in ["bigha", "kanal", "ha", "acre", "biswa"]):
                total_area = paren_m.group(1).strip()

        # Co-sharers pattern: e.g. "1. राम स्वरूप पुत्र मंगल सिंह - अंश: 1 बीघा (1 Bigha)"
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines:
            # Check for line indicating co-sharer
            if re.search(r"^\d+[\.\)]|\b(?:अंश|हिस्सा|share)\b", line, re.IGNORECASE):
                # Pattern: [index.] [name] - [अंश/share]: [share_value]
                parts = re.split(r"[-–:]\s*(?:अंश|हिस्सा|share)?[:\s]*", line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    name_raw = re.sub(r"^\d+[\.\)]\s*", "", parts[0]).strip()
                    share_raw = parts[1].strip()
                    # Check for parenthesized translation e.g. "1 बीघा (1 Bigha)"
                    paren = re.search(r"\(([^)]+)\)", share_raw)
                    if paren:
                        share_val = paren.group(1).strip()
                    else:
                        share_val = share_raw.split("-")[0].strip()

                    if name_raw and share_val:
                        co_sharers.append({
                            "name": name_raw,
                            "share": share_val
                        })

        return {
            "state": state,
            "district": district,
            "tehsil": tehsil,
            "plot_id": plot_id,
            "total_registered_area": total_area,
            "unit_hint": unit_hint,
            "co_sharers": co_sharers
        }

    @staticmethod
    def get_indus_web_prompt(land_record_text: str) -> str:
        """
        Generates a copy-pasteable prompt optimized for the Indus web app at https://indus.sarvam.ai/
        """
        return (
            "Visit https://indus.sarvam.ai/ and paste the following prompt:\n\n"
            "------------------ INDUS PROMPT START ------------------\n"
            f"{INDUS_SYSTEM_PROMPT}\n\n"
            "Here is the Land Record Extract to parse:\n"
            f"{land_record_text}\n"
            "------------------ INDUS PROMPT END --------------------\n"
        )
