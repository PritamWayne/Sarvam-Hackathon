"""
Area Unit Normalization Engine for Indian Land Records.
Converts localized, compound revenue units (Bigha-Biswa, Kanal-Marla, Guntha, Acre, etc.)
and fractional co-sharing holdings (Hissedari) into exact SI Square Meters (m^2).
"""

import re
from fractions import Fraction
from typing import Dict, Any, Tuple, Optional, Union
from regional_standards import resolve_regional_standard, REGIONAL_STANDARDS, SQ_M_PER_ACRE, SQ_M_PER_HECTARE


class AreaNormalizer:
    """
    Normalizes localized land areas and co-sharer fractional shares (Hissedari)
    to standardized square meters (m^2) and exact rational fractions.
    """

    def __init__(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        tehsil: Optional[str] = None,
        preferred_standard: Optional[str] = None
    ):
        self.state = state
        self.district = district
        self.tehsil = tehsil
        self.standard = resolve_regional_standard(state, district, tehsil, preferred_standard)

    def normalize_area_to_sq_meters(
        self,
        area_input: Union[str, float, int, Dict[str, float]],
        unit_hint: Optional[str] = None
    ) -> float:
        """
        Converts any localized area expression into standard Square Meters (m^2).
        Handles:
          - Numeric inputs with unit_hint (e.g. 5.5, "bigha")
          - Compound strings: "2 Bigha 15 Biswa 10 Biswansi", "4 Kanal 12 Marla", "1 Ha 25 R"
          - Explicit units: "1000 sq ft", "500 gaj", "2.5 acre", "3.2 hectare"
          - Structured dict: {"bigha": 2, "biswa": 10}
        """
        if isinstance(area_input, (int, float)):
            unit = (unit_hint or "sq_meter").strip().lower()
            return self._convert_single_unit(float(area_input), unit)

        if isinstance(area_input, dict):
            total_sq_m = 0.0
            for u, val in area_input.items():
                total_sq_m += self._convert_single_unit(float(val), u.lower())
            return total_sq_m

        text = str(area_input).strip().lower()

        # Check pure number
        try:
            val = float(text)
            unit = (unit_hint or "sq_meter").strip().lower()
            return self._convert_single_unit(val, unit)
        except ValueError:
            pass

        # Parse compound string
        return self._parse_compound_area_string(text, unit_hint)

    def _convert_single_unit(self, value: float, unit: str) -> float:
        unit = unit.replace("-", "_").replace(" ", "_").strip()

        # Check active regional standard subunits
        subunits = self.standard.get("subunits", {})
        if unit in subunits and "sq_meters" in subunits[unit]:
            return value * subunits[unit]["sq_meters"]

        # Universal checks across all standards
        for std in REGIONAL_STANDARDS.values():
            s_units = std.get("subunits", {})
            if unit in s_units and "sq_meters" in s_units[unit]:
                return value * s_units[unit]["sq_meters"]

        # Metric & Imperial standard aliases
        aliases = {
            "sq_meter": 1.0,
            "sq_meters": 1.0,
            "sq_m": 1.0,
            "sqm": 1.0,
            "m2": 1.0,
            "meter": 1.0,
            "meters": 1.0,
            "are": 100.0,
            "ares": 100.0,
            "r": 100.0,
            "ha": SQ_M_PER_HECTARE,
            "hectare": SQ_M_PER_HECTARE,
            "hectares": SQ_M_PER_HECTARE,
            "acre": SQ_M_PER_ACRE,
            "acres": SQ_M_PER_ACRE,
            "sq_foot": 0.09290304,
            "sq_feet": 0.09290304,
            "sq_ft": 0.09290304,
            "sqft": 0.09290304,
            "sq_yard": 0.83612736,
            "sq_yards": 0.83612736,
            "sq_yd": 0.83612736,
            "sqyd": 0.83612736,
            "gaj": 0.83612736,
            "gaz": 0.83612736,
            "guntha": 101.17141056,
            "gunta": 101.17141056,
            "cent": 40.468564,
            "cents": 40.468564,
            "ground": 222.967296,
            "ankanam": 6.689019,
        }

        if unit in aliases:
            return value * aliases[unit]

        raise ValueError(
            f"Unrecognized land measurement unit '{unit}' under regional standard '{self.standard['name']}'."
        )

    def _parse_compound_area_string(self, text: str, fallback_unit: Optional[str] = None) -> float:
        """
        Parses multi-component strings like:
        '2 Bigha 10 Biswa 5 Biswansi', '4-12-2' (Kanal-Marla-Sarsahi), '1 Ha 20 R'
        """
        total_sq_m = 0.0
        found_tokens = False

        # Pattern: [number] [unit]
        # Supports Bigha, Biswa, Biswansi, Kanal, Marla, Sarsahi, Katha, Dhur, Guntha, Are, Ha, Acre, etc.
        token_pattern = re.compile(
            r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z_]+(?:\s+[a-zA-Z_]+)?)",
            re.IGNORECASE
        )

        matches = token_pattern.findall(text)
        if matches:
            for val_str, unit_str in matches:
                u_clean = unit_str.strip().lower().replace(" ", "_")
                val = float(val_str)
                try:
                    sq_m = self._convert_single_unit(val, u_clean)
                    total_sq_m += sq_m
                    found_tokens = True
                except ValueError:
                    # Ignore connective words like 'and', 'with', 'or'
                    pass

        if found_tokens:
            return total_sq_m

        # Check hyphen/colon separated notation common in revenue records:
        # e.g., Punjab Jamabandi "4-12" (4 Kanal 12 Marla) or "4-12-3" (4 Kanal 12 Marla 3 Sarsahi)
        # e.g., UP "2-10-5" (2 Bigha 10 Biswa 5 Biswansi)
        # e.g., Maharashtra 7/12 "1-25" (1 Hectare 25 Are)
        delimiters = ["-", ":", "/"]
        for d in delimiters:
            if d in text:
                parts = [p.strip() for p in text.split(d) if p.strip()]
                if all(self._is_number(p) for p in parts):
                    return self._convert_delimited_parts(parts)

        # Fallback to single numeric with fallback unit
        num_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
        if num_match:
            val = float(num_match.group(1))
            unit = fallback_unit or "sq_meter"
            return self._convert_single_unit(val, unit)

        raise ValueError(f"Could not parse area from string: '{text}'")

    def _convert_delimited_parts(self, parts: list) -> float:
        """Converts delimited numerical records (e.g. Kanal-Marla-Sarsahi or Bigha-Biswa-Biswansi)."""
        nums = [float(p) for p in parts]
        std_name = self.standard["name"]

        if "Punjab" in std_name or "Haryana" in std_name:
            # Format: Kanal - Marla [- Sarsahi]
            sq_m = nums[0] * self._convert_single_unit(1.0, "kanal")
            if len(nums) > 1:
                sq_m += nums[1] * self._convert_single_unit(1.0, "marla")
            if len(nums) > 2:
                sq_m += nums[2] * self._convert_single_unit(1.0, "sarsahi")
            return sq_m

        elif "Maharashtra" in std_name or "Gujarat" in std_name:
            # Format: Hectare - Are (Ha - R)
            sq_m = nums[0] * SQ_M_PER_HECTARE
            if len(nums) > 1:
                sq_m += nums[1] * 100.0  # 1 Are = 100 sq m
            return sq_m

        else:
            # Default Bigha - Biswa [- Biswansi]
            sq_m = nums[0] * self._convert_single_unit(1.0, "bigha")
            if len(nums) > 1:
                sq_m += nums[1] * self._convert_single_unit(1.0, "biswa")
            if len(nums) > 2:
                sq_m += nums[2] * self._convert_single_unit(1.0, "biswansi")
            return sq_m

    def parse_hissedari_fraction(
        self,
        share_expression: Union[str, float, int, Fraction],
        total_plot_sq_m: Optional[float] = None
    ) -> Fraction:
        """
        Parses fractional holdings (Hissedari / Khewat shares) into an exact Fraction.
        Supports:
          - Fractions: "1/3", "5/12", "7/24", "11/120"
          - Percentages: "25%", "33.333%"
          - Decimals: 0.25, "0.125"
          - Indian Rupee/Anna/Pai system:
              - "8 Annas" -> 8/16 = 1/2
              - "4 Anna 6 Pai" -> 4/16 + 6/(16*12) = 1/4 + 1/32 = 9/32
          - Biswa shares: "5 Biswa" out of 20 = 5/20 = 1/4
          - Explicit parcel areas: "1 Bigha", "2 Kanal 4 Marla" (if total_plot_sq_m provided or inferred)
        """
        if isinstance(share_expression, Fraction):
            return share_expression

        if isinstance(share_expression, int):
            # If 1, it represents 100% (sole owner)
            return Fraction(share_expression, 1)

        if isinstance(share_expression, float):
            return Fraction(str(share_expression)).limit_denominator(1000000)

        raw = str(share_expression).strip().lower()

        # Percentage
        if "%" in raw:
            cleaned = raw.replace("%", "").strip()
            return Fraction(cleaned) / 100

        # Anna / Pai revenue share notation (16 Annas = 1 Whole Rupee)
        if "anna" in raw or "aane" in raw or "pai" in raw:
            return self._parse_anna_pai_share(raw)

        # Standard fraction: a/b
        if "/" in raw and not any(u in raw for u in ["bigha", "kanal", "marla", "biswa", "ha", "are", "katha"]):
            parts = raw.split("/")
            if len(parts) == 2 and self._is_number(parts[0]) and self._is_number(parts[1]):
                num = int(float(parts[0].strip()))
                denom = int(float(parts[1].strip()))
                if denom == 0:
                    raise ZeroDivisionError("Fraction denominator cannot be zero.")
                return Fraction(num, denom)

        # Check if the share expression is actually an explicit area unit (e.g. "1 Bigha", "4 Kanal")
        known_units = [
            "bigha", "biswa", "biswansi", "kanal", "marla", "sarsahi", "katha", "dhur",
            "guntha", "gunta", "are", "hectare", "ha", "cent", "ground", "sq", "gaj"
        ]
        if any(u in raw for u in known_units):
            try:
                area_sq_m = self.normalize_area_to_sq_meters(raw)
                if total_plot_sq_m and total_plot_sq_m > 0:
                    ratio = area_sq_m / total_plot_sq_m
                    return Fraction(str(round(ratio, 8))).limit_denominator(1000000)
            except Exception:
                pass

        # Biswa share notation e.g. "5 biswa" out of standard 20 biswa
        if "biswa" in raw:
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*biswa", raw)
            if m:
                val = float(m.group(1))
                return (Fraction(str(val)) / 20).limit_denominator(1000)

        # Pure float string
        try:
            return Fraction(raw).limit_denominator(1000000)
        except Exception:
            raise ValueError(f"Unable to parse Hissedari share expression: '{share_expression}'")

    def _parse_anna_pai_share(self, text: str) -> Fraction:
        """
        Calculates share in traditional 1 Rupee = 16 Annas, 1 Anna = 12 Pais system.
        Total share is normalized to 1.0 (1 Rupee = 100%).
        """
        total_annas = Fraction(0, 1)

        anna_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*ann?a", text)
        if anna_match:
            total_annas += Fraction(anna_match.group(1))

        pai_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*pai", text)
        if pai_match:
            # 12 Pai = 1 Anna
            total_annas += Fraction(pai_match.group(1)) / 12

        # 16 Annas = 1 Whole Holding (1.0)
        return (total_annas / 16).limit_denominator(1000000)

    @staticmethod
    def _is_number(val: str) -> bool:
        try:
            float(val.strip())
            return True
        except ValueError:
            return False
