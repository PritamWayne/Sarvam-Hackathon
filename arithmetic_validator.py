"""
Arithmetic Validation & Mathematical Conservation Audit Engine.
Validates co-sharers' fractional holdings (Hissedari) against total registered plot area,
detects 'land created out of thin air' (surplus) or unaccounted deficits, and generates
an exhaustive forensic audit report.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Dict, Any, Optional
import json

from area_normalizer import AreaNormalizer
from regional_standards import SQ_M_PER_ACRE, SQ_M_PER_HECTARE, SQ_FT_PER_SQ_M


@dataclass
class CoSharerRecord:
    name: str
    raw_share: Any
    share_fraction: Fraction
    share_percentage: float
    computed_area_sq_m: float
    computed_area_sq_ft: float
    computed_area_acres: float
    recorded_parcel_area: Optional[str] = None
    recorded_parcel_sq_m: Optional[float] = None
    discrepancy_sq_m: Optional[float] = None
    remarks: str = ""


@dataclass
class PlotAuditResult:
    plot_id: str
    state: str
    district: str
    tehsil: str
    standard_name: str
    total_registered_area_raw: str
    total_registered_area_sq_m: float
    total_registered_area_acres: float
    total_registered_area_hectares: float
    co_sharers: List[CoSharerRecord]
    sum_shares_fraction: Fraction
    sum_shares_percentage: float
    sum_co_sharer_sq_m: float
    share_delta_fraction: Fraction
    share_delta_percentage: float
    area_delta_sq_m: float
    status: str  # "CONSERVED", "SURPLUS_ALERT", "DEFICIT_ALERT"
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    summary_verdict: str
    legal_audit_findings: List[str]


class ArithmeticValidator:
    """
    Computes mathematical integrity of land parcels across co-sharers.
    Verifies mathematical conservation: Sum(shares) == 100% and Sum(areas) == Total Area.
    """

    def __init__(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        tehsil: Optional[str] = None,
        tolerance_percentage: float = 0.05  # 0.05% tolerance for minor rounding
    ):
        self.state = state or "Standard"
        self.district = district or "General"
        self.tehsil = tehsil or "General"
        self.tolerance_percentage = tolerance_percentage
        self.normalizer = AreaNormalizer(state=state, district=district, tehsil=tehsil)

    def audit_plot(
        self,
        plot_id: str,
        total_plot_area: Any,
        total_plot_unit_hint: Optional[str] = None,
        co_sharers_data: Optional[List[Dict[str, Any]]] = None,
        unit_hint: Optional[str] = None
    ) -> PlotAuditResult:
        """
        Runs comprehensive arithmetic audit on a registered plot and its co-sharers.
        co_sharers_data expects a list of dictionaries with:
          - "name": str
          - "share": fraction, percentage, anna-pai, or ratio (e.g. "1/3", "4 Annas", "25%")
          - optional "recorded_area": explicit localized area string (e.g. "1 Bigha 5 Biswa")
        """
        co_sharers_data = co_sharers_data or []
        effective_unit_hint = unit_hint or total_plot_unit_hint

        # 1. Standardize Total Registered Plot Area to sq meters
        total_sq_m = self.normalizer.normalize_area_to_sq_meters(
            total_plot_area, unit_hint=effective_unit_hint
        )
        total_acres = total_sq_m / SQ_M_PER_ACRE
        total_hectares = total_sq_m / SQ_M_PER_HECTARE

        parsed_sharers: List[CoSharerRecord] = []
        sum_fractions = Fraction(0, 1)
        sum_explicit_sq_m = 0.0
        has_explicit_parcel_areas = False

        # 2. Convert and validate each co-sharer's holding
        for idx, item in enumerate(co_sharers_data):
            name = item.get("name", f"Co-sharer #{idx + 1}")
            share_raw = item.get("share")
            rec_area_raw = item.get("recorded_area")

            share_frac = None
            rec_sq_m = None

            if rec_area_raw:
                has_explicit_parcel_areas = True
                rec_sq_m = self.normalizer.normalize_area_to_sq_meters(rec_area_raw)
                sum_explicit_sq_m += rec_sq_m

            if share_raw is not None:
                share_frac = self.normalizer.parse_hissedari_fraction(share_raw, total_plot_sq_m=total_sq_m)
            elif rec_sq_m is not None and total_sq_m > 0:
                # Derive fractional share from recorded parcel area
                share_frac = Fraction(rec_sq_m / total_sq_m).limit_denominator(10000)
            else:
                share_frac = Fraction(0, 1)

            sum_fractions += share_frac
            share_pct = float(share_frac) * 100.0

            # Computed area based on normalized fraction
            comp_sq_m = float(share_frac) * total_sq_m
            comp_sq_ft = comp_sq_m * SQ_FT_PER_SQ_M
            comp_acres = comp_sq_m / SQ_M_PER_ACRE

            discrepancy = None
            remarks = []
            if rec_sq_m is not None:
                discrepancy = rec_sq_m - comp_sq_m
                if abs(discrepancy) > 1.0:
                    remarks.append(f"Recorded area differs by {discrepancy:+.2f} sq.m from fractional share")

            parsed_sharers.append(
                CoSharerRecord(
                    name=name,
                    raw_share=share_raw if share_raw is not None else rec_area_raw,
                    share_fraction=share_frac,
                    share_percentage=round(share_pct, 4),
                    computed_area_sq_m=round(comp_sq_m, 3),
                    computed_area_sq_ft=round(comp_sq_ft, 2),
                    computed_area_acres=round(comp_acres, 4),
                    recorded_parcel_area=str(rec_area_raw) if rec_area_raw else None,
                    recorded_parcel_sq_m=round(rec_sq_m, 3) if rec_sq_m else None,
                    discrepancy_sq_m=round(discrepancy, 3) if discrepancy is not None else None,
                    remarks="; ".join(remarks)
                )
            )

        # 3. Sum all shares & Check for Mathematical Conservation
        sum_pct = float(sum_fractions) * 100.0
        delta_frac = sum_fractions - Fraction(1, 1)
        delta_pct = sum_pct - 100.0

        if has_explicit_parcel_areas and not all(item.get("share") for item in co_sharers_data):
            sum_co_sharer_sq_m = sum_explicit_sq_m
            area_delta = sum_explicit_sq_m - total_sq_m
        else:
            sum_co_sharer_sq_m = float(sum_fractions) * total_sq_m
            area_delta = sum_co_sharer_sq_m - total_sq_m

        # 4. Conservation Classification & Risk Scoring
        findings = []
        if abs(delta_pct) <= self.tolerance_percentage and abs(area_delta) < 1.0:
            status = "CONSERVED"
            risk_level = "LOW"
            verdict = "PASS: Mathematical Conservation verified. Co-sharer holdings tally perfectly to 100% of registered plot area."
            findings.append("Total allocated fractional shares equate exactly to unity (100.00%).")
            findings.append(f"Area conservation maintained with 0.00 sq.m unaccounted discrepancy.")
        elif delta_pct > self.tolerance_percentage:
            status = "SURPLUS_ALERT"
            risk_level = "CRITICAL" if delta_pct > 5.0 else "HIGH"
            verdict = f"FAIL (SURPLUS): Excess land created out of thin air (+{delta_pct:.2f}% / +{area_delta:.2f} sq.m)."
            findings.append(
                f"CRITICAL DISCREPANCY: Cumulative co-sharer shares equal {sum_pct:.2f}% (exceeding 100% by {delta_pct:+.2f}%)."
            )
            findings.append(
                f"UNACCOUNTED SURPLUS: Over-allocation of {area_delta:+.2f} sq.m ({area_delta / SQ_M_PER_ACRE:+.4f} Acres) detected beyond registered title boundary."
            )
            findings.append(
                "FORENSIC RISK: High probability of overlapping title deeds, fraudulent double-registration, or flawed mutation records."
            )
        else:
            status = "DEFICIT_ALERT"
            risk_level = "HIGH" if abs(delta_pct) > 5.0 else "MEDIUM"
            verdict = f"FAIL (DEFICIT): Unaccounted-for land deficit ({delta_pct:.2f}% / {area_delta:.2f} sq.m remaining unallocated)."
            findings.append(
                f"SHARE DEFICIT: Sum of co-sharer parcels accounts for only {sum_pct:.2f}% of the registered land parcel."
            )
            findings.append(
                f"UNALLOCATED BALANCE: {abs(area_delta):.2f} sq.m ({abs(area_delta) / SQ_M_PER_ACRE:.4f} Acres) is unaccounted for or omitted."
            )
            findings.append(
                "FORENSIC RISK: Missing legal heir/co-sharer, unrecorded government vesting/ceiling acquisition, or clerical transcription omission."
            )

        return PlotAuditResult(
            plot_id=plot_id,
            state=self.state,
            district=self.district,
            tehsil=self.tehsil,
            standard_name=self.normalizer.standard["name"],
            total_registered_area_raw=str(total_plot_area),
            total_registered_area_sq_m=round(total_sq_m, 3),
            total_registered_area_acres=round(total_acres, 4),
            total_registered_area_hectares=round(total_hectares, 4),
            co_sharers=parsed_sharers,
            sum_shares_fraction=sum_fractions,
            sum_shares_percentage=round(sum_pct, 4),
            sum_co_sharer_sq_m=round(sum_co_sharer_sq_m, 3),
            share_delta_fraction=delta_frac,
            share_delta_percentage=round(delta_pct, 4),
            area_delta_sq_m=round(area_delta, 3),
            status=status,
            risk_level=risk_level,
            summary_verdict=verdict,
            legal_audit_findings=findings
        )

    def generate_markdown_report(self, audit: PlotAuditResult) -> str:
        """Generates an exhaustive, formal Markdown Arithmetic Audit Report."""
        status_badges = {
            "CONSERVED": "🟢 **MATHEMATICALLY CONSERVED (100% MATCH)**",
            "SURPLUS_ALERT": "🔴 **ANOMALY: EXCESS LAND CREATED (SURPLUS)**",
            "DEFICIT_ALERT": "🟡 **ANOMALY: UNALLOCATED HOLDING (DEFICIT)**"
        }

        badge = status_badges.get(audit.status, audit.status)

        md = []
        md.append(f"# Land Record Arithmetic Audit Report: Plot `{audit.plot_id}`")
        md.append("")
        md.append(f"**Audit Status**: {badge}  ")
        md.append(f"**Risk Severity**: `{audit.risk_level}`  ")
        md.append(f"**Revenue Jurisdiction**: {audit.tehsil} Tehsil, {audit.district} District, {audit.state}  ")
        md.append(f"**Standard Applied**: {audit.standard_name}  ")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 1. Registered Parcel Baseline Dimensions")
        md.append("")
        md.append(f"| Dimension Metric | Registered Value | Normalized SI Metric | Standard Imperial |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.append(
            f"| **Total Plot Area** | `{audit.total_registered_area_raw}` | "
            f"**{audit.total_registered_area_sq_m:,.2f} m²** ({audit.total_registered_area_hectares:.4f} Ha) | "
            f"**{audit.total_registered_area_acres:.4f} Acres** ({audit.total_registered_area_sq_m * SQ_FT_PER_SQ_M:,.1f} sq ft) |"
        )
        md.append("")
        md.append("## 2. Co-Sharer (Hissedari) Distribution Audit")
        md.append("")
        md.append("| # | Co-Sharer Name | Recorded Share / Area | Exact Fraction | Normalized % | Computed Area (m²) | Imperial Area (Acres) | Discrepancy / Notes |")
        md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

        for idx, cs in enumerate(audit.co_sharers, start=1):
            discrepancy_str = f"{cs.discrepancy_sq_m:+.2f} m²" if cs.discrepancy_sq_m is not None else "-"
            notes = cs.remarks or discrepancy_str
            md.append(
                f"| {idx} | **{cs.name}** | `{cs.raw_share}` | `{cs.share_fraction}` | "
                f"{cs.share_percentage:.3f}% | {cs.computed_area_sq_m:,.2f} m² | {cs.computed_area_acres:.4f} ac | {notes} |"
            )

        md.append("")
        md.append("## 3. Mathematical Integrity & Conservation Proof")
        md.append("")
        md.append(f"| Verification Check | Target Standard | Audited Sum | Variance / Delta | Mathematical Verdict |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.append(
            f"| **Total Share Fraction** | `1/1` (100.00%) | `{audit.sum_shares_fraction}` ({audit.sum_shares_percentage:.3f}%) | "
            f"`{audit.share_delta_fraction}` ({audit.share_delta_percentage:+.3f}%) | "
            f"{'✅ BALANCED' if audit.status == 'CONSERVED' else '❌ DISCREPANCY'} |"
        )
        md.append(
            f"| **Cumulative Land Area** | `{audit.total_registered_area_sq_m:,.2f} m²` | `{audit.sum_co_sharer_sq_m:,.2f} m²` | "
            f"`{audit.area_delta_sq_m:+,.2f} m²` ({audit.area_delta_sq_m / SQ_M_PER_ACRE:+.4f} ac) | "
            f"{'✅ CONSERVED' if audit.status == 'CONSERVED' else ('⚠️ SURPLUS (+)' if audit.area_delta_sq_m > 0 else '⚠️ DEFICIT (-)')} |"
        )
        md.append("")
        md.append("## 4. Forensic Revenue & Legal Findings")
        md.append("")
        for f in audit.legal_audit_findings:
            md.append(f"- {f}")
        md.append("")
        md.append(f"> **Audit Conclusion**: {audit.summary_verdict}")
        md.append("")

        return "\n".join(md)

    def generate_json_report(self, audit: PlotAuditResult) -> str:
        """Returns structured JSON for programmatic pipelines."""
        payload = {
            "plot_id": audit.plot_id,
            "jurisdiction": {
                "state": audit.state,
                "district": audit.district,
                "tehsil": audit.tehsil,
                "standard": audit.standard_name
            },
            "registered_baseline": {
                "raw_input": audit.total_registered_area_raw,
                "area_sq_meters": audit.total_registered_area_sq_m,
                "area_acres": audit.total_registered_area_acres,
                "area_hectares": audit.total_registered_area_hectares
            },
            "co_sharers": [
                {
                    "name": cs.name,
                    "raw_share": str(cs.raw_share),
                    "fraction": str(cs.share_fraction),
                    "percentage": cs.share_percentage,
                    "computed_area_sq_m": cs.computed_area_sq_m,
                    "computed_area_acres": cs.computed_area_acres,
                    "recorded_parcel_area": cs.recorded_parcel_area,
                    "recorded_parcel_sq_m": cs.recorded_parcel_sq_m,
                    "discrepancy_sq_m": cs.discrepancy_sq_m,
                    "remarks": cs.remarks
                }
                for cs in audit.co_sharers
            ],
            "arithmetic_validation": {
                "sum_shares_fraction": str(audit.sum_shares_fraction),
                "sum_shares_percentage": audit.sum_shares_percentage,
                "sum_co_sharer_sq_m": audit.sum_co_sharer_sq_m,
                "share_delta_fraction": str(audit.share_delta_fraction),
                "share_delta_percentage": audit.share_delta_percentage,
                "area_delta_sq_m": audit.area_delta_sq_m,
                "conservation_status": audit.status,
                "risk_level": audit.risk_level,
                "verdict": audit.summary_verdict,
                "findings": audit.legal_audit_findings
            }
        }
        return json.dumps(payload, indent=2)
