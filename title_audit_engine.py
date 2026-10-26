"""
Discrepancy & Title Audit Engine (Sarvam-105B Integration).
Compares official land records and mutation history against oral testimony vanshavali
and statutory succession rules to detect irregularities and compile a forensic discrepancy matrix.

Process:
1. Map reconstructed family tree against names on extracted land records.
2. Apply statutory succession rules (HSA 1956 / 2005) to compute claimant's theoretical lawful share.
3. Cross-reference against mutation history to detect red flags:
   - Legal heir omitted without registered relinquishment deed (Haq-Tyag).
   - Mutation recorded during minority of an heir without guardian representation (HMGA 1956 Sec 8).
   - Area transferred exceeding transferor's recorded share (Nemo dat quod non habet).
4. Output structured discrepancy matrix with severity, exact line items, and bounding boxes.
"""

from datetime import datetime
from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple
import json
import re

from schema import VanshavaliTree, PersonNode, OralTestimonyNormalizedSchema
from title_audit_models import (
    LandRecordDocument,
    RecordedCoSharer,
    MutationRecord,
    MutationType,
    DiscrepancyItem,
    DiscrepancyMatrixReport,
    StatutoryHeirShare,
    DefectCategory,
    LegalSeverity,
    BoundingBox,
    DocumentLineItem,
)
from statutory_succession import StatutorySuccessionEngine
from sarvam_title_auditor import SarvamTitleAuditor
from area_normalizer import AreaNormalizer
from regional_standards import SQ_M_PER_ACRE


class TitleAuditEngine:
    """
    Forensic Title Audit & Discrepancy Engine.
    Executes deep cross-examination of revenue records, oral family trees, and succession law.
    """

    def __init__(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        tehsil: Optional[str] = None,
        sarvam_api_key: Optional[str] = None,
        sarvam_model: str = "sarvam-105b-conversations"
    ):
        self.state = state or "General"
        self.district = district or "General"
        self.tehsil = tehsil or "General"
        self.normalizer = AreaNormalizer(state=state, district=district, tehsil=tehsil)
        self.succession_engine = StatutorySuccessionEngine()
        self.sarvam_auditor = SarvamTitleAuditor(api_key=sarvam_api_key, model=sarvam_model)

    def audit_title(
        self,
        vanshavali: VanshavaliTree,
        land_record: LandRecordDocument,
        mutations: List[MutationRecord],
        oral_testimony: Optional[OralTestimonyNormalizedSchema] = None,
        audit_id: Optional[str] = None
    ) -> DiscrepancyMatrixReport:
        """
        Executes complete Title Audit pipeline and returns a DiscrepancyMatrixReport.
        """
        audit_id = audit_id or f"TA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # 1. Apply Statutory Succession Rules to Determine Theoretical Lawful Shares
        statutory_shares = self.succession_engine.compute_succession_shares(
            vanshavali=vanshavali,
            total_plot_area_sq_m=land_record.total_area_sq_m
        )

        # Map person nodes for fast lookup
        persons_map: Dict[str, PersonNode] = {m.person_id: m for m in vanshavali.members}
        head = vanshavali.ancestral_head
        if head.person_id not in persons_map:
            persons_map[head.person_id] = head

        # Identify Claimant
        claimant_node = next((p for p in persons_map.values() if p.is_claimant), None)
        claimant_id = claimant_node.person_id if claimant_node else None
        claimant_name = claimant_node.name if claimant_node else "Unknown Claimant"

        # Find Claimant's Statutory Share
        claimant_stat_share = next((s for s in statutory_shares if s.is_claimant), None)
        claimant_theo_fraction_str = claimant_stat_share.statutory_fraction_str if claimant_stat_share else "0"
        claimant_theo_fraction = Fraction(claimant_theo_fraction_str)
        claimant_theo_area_sq_m = float(claimant_theo_fraction) * land_record.total_area_sq_m

        # 2. Map Family Tree against Extracted Land Records
        recorded_co_sharers_matched = self._map_family_tree_to_land_records(
            vanshavali=vanshavali,
            land_record=land_record
        )

        # Update statutory_shares with recorded values found on land record
        for stat_share in statutory_shares:
            matched_record = recorded_co_sharers_matched.get(stat_share.person_id)
            if matched_record:
                rec_frac_str = matched_record.share_fraction or "0"
                rec_frac = Fraction(rec_frac_str)
                rec_area = matched_record.recorded_area_sq_m or (float(rec_frac) * land_record.total_area_sq_m)
                theo_frac = Fraction(stat_share.statutory_fraction_str)
                deprived_frac = theo_frac - rec_frac
                deprived_area = (float(theo_frac) - float(rec_frac)) * land_record.total_area_sq_m

                stat_share.recorded_share_fraction_str = rec_frac_str
                stat_share.recorded_share_fraction_val = float(rec_frac)
                stat_share.recorded_area_sq_m = round(rec_area, 2)
                stat_share.deprived_fraction_str = str(deprived_frac) if deprived_frac > 0 else "0"
                stat_share.deprived_area_sq_m = round(max(0.0, deprived_area), 2)

                if deprived_frac > 0:
                    stat_share.status = "Deprived / Diluted"
                elif rec_frac > theo_frac:
                    stat_share.status = "Inflated / Surplus"
                else:
                    stat_share.status = "Accorded"
            else:
                # Omitted completely from official land record
                theo_frac = Fraction(stat_share.statutory_fraction_str)
                if theo_frac > 0:
                    stat_share.recorded_share_fraction_str = "0"
                    stat_share.recorded_share_fraction_val = 0.0
                    stat_share.recorded_area_sq_m = 0.0
                    stat_share.deprived_fraction_str = str(theo_frac)
                    stat_share.deprived_area_sq_m = round(float(theo_frac) * land_record.total_area_sq_m, 2)
                    stat_share.status = "Omitted from Title"

        # Check claimant recorded holding
        claimant_rec = recorded_co_sharers_matched.get(claimant_id)
        if claimant_rec:
            claimant_rec_share_str = claimant_rec.share_fraction or "0"
            claimant_rec_area_sq_m = claimant_rec.recorded_area_sq_m or (float(Fraction(claimant_rec_share_str)) * land_record.total_area_sq_m)
        else:
            claimant_rec_share_str = "0 (Omitted)"
            claimant_rec_area_sq_m = 0.0

        claimant_deprived_sq_m = max(0.0, claimant_theo_area_sq_m - claimant_rec_area_sq_m)
        claimant_deprived_acres = claimant_deprived_sq_m / SQ_M_PER_ACRE

        # 3. Cross-reference against Mutation History to Detect Red Flags
        detected_defects: List[DiscrepancyItem] = []
        defect_counter = 1

        # Red Flag A: Legal Heir Omitted without Registered Relinquishment Deed (Haq-Tyag)
        omission_defects, defect_counter = self._detect_omitted_heirs_without_haq_tyag(
            vanshavali=vanshavali,
            mutations=mutations,
            statutory_shares=statutory_shares,
            land_record=land_record,
            start_idx=defect_counter
        )
        detected_defects.extend(omission_defects)

        # Red Flag B: Mutation Recorded during Minority without Guardian Representation
        minority_defects, defect_counter = self._detect_unrepresented_minor_mutations(
            vanshavali=vanshavali,
            mutations=mutations,
            statutory_shares=statutory_shares,
            land_record=land_record,
            start_idx=defect_counter
        )
        detected_defects.extend(minority_defects)

        # Red Flag C: Area Transferred Exceeding Transferor's Recorded Share (Excess Sale)
        excess_defects, defect_counter = self._detect_excess_area_conveyance(
            vanshavali=vanshavali,
            mutations=mutations,
            land_record=land_record,
            recorded_matched=recorded_co_sharers_matched,
            start_idx=defect_counter
        )
        detected_defects.extend(excess_defects)

        # Red Flag D: Co-sharer Fractional Dilution / Omission on current Jamabandi
        dilution_defects, defect_counter = self._detect_current_title_omissions(
            vanshavali=vanshavali,
            land_record=land_record,
            statutory_shares=statutory_shares,
            recorded_matched=recorded_co_sharers_matched,
            start_idx=defect_counter
        )
        detected_defects.extend(dilution_defects)

        # 4. Assess Overall Title Risk Score
        has_critical = any(d.severity == LegalSeverity.CRITICAL for d in detected_defects)
        has_high = any(d.severity == LegalSeverity.HIGH for d in detected_defects)

        if has_critical:
            overall_risk = "CRITICAL_TITLE_DEFECT"
            summary_verdict = (
                f"TITLE CLOUD DETECTED (CRITICAL): Title is fatally defective. "
                f"Illegal omission of statutory heirs without registered Haq-Tyag and unauthorized over-conveyance "
                f"deprived claimant '{claimant_name}' of {claimant_theo_fraction_str} share "
                f"({claimant_deprived_sq_m:,.2f} m² / {claimant_deprived_acres:.4f} Acres)."
            )
        elif has_high:
            overall_risk = "HIGH_RISK_TITLE"
            summary_verdict = (
                f"TITLE DEFECT DETECTED (HIGH): Multiple substantive statutory irregularities found. "
                f"Statutory succession was violated in summary mutation proceedings."
            )
        elif detected_defects:
            overall_risk = "MEDIUM_RISK"
            summary_verdict = "IRREGULARITIES DETECTED: Procedural revenue defects require rectification."
        else:
            overall_risk = "CLEAR_TITLE"
            summary_verdict = "TITLE VERIFIED: Extracted records harmonize with statutory succession rules."

        # 5. Synthesize Sarvam-105B Intelligence & Legal Opinion
        sarvam_analysis = self.sarvam_auditor.analyze_title_case(
            vanshavali_summary={
                "ancestral_head": vanshavali.ancestral_head.model_dump(),
                "total_members": len(vanshavali.members),
                "members": [m.model_dump() for m in vanshavali.members],
                "relationships": [r.model_dump() for r in vanshavali.relationships]
            },
            claimant_info={
                "id": claimant_id,
                "name": claimant_name,
                "theoretical_share": claimant_theo_fraction_str,
                "recorded_share": claimant_rec_share_str,
                "deprived_area_sq_m": claimant_deprived_sq_m,
                "relationship": claimant_stat_share.relationship_to_deceased if claimant_stat_share else "Claimant"
            },
            statutory_shares=[s.model_dump() for s in statutory_shares],
            land_record=land_record.model_dump(),
            mutations=[m.model_dump() for m in mutations],
            detected_defects=[d.model_dump() for d in detected_defects]
        )

        roadmap = self._generate_legal_roadmap(detected_defects, claimant_name, claimant_theo_fraction_str)

        return DiscrepancyMatrixReport(
            audit_id=audit_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            jurisdiction={
                "state": land_record.state,
                "district": land_record.district,
                "tehsil": land_record.tehsil,
                "village": land_record.village
            },
            khasra_numbers=land_record.khasra_numbers,
            total_plot_area_raw=land_record.total_area_raw,
            total_plot_area_sq_m=land_record.total_area_sq_m,
            claimant_id=claimant_id,
            claimant_name=claimant_name,
            claimant_theoretical_share=claimant_theo_fraction_str,
            claimant_recorded_share=claimant_rec_share_str,
            claimant_deprived_area_sq_m=round(claimant_deprived_sq_m, 2),
            claimant_deprived_area_acres=round(claimant_deprived_acres, 4),
            statutory_heir_shares=statutory_shares,
            discrepancy_matrix=detected_defects,
            overall_title_risk=overall_risk,
            summary_verdict=summary_verdict,
            sarvam_105b_legal_opinion=sarvam_analysis.get("legal_opinion"),
            recommended_legal_roadmap=roadmap
        )

    # -------------------------------------------------------------------------
    # Helper Detectors
    # -------------------------------------------------------------------------

    def _detect_omitted_heirs_without_haq_tyag(
        self,
        vanshavali: VanshavaliTree,
        mutations: List[MutationRecord],
        statutory_shares: List[StatutoryHeirShare],
        land_record: LandRecordDocument,
        start_idx: int
    ) -> Tuple[List[DiscrepancyItem], int]:
        """
        Detects Class I legal heirs omitted from inheritance mutations without a registered Haq-Tyag.
        Identifies direct Class I heirs of the specific deceased ancestor whose estate devolved.
        """
        defects: List[DiscrepancyItem] = []
        counter = start_idx

        # Adjacency maps for the family tree
        members_by_id = {m.person_id: m for m in vanshavali.members}
        head = vanshavali.ancestral_head
        if head.person_id not in members_by_id:
            members_by_id[head.person_id] = head

        children_of: Dict[str, List[str]] = {}
        spouses_of: Dict[str, List[str]] = {}

        for rel in vanshavali.relationships:
            if rel.relation_type == "parent_of":
                children_of.setdefault(rel.source_id, []).append(rel.target_id)
            elif rel.relation_type == "child_of":
                children_of.setdefault(rel.target_id, []).append(rel.source_id)
            elif rel.relation_type == "spouse_of":
                spouses_of.setdefault(rel.source_id, []).append(rel.target_id)
                spouses_of.setdefault(rel.target_id, []).append(rel.source_id)

        inheritance_mutations = [
            m for m in mutations if m.mutation_type == MutationType.INHERITANCE_FAUTI
        ]

        for mut in inheritance_mutations:
            # Determine who is the deceased person
            deceased_name = mut.deceased_predecessor or head.name
            deceased_node = next(
                (m for m in members_by_id.values() if self._names_match(m.name, deceased_name)),
                head
            )

            # Direct Class I heirs of this deceased person: children and spouses
            direct_heir_ids = set(children_of.get(deceased_node.person_id, [])) | set(spouses_of.get(deceased_node.person_id, []))
            entitled_heirs = [members_by_id[hid] for hid in direct_heir_ids if hid in members_by_id]

            if not entitled_heirs:
                # Fallback to statutory shares if no direct children registered
                entitled_heirs = [members_by_id[s.person_id] for s in statutory_shares if s.person_id in members_by_id]

            for heir_node in entitled_heirs:
                # Check if this heir is listed as a transferee
                is_named = any(self._names_match(heir_node.name, t) for t in mut.transferee_names)
                if not is_named:
                    # Heir was omitted from this inheritance mutation!
                    if not mut.has_registered_haq_tyag:
                        is_claimant = heir_node.is_claimant
                        severity = LegalSeverity.CRITICAL if is_claimant else LegalSeverity.HIGH

                        stat_share_obj = next((s for s in statutory_shares if s.person_id == heir_node.person_id), None)
                        theo_fraction_str = stat_share_obj.statutory_fraction_str if stat_share_obj else "Direct Share"
                        theo_area_sq_m = stat_share_obj.theoretical_area_sq_m if stat_share_obj else 0.0
                        theo_area_acres = stat_share_obj.theoretical_area_acres if stat_share_obj else 0.0

                        bbox = mut.bounding_box or BoundingBox(ymin=120.0, xmin=45.0, ymax=180.0, xmax=550.0)
                        doc_cite = (
                            f"Mutation No. {mut.mutation_no} ({mut.mutation_date_or_year}), "
                            f"Column 'Order of Revenue Officer' [Col 8]"
                        )
                        if mut.line_item:
                            doc_cite = f"{mut.line_item.doc_id}, Line: '{mut.line_item.line_text}'"

                        narrative = (
                            f"FATAL SUCCESSION DEFECT: Legal heir '{heir_node.name}' "
                            f"(entitled under Hindu Succession Act) was omitted from "
                            f"Inheritance Mutation No. {mut.mutation_no} ({mut.mutation_date_or_year}) "
                            f"sanctioned on the demise of '{deceased_name}'. "
                            f"No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) "
                            f"of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer "
                            f"is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787)."
                        )

                        remedy = (
                            f"File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. {mut.mutation_no}. "
                            f"Seek immediate correction of Jamabandi entries to restore {heir_node.name}'s lawful share."
                        )

                        defects.append(
                            DiscrepancyItem(
                                defect_id=f"DEF-{counter:03d}",
                                title=f"Omission of Legal Heir ({heir_node.name}) without Registered Haq-Tyag",
                                defect_category=DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG,
                                severity=severity,
                                statutory_violations=[
                                    "Hindu Succession Act 1956, Section 6 & 8",
                                    "Registration Act 1908, Section 17(1)(b) & Section 49",
                                    "Transfer of Property Act 1882, Section 9"
                                ],
                                parties_involved={
                                    "omitted_heir": heir_node.name,
                                    "deceased_predecessor": deceased_name,
                                    "beneficiaries": mut.transferee_names
                                },
                                theoretical_share_str=theo_fraction_str,
                                recorded_share_str="0 (Omitted)",
                                deprived_share_str=theo_fraction_str,
                                deprived_area_sq_m=theo_area_sq_m,
                                deprived_area_acres=theo_area_acres,
                                document_citation=doc_cite,
                                bounding_box=bbox,
                                forensic_narrative=narrative,
                                actionable_remedy=remedy
                            )
                        )
                        counter += 1

        return defects, counter

    def _detect_unrepresented_minor_mutations(
        self,
        vanshavali: VanshavaliTree,
        mutations: List[MutationRecord],
        statutory_shares: List[StatutoryHeirShare],
        land_record: LandRecordDocument,
        start_idx: int
    ) -> Tuple[List[DiscrepancyItem], int]:
        """
        Detects mutations executed or recorded during the minority of an heir without lawful guardian representation.
        """
        defects: List[DiscrepancyItem] = []
        counter = start_idx

        for mut in mutations:
            if mut.minor_heirs_involved:
                # Check guardian representation & court permission
                if not mut.guardian_represented or (mut.mutation_type == MutationType.SALE_TRANSFER and not mut.district_court_permission_sec8):
                    minor_names_str = ", ".join(mut.minor_names) or "Minor Heir"
                    bbox = mut.bounding_box or BoundingBox(ymin=210.0, xmin=50.0, ymax=275.0, xmax=540.0)
                    doc_cite = f"Mutation No. {mut.mutation_no} ({mut.mutation_date_or_year}), Column 8/11"

                    is_claimant_minor = any(
                        any(self._names_match(m, s.name) for m in mut.minor_names)
                        for s in statutory_shares if s.is_claimant
                    )

                    severity = LegalSeverity.CRITICAL if is_claimant_minor else LegalSeverity.HIGH

                    narrative = (
                        f"STATUTORY MINORITY IMPAIRMENT: Mutation No. {mut.mutation_no} ({mut.mutation_date_or_year}) "
                        f"affected the proprietary estate of minor(s) [{minor_names_str}] without lawful guardian representation "
                        f"or without mandatory prior sanction from the District Court under Section 8(2) of the Hindu Minority "
                        f"and Guardianship Act, 1956. Any transaction or mutation adverse to a minor without court approval is "
                        f"voidable at the minor's option under Section 8(3) HMGA and void ab initio if completely unrepresented."
                    )

                    remedy = (
                        f"Institute suit for Declaration and Invalidation of Mutation No. {mut.mutation_no} "
                        f"under Section 8(3) of the Hindu Minority and Guardianship Act, 1956 read with Section 31 "
                        f"of the Specific Relief Act, 1963. Limitation commences from the date of attaining majority."
                    )

                    defects.append(
                        DiscrepancyItem(
                            defect_id=f"DEF-{counter:03d}",
                            title=f"Unrepresented Minor Mutation ({minor_names_str}) without HMGA Sec 8 Sanction",
                            defect_category=DefectCategory.UNREPRESENTED_MINOR_MUTATION,
                            severity=severity,
                            statutory_violations=[
                                "Hindu Minority and Guardianship Act 1956, Section 6 & 8(2)",
                                "Indian Majority Act 1875, Section 3",
                                "Civil Procedure Code 1908, Order XXXII Rules 1-3"
                            ],
                            parties_involved={
                                "minors": mut.minor_names,
                                "transferor_or_applicant": mut.transferor_names,
                                "beneficiaries": mut.transferee_names
                            },
                            theoretical_share_str=None,
                            recorded_share_str=mut.share_transferred_raw,
                            deprived_share_str=mut.share_transferred_raw,
                            deprived_area_sq_m=mut.area_transferred_sq_m,
                            deprived_area_acres=mut.area_transferred_sq_m / SQ_M_PER_ACRE if mut.area_transferred_sq_m else None,
                            document_citation=doc_cite,
                            bounding_box=bbox,
                            forensic_narrative=narrative,
                            actionable_remedy=remedy
                        )
                    )
                    counter += 1

        return defects, counter

    def _detect_excess_area_conveyance(
        self,
        vanshavali: VanshavaliTree,
        mutations: List[MutationRecord],
        land_record: LandRecordDocument,
        recorded_matched: Dict[str, RecordedCoSharer],
        start_idx: int
    ) -> Tuple[List[DiscrepancyItem], int]:
        """
        Detects transfers / sales where the transferor alienates area exceeding their recorded or lawful share.
        Principle: Nemo dat quod non habet (Sec 44 & 48 Transfer of Property Act, 1882).
        """
        defects: List[DiscrepancyItem] = []
        counter = start_idx

        transfer_mutations = [
            m for m in mutations if m.mutation_type in (MutationType.SALE_TRANSFER, MutationType.GIFT_HIBA)
        ]

        # Calculate each co-sharer's baseline recorded area/fraction
        co_sharer_holdings: Dict[str, float] = {}
        for cs in land_record.co_sharers:
            norm_name = self._normalize_name(cs.name)
            sq_m = cs.recorded_area_sq_m
            if not sq_m and cs.share_fraction:
                sq_m = float(Fraction(cs.share_fraction)) * land_record.total_area_sq_m
            co_sharer_holdings[norm_name] = sq_m or 0.0

        for mut in transfer_mutations:
            area_transferred = mut.area_transferred_sq_m
            if not area_transferred and mut.area_transferred_raw:
                area_transferred = self.normalizer.normalize_area_to_sq_meters(mut.area_transferred_raw)

            # Check each transferor's holding
            for t_name in mut.transferor_names:
                norm_t = self._normalize_name(t_name)
                # Find matching holding
                recorded_holding = next(
                    (val for k, val in co_sharer_holdings.items() if self._names_match(k, norm_t)),
                    None
                )

                if recorded_holding is not None and area_transferred is not None:
                    if area_transferred > (recorded_holding + 1.0):  # 1 sq m tolerance
                        excess_sq_m = area_transferred - recorded_holding
                        excess_acres = excess_sq_m / SQ_M_PER_ACRE

                        bbox = mut.bounding_box or BoundingBox(ymin=310.0, xmin=40.0, ymax=390.0, xmax=560.0)
                        doc_cite = (
                            f"Sale Mutation No. {mut.mutation_no} ({mut.mutation_date_or_year}), "
                            f"Transferor: {t_name}, Area: {mut.area_transferred_raw}"
                        )

                        narrative = (
                            f"CRITICAL OVER-CONVEYANCE (NEMO DAT QUOD NON HABET): Transferor '{t_name}' "
                            f"purported to alienate {area_transferred:,.2f} m² via Mutation No. {mut.mutation_no}, "
                            f"whereas their recorded lawful entitlement on revenue records was only {recorded_holding:,.2f} m². "
                            f"This constitutes an unauthorized illegal over-conveyance of +{excess_sq_m:,.2f} m² (+{excess_acres:.4f} Acres). "
                            f"Under Section 44 and 48 of the Transfer of Property Act, 1882, a co-sharer cannot convey any parcel "
                            f"or share exceeding their undivided holding; the excess sale directly encroaches upon co-sharers' title."
                        )

                        remedy = (
                            f"File a Civil Suit for Declaration and Cancellation of Sale Deed / Mutation under "
                            f"Section 31 of the Specific Relief Act, 1963 to void the transaction to the extent of {excess_sq_m:,.2f} m² excess. "
                            f"Obtain an interim injunction against the purchaser under Order XXXIX Rules 1 & 2 CPC."
                        )

                        defects.append(
                            DiscrepancyItem(
                                defect_id=f"DEF-{counter:03d}",
                                title=f"Excess Area Alienated by {t_name} Exceeding Recorded Share (+{excess_sq_m:,.1f} m²)",
                                defect_category=DefectCategory.EXCESS_AREA_CONVEYANCE,
                                severity=LegalSeverity.CRITICAL,
                                statutory_violations=[
                                    "Transfer of Property Act 1882, Section 44 & Section 48",
                                    "Specific Relief Act 1963, Section 31",
                                    "Indian Contract Act 1872, Section 23 (Void unlawful consideration)"
                                ],
                                parties_involved={
                                    "defaulting_transferor": t_name,
                                    "recorded_holding_sq_m": recorded_holding,
                                    "alienated_area_sq_m": area_transferred,
                                    "excess_alienation_sq_m": round(excess_sq_m, 2),
                                    "transferee_purchasers": mut.transferee_names
                                },
                                theoretical_share_str=None,
                                recorded_share_str=str(mut.share_transferred_raw),
                                deprived_share_str=None,
                                deprived_area_sq_m=round(excess_sq_m, 2),
                                deprived_area_acres=round(excess_acres, 4),
                                document_citation=doc_cite,
                                bounding_box=bbox,
                                forensic_narrative=narrative,
                                actionable_remedy=remedy
                            )
                        )
                        counter += 1

        return defects, counter

    def _detect_current_title_omissions(
        self,
        vanshavali: VanshavaliTree,
        land_record: LandRecordDocument,
        statutory_shares: List[StatutoryHeirShare],
        recorded_matched: Dict[str, RecordedCoSharer],
        start_idx: int
    ) -> Tuple[List[DiscrepancyItem], int]:
        """
        Detects omissions or dilutions in the latest Jamabandi / Khatauni compared to theoretical lawful shares.
        """
        defects: List[DiscrepancyItem] = []
        counter = start_idx

        for heir in statutory_shares:
            if heir.statutory_fraction_val <= 0:
                continue

            matched = recorded_matched.get(heir.person_id)
            if not matched:
                # Totally omitted from latest Jamabandi
                severity = LegalSeverity.CRITICAL if heir.is_claimant else LegalSeverity.HIGH
                bbox = BoundingBox(ymin=40.0, xmin=30.0, ymax=100.0, xmax=570.0)
                doc_cite = f"{land_record.doc_type} ({land_record.fasli_year_or_period}), Khatauni/Khewat {land_record.khata_khewat_no}"

                narrative = (
                    f"TITLE REGISTER OMISSION: Statutory Class I heir '{heir.name}' ({heir.relationship_to_deceased}) "
                    f"is totally absent from the ownership column of official {land_record.doc_type} ({land_record.fasli_year_or_period}). "
                    f"Heir's theoretical entitlement is {heir.statutory_fraction_str} ({heir.theoretical_area_sq_m:,.2f} m² / "
                    f"{heir.theoretical_area_acres:.4f} Acres). Omission creates an actionable cloud on title."
                )

                remedy = (
                    f"Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) "
                    f"under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. "
                    f"Concurrently institute a Civil Suit for Partition & Separate Possession."
                )

                defects.append(
                    DiscrepancyItem(
                        defect_id=f"DEF-{counter:03d}",
                        title=f"Total Absence of Legal Heir '{heir.name}' from Current Record of Rights",
                        defect_category=DefectCategory.CO_SHARER_FRACTIONAL_DILUTION,
                        severity=severity,
                        statutory_violations=[
                            "Hindu Succession Act 1956, Section 8 & 10",
                            "Constitution of India, Article 300A (Right to Property)"
                        ],
                        parties_involved={
                            "omitted_heir": heir.name,
                            "co_sharers_recorded": [cs.name for cs in land_record.co_sharers]
                        },
                        theoretical_share_str=heir.statutory_fraction_str,
                        recorded_share_str="0 (Absent)",
                        deprived_share_str=heir.statutory_fraction_str,
                        deprived_area_sq_m=heir.theoretical_area_sq_m,
                        deprived_area_acres=heir.theoretical_area_acres,
                        document_citation=doc_cite,
                        bounding_box=bbox,
                        forensic_narrative=narrative,
                        actionable_remedy=remedy
                    )
                )
                counter += 1

        return defects, counter

    # -------------------------------------------------------------------------
    # Mapping & Normalization Utilities
    # -------------------------------------------------------------------------

    def _map_family_tree_to_land_records(
        self,
        vanshavali: VanshavaliTree,
        land_record: LandRecordDocument
    ) -> Dict[str, RecordedCoSharer]:
        """
        Maps Vanshavali members (PersonNode) to RecordedCoSharers in LandRecordDocument.
        Returns a dict mapping person_id -> RecordedCoSharer.
        """
        matched: Dict[str, RecordedCoSharer] = {}

        for member in vanshavali.members:
            # Try to match member name against co_sharers
            for cs in land_record.co_sharers:
                if self._names_match(member.name, cs.name):
                    matched[member.person_id] = cs
                    break
                # Try member aliases
                if any(self._names_match(alias, cs.name) for alias in member.aliases):
                    matched[member.person_id] = cs
                    break

        return matched

    def _normalize_name(self, name: str) -> str:
        s = name.lower()
        # Remove common prefixes/suffixes/honorifics
        prefixes = [
            "smt.", "smt", "shri", "sh.", "late", "mr.", "mrs.", "sardar",
            "ch.", "choudhary", "babu", "thakur", "pandit", "pt.", "s/o", "w/o", "d/o"
        ]
        for p in prefixes:
            s = re.sub(rf"\b{re.escape(p)}\b", "", s)
        s = re.sub(r"[^\w\s]", "", s)
        return " ".join(s.split())

    def _names_match(self, name1: str, name2: str) -> bool:
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)
        if not n1 or not n2:
            return False
        if n1 == n2:
            return True
        # Check sub-words
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words1.issubset(words2):
            return True
        if words2 and words2.issubset(words1):
            return True
        return False

    def _generate_legal_roadmap(
        self,
        defects: List[DiscrepancyItem],
        claimant_name: str,
        claimant_theo_share: str
    ) -> List[str]:
        """Generates prioritized judicial next steps for claimant's counsel."""
        steps = [
            f"1. **Caveat & Urgent Interim Injunction**: File caveat petitions under Section 148A CPC and seek status-quo injunction under Order XXXIX Rules 1 & 2 CPC against any further alienation of the suit Khasras.",
            f"2. **Statutory Revenue Appeal**: Challenge the fraudulent/omissive Mutation orders before the Collector/Sub-Divisional Officer under the State Land Revenue Act.",
            f"3. **Civil Suit for Partition & Declaration**: Institute a comprehensive Title Suit before the Senior Civil Judge seeking a declaration of {claimant_name}'s {claimant_theo_share} statutory share and physical demarcation by metes and bounds.",
            f"4. **Cancellation of Ultra-Vires Sale Deeds**: Seek decree of cancellation under Section 31 of Specific Relief Act 1963 for any conveyances executed beyond the transferors' legitimate holdings.",
            f"5. **Revenue Register Rectification**: Apply for Fard-Badar / Tarseem-e-Record to update the official Record of Rights reflecting the true Vanshavali."
        ]
        return steps

    # -------------------------------------------------------------------------
    # Markdown & JSON Reporting
    # -------------------------------------------------------------------------

    def generate_markdown_report(self, report: DiscrepancyMatrixReport) -> str:
        """Renders an exhaustive, court-ready Discrepancy Matrix & Title Audit Report."""
        md = []
        md.append(f"# Discrepancy & Title Audit Engine Report (Sarvam-105B)")
        md.append(f"**Audit Reference ID**: `{report.audit_id}` | **Engine**: `{report.engine_version}`")
        md.append(f"**Execution Timestamp**: {report.timestamp}")
        md.append("")
        md.append("---")
        md.append("")

        # Executive Summary & Risk Badge
        risk_badges = {
            "CRITICAL_TITLE_DEFECT": "🔴 **CRITICAL TITLE DEFECT (ACTION REQUIRED)**",
            "HIGH_RISK_TITLE": "🟠 **HIGH RISK TITLE (SUBSTANTIVE DEFECTS)**",
            "MEDIUM_RISK": "🟡 **MEDIUM RISK TITLE (IRREGULARITIES PRESENT)**",
            "CLEAR_TITLE": "🟢 **CLEAR TITLE (VERIFIED)**"
        }
        badge = risk_badges.get(report.overall_title_risk, report.overall_title_risk)

        md.append("## 1. Executive Title Audit Summary")
        md.append("")
        md.append(f"| Audit Metric | Assessment Details |")
        md.append(f"| :--- | :--- |")
        md.append(f"| **Overall Title Health** | {badge} |")
        md.append(f"| **Target Revenue Jurisdiction** | {report.jurisdiction['village']}, Tehsil {report.jurisdiction['tehsil']}, District {report.jurisdiction['district']}, {report.jurisdiction['state']} |")
        md.append(f"| **Khasra / Survey Parcels** | `{', '.join(report.khasra_numbers) or 'Audited Khasras'}` |")
        md.append(f"| **Total Registered Parcel Area** | `{report.total_plot_area_raw}` ({report.total_plot_area_sq_m:,.2f} m² / {report.total_plot_area_sq_m / SQ_M_PER_ACRE:.4f} Acres) |")
        md.append(f"| **Claimant Name & ID** | **{report.claimant_name}** (`{report.claimant_id}`) |")
        md.append(f"| **Theoretical Lawful Share (HSA)** | **`{report.claimant_theoretical_share}`** |")
        md.append(f"| **Official Recorded Share** | **`{report.claimant_recorded_share}`** |")
        md.append(f"| **Claimant Deprivation / Deficit** | **{report.claimant_deprived_area_sq_m:,.2f} m²** ({report.claimant_deprived_area_acres:.4f} Acres) |")
        md.append(f"| **Total Irregularities Detected** | **{len(report.discrepancy_matrix)} Defects Identified** |")
        md.append("")
        md.append(f"> **Verdict**: {report.summary_verdict}")
        md.append("")

        # Statutory Succession Table
        md.append("## 2. Statutory Succession Entitlement Ledger (Hindu Succession Act)")
        md.append("")
        md.append("| Person ID | Legal Heir Name | Statutory Relationship | Class | Theoretical Share | Entitled Area (m²) | Recorded Share | Status |")
        md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |")
        for h in report.statutory_heir_shares:
            c_tag = " ⭐ (Claimant)" if h.is_claimant else ""
            rec_str = h.recorded_share_fraction_str or "0 (Omitted)"
            md.append(
                f"| `{h.person_id}` | **{h.name}**{c_tag} | {h.relationship_to_deceased} | {h.heir_class} | "
                f"`{h.statutory_fraction_str}` | {h.theoretical_area_sq_m:,.2f} m² | `{rec_str}` | **{h.status}** |"
            )
        md.append("")

        # Structured Discrepancy Matrix Table
        md.append("## 3. Structured Discrepancy Matrix")
        md.append("")
        md.append("| Defect ID | Severity | Title Irregularity & Category | Statutory Ground | Evidence Citation & Bounding Box | Deprived Holding | Recommended Legal Remedy |")
        md.append("| :---: | :---: | :--- | :--- | :--- | :---: | :--- |")

        for d in report.discrepancy_matrix:
            sev_badge = {
                LegalSeverity.CRITICAL: "🔴 `CRITICAL`",
                LegalSeverity.HIGH: "🟠 `HIGH`",
                LegalSeverity.MEDIUM: "🟡 `MEDIUM`",
                LegalSeverity.LOW: "⚪ `LOW`"
            }.get(d.severity, str(d.severity))

            bbox_str = d.bounding_box.to_formatted_str() if d.bounding_box else "N/A"
            shortfall = f"{d.deprived_area_sq_m:,.1f} m²" if d.deprived_area_sq_m else "-"
            statutes = "<br>".join(d.statutory_violations)

            md.append(
                f"| **{d.defect_id}** | {sev_badge} | **{d.title}**<br>*{d.defect_category}* | {statutes} | "
                f"**{d.document_citation}**<br>`bbox: {bbox_str}` | {shortfall} | {d.actionable_remedy} |"
            )
        md.append("")

        # Deep Forensic Defect Narratives
        md.append("## 4. In-Depth Forensic Legal Analysis")
        md.append("")
        for d in report.discrepancy_matrix:
            md.append(f"### [{d.defect_id}] {d.title} (Severity: `{d.severity}`)")
            md.append(f"- **Defect Category**: `{d.defect_category}`")
            md.append(f"- **Statutory Enactments Violated**: {', '.join(d.statutory_violations)}")
            md.append(f"- **Visual Citation & Coordinates**: `{d.document_citation}` | Bounding Box: `{d.bounding_box.to_formatted_str() if d.bounding_box else 'N/A'}`")
            md.append(f"- **Parties Implicated**: `{json.dumps(d.parties_involved)}`")
            md.append(f"- **Substantive Finding**: {d.forensic_narrative}")
            md.append(f"- **Prescribed Judicial Action**: {d.actionable_remedy}")
            md.append("")

        # Sarvam-105B Legal Opinion
        if report.sarvam_105b_legal_opinion:
            md.append("## 5. Sarvam-105B Jurisprudential Opinion")
            md.append("")
            md.append(report.sarvam_105b_legal_opinion)
            md.append("")

        # Recommended Actionable Roadmap
        md.append("## 6. Actionable Legal Roadmap & Litigation Strategy")
        md.append("")
        for step in report.recommended_legal_roadmap:
            md.append(f"{step}")
        md.append("")

        return "\n".join(md)

    def generate_json_report(self, report: DiscrepancyMatrixReport) -> str:
        """Returns structured JSON for programmatic consumption."""
        return report.model_dump_json(indent=2)
