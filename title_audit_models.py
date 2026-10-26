"""
Title Audit & Discrepancy Matrix Models for Step 4.
Defines schemas for:
- Official Land Records (Jamabandi, Khatauni, RoR)
- Mutation History (Intiqal Register entries)
- Line Items & Document Visual Bounding Boxes
- Statutory Succession Calculations
- Structured Discrepancy Matrix & Forensic Legal Defects
"""

from enum import Enum
from fractions import Fraction
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized coordinates [ymin, xmin, ymax, xmax] in range 0-1000 or 0.0-1.0."""
    ymin: float = Field(..., description="Top boundary coordinate")
    xmin: float = Field(..., description="Left boundary coordinate")
    ymax: float = Field(..., description="Bottom boundary coordinate")
    xmax: float = Field(..., description="Right boundary coordinate")

    def to_tuple(self) -> tuple:
        return (self.ymin, self.xmin, self.ymax, self.xmax)

    def to_formatted_str(self) -> str:
        return f"[{self.ymin:.1f}, {self.xmin:.1f}, {self.ymax:.1f}, {self.xmax:.1f}]"


class DocumentLineItem(BaseModel):
    """Pinpoints the exact visual/textual evidence in official records."""
    doc_id: str = Field(..., description="Document ID or register reference (e.g. JAM-1998, INT-452)")
    doc_type: str = Field(..., description="Document type: Jamabandi, Khatauni, Intiqal/Mutation, Sale Deed, Haq-Tyag Deed")
    page_no: Optional[int] = Field(None, description="Page number of the document")
    khasra_no: Optional[str] = Field(None, description="Khasra / Survey number")
    khata_khewat_no: Optional[str] = Field(None, description="Khata or Khewat number")
    column_name: Optional[str] = Field(None, description="Column in revenue register (e.g. Col 4 Owner, Col 8 Mutation Order)")
    line_text: str = Field(..., description="Verbatim or extracted textual line item")
    bounding_box: Optional[BoundingBox] = Field(None, description="Visual bounding box of the line item on the scanned page")


class RecordedCoSharer(BaseModel):
    """Individual co-sharer recorded in the official RoR/Jamabandi/Khatauni."""
    name: str = Field(..., description="Full recorded name of co-sharer")
    parentage: Optional[str] = Field(None, description="Father or husband name recorded in title")
    share_raw: Optional[str] = Field(None, description="Raw recorded share (e.g., '1/3', '4 Annas', '0.25')")
    share_fraction: Optional[str] = Field(None, description="Normalized fractional share (e.g. '1/3')")
    recorded_area_raw: Optional[str] = Field(None, description="Raw recorded area if specified (e.g. '2 Bigha 10 Biswa')")
    recorded_area_sq_m: Optional[float] = Field(None, description="Normalized area in square meters")
    is_minor: bool = Field(default=False, description="Whether marked as minor (nabaligh) in records")
    guardian_name: Optional[str] = Field(None, description="Name of recorded guardian (wali/sarparast)")
    line_item: Optional[DocumentLineItem] = Field(None, description="Exact line item reference")


class LandRecordDocument(BaseModel):
    """Official extracted land title document (Jamabandi / Khatauni / RoR)."""
    doc_id: str = Field(..., description="Document reference code")
    doc_type: str = Field(default="Jamabandi", description="Jamabandi, Khatauni, or RoR")
    fasli_year_or_period: str = Field(..., description="Fasli year or settlement year (e.g., '1998-1999', '1425 Fasli')")
    state: str = Field(..., description="State jurisdiction (e.g., 'Uttar Pradesh', 'Punjab', 'Rajasthan')")
    district: str = Field(..., description="District jurisdiction")
    tehsil: str = Field(..., description="Tehsil / Taluk jurisdiction")
    village: str = Field(..., description="Village / Mauza name")
    khasra_numbers: List[str] = Field(default_factory=list, description="Khasra/Survey numbers comprising the holding")
    khata_khewat_no: Optional[str] = Field(None, description="Khatauni / Khewat number")
    total_area_raw: str = Field(..., description="Total parcel area as stated in record")
    total_area_sq_m: float = Field(..., description="Normalized total parcel area in square meters")
    co_sharers: List[RecordedCoSharer] = Field(default_factory=list, description="List of recorded titleholders")
    remarks: Optional[str] = Field(None, description="Additional revenue remarks or endorsements")


class MutationType(str, Enum):
    INHERITANCE_FAUTI = "INHERITANCE_FAUTI"       # Warisana / Fauti Intiqal (Devolution on death)
    SALE_TRANSFER = "SALE_TRANSFER"               # Bai / Sale Deed conveyance
    PARTITION_TAQSEEM = "PARTITION_TAQSEEM"       # Taqseem / Family or court partition
    GIFT_HIBA = "GIFT_HIBA"                       # Hiba / Gift deed transfer
    RELEASE_HAQ_TYAG = "RELEASE_HAQ_TYAG"         # Haq-Tyag / Relinquishment deed
    MORTGAGE_RAHAN = "MORTGAGE_RAHAN"             # Rahan / Mortgage entry
    OTHER = "OTHER"


class MutationRecord(BaseModel):
    """Official extracted Mutation entry (Intiqal / Dakhil-Kharij)."""
    mutation_no: str = Field(..., description="Mutation entry number (Intiqal number)")
    mutation_date_or_year: str = Field(..., description="Date or year mutation was entered or sanctioned")
    mutation_type: MutationType = Field(..., description="Categorization of the mutation")
    deceased_predecessor: Optional[str] = Field(None, description="Name of deceased ancestor whose estate devolved")
    transferor_names: List[str] = Field(default_factory=list, description="Names of alienating parties / transferors")
    transferee_names: List[str] = Field(default_factory=list, description="Names of acquiring parties / successors")
    share_transferred_raw: Optional[str] = Field(None, description="Fraction or share transferred")
    area_transferred_raw: Optional[str] = Field(None, description="Raw area transferred (e.g. '4 Bigha 0 Biswa')")
    area_transferred_sq_m: Optional[float] = Field(None, description="Normalized area transferred in sq meters")
    
    # Red Flag Check Attributes
    has_registered_haq_tyag: bool = Field(
        default=False, 
        description="Whether a registered relinquishment deed is cited for excluded legal heirs"
    )
    haq_tyag_deed_ref: Optional[str] = Field(
        None, 
        description="Registered deed number, bahi number, date, and sub-registrar office details if any"
    )
    minor_heirs_involved: bool = Field(
        default=False, 
        description="Whether any affected co-sharer / heir was a minor at time of mutation"
    )
    minor_names: List[str] = Field(default_factory=list, description="Names of minors involved")
    guardian_represented: bool = Field(
        default=True, 
        description="Whether a legal guardian was officially appointed and represented the minor"
    )
    guardian_details: Optional[str] = Field(None, description="Guardian identity and legal capacity")
    district_court_permission_sec8: bool = Field(
        default=False, 
        description="Whether District Court permission was obtained under Sec 8 HMGA 1956 for minor's alienation"
    )
    is_will_based: bool = Field(default=False, description="Whether mutation was sanctioned based on a testamentary will")
    is_will_registered_and_probated: bool = Field(
        default=False, 
        description="Whether the cited will was registered with Sub-Registrar and/or probated"
    )
    sanctioning_authority: Optional[str] = Field(
        None, 
        description="Officer sanctioning mutation (e.g., Tehsildar, AC 1st Grade, Naib Tehsildar)"
    )
    status: str = Field(default="Sanctioned", description="Sanctioned, Contested, Cancelled, or Pending")
    line_item: Optional[DocumentLineItem] = Field(None, description="Reference line item in mutation register")
    bounding_box: Optional[BoundingBox] = Field(None, description="Visual bounding box on mutation register page")
    notes: Optional[str] = Field(None, description="Patwari or Tehsildar endorsements")


class DefectCategory(str, Enum):
    OMITTED_LEGAL_HEIR_NO_HAQ_TYAG = "OMITTED_LEGAL_HEIR_NO_HAQ_TYAG"
    UNREPRESENTED_MINOR_MUTATION = "UNREPRESENTED_MINOR_MUTATION"
    EXCESS_AREA_CONVEYANCE = "EXCESS_AREA_CONVEYANCE"
    UNAUTHORIZED_TESTAMENTARY_EXCLUSION = "UNAUTHORIZED_TESTAMENTARY_EXCLUSION"
    ARITHMETIC_SURPLUS_INFLATION = "ARITHMETIC_SURPLUS_INFLATION"
    CO_SHARER_FRACTIONAL_DILUTION = "CO_SHARER_FRACTIONAL_DILUTION"
    TESTIMONY_TITLE_DISCREPANCY = "TESTIMONY_TITLE_DISCREPANCY"


class LegalSeverity(str, Enum):
    CRITICAL = "Critical"  # Title defect void ab initio, invalidates chain of title or causes total dispossession
    HIGH = "High"          # Substantive statutory defect, voidable mutation, actionable in revenue/civil court
    MEDIUM = "Medium"      # Procedural defect or unverified conveyance requiring rectification
    LOW = "Low"            # Minor clerical or name variation requiring routine correction


class StatutoryHeirShare(BaseModel):
    """Calculated theoretical lawful entitlement under succession statutes."""
    person_id: str = Field(..., description="ID matching PersonNode in family tree")
    name: str = Field(..., description="Name of the legal heir")
    relationship_to_deceased: str = Field(..., description="Kinship relation (e.g. Daughter, Son, Widow, Mother)")
    heir_class: str = Field(default="Class I", description="Statutory class: Class I, Class II, Coparcener")
    statutory_fraction_str: str = Field(..., description="Theoretical share fraction (e.g. '1/4', '1/6')")
    statutory_fraction_val: float = Field(..., description="Decimal representation of statutory fraction")
    theoretical_area_sq_m: float = Field(..., description="Theoretical area entitlement in sq meters")
    theoretical_area_acres: float = Field(..., description="Theoretical area in acres")
    recorded_share_fraction_str: Optional[str] = Field(None, description="Actual share found on land record")
    recorded_share_fraction_val: float = Field(default=0.0, description="Decimal of recorded share")
    recorded_area_sq_m: float = Field(default=0.0, description="Actual recorded area in sq meters")
    deprived_fraction_str: Optional[str] = Field(None, description="Shortfall fraction: Theoretical - Recorded")
    deprived_area_sq_m: float = Field(default=0.0, description="Shortfall in sq meters")
    is_claimant: bool = Field(default=False, description="Whether this is the claimant")
    status: str = Field(..., description="Entitled, Dispossessed, Omitted, Diluted, or Fully Accorded")


class DiscrepancyItem(BaseModel):
    """Specific line-item defect identified in the title audit discrepancy matrix."""
    defect_id: str = Field(..., description="Unique defect identifier (e.g., DEF-001, DEF-002)")
    title: str = Field(..., description="Brief title of the irregularity")
    defect_category: DefectCategory = Field(..., description="Standardized classification of title defect")
    severity: LegalSeverity = Field(..., description="Legal severity rating: Critical, High, Medium, Low")
    statutory_violations: List[str] = Field(
        ..., 
        description="Exact statutes violated (e.g., Hindu Succession Act 1956 Sec 6 & 8, Registration Act 1908 Sec 17, HMGA 1956 Sec 8)"
    )
    parties_involved: Dict[str, Any] = Field(
        ..., 
        description="Parties implicated (claimant, omitted heirs, defaulting transferors, beneficiaries)"
    )
    theoretical_share_str: Optional[str] = Field(None, description="Claimant or lawful heir's theoretical share")
    recorded_share_str: Optional[str] = Field(None, description="Recorded share in challenged document")
    deprived_share_str: Optional[str] = Field(None, description="Shortfall or illegal dilution fraction")
    deprived_area_sq_m: Optional[float] = Field(None, description="Area shortfall in sq meters")
    deprived_area_acres: Optional[float] = Field(None, description="Area shortfall in acres")
    document_citation: str = Field(..., description="Precise document name, mutation number, page, line item")
    bounding_box: Optional[BoundingBox] = Field(None, description="Document visual coordinates [ymin, xmin, ymax, xmax]")
    forensic_narrative: str = Field(..., description="Detailed factual and legal narrative of how the clash occurs")
    actionable_remedy: str = Field(..., description="Recommended legal proceeding, statute, and judicial forum")


class DiscrepancyMatrixReport(BaseModel):
    """Complete Title Audit & Discrepancy Matrix Output Report."""
    audit_id: str = Field(..., description="Unique Title Audit reference ID")
    timestamp: str = Field(..., description="Timestamp of title audit execution")
    engine_version: str = Field(default="Sarvam-105B Title Audit Engine v1.0", description="Audit engine version")
    jurisdiction: Dict[str, str] = Field(..., description="State, district, tehsil, and village")
    khasra_numbers: List[str] = Field(default_factory=list, description="Khasra parcels audited")
    total_plot_area_raw: str = Field(..., description="Total parcel area as stated")
    total_plot_area_sq_m: float = Field(..., description="Total area in square meters")
    claimant_id: Optional[str] = Field(None, description="Claimant person ID")
    claimant_name: Optional[str] = Field(None, description="Claimant name")
    claimant_theoretical_share: Optional[str] = Field(None, description="Lawful share under statutory succession")
    claimant_recorded_share: Optional[str] = Field(None, description="Recorded share on revenue records")
    claimant_deprived_area_sq_m: float = Field(default=0.0, description="Total area claimant was deprived of")
    claimant_deprived_area_acres: float = Field(default=0.0, description="Total area in acres claimant was deprived of")
    statutory_heir_shares: List[StatutoryHeirShare] = Field(default_factory=list, description="Theoretical vs actual shares of all heirs")
    discrepancy_matrix: List[DiscrepancyItem] = Field(default_factory=list, description="List of all detected title defects")
    overall_title_risk: str = Field(..., description="CRITICAL_TITLE_DEFECT, HIGH_RISK_TITLE, MEDIUM_RISK, or CLEAR_TITLE")
    summary_verdict: str = Field(..., description="Summary legal verdict")
    sarvam_105b_legal_opinion: Optional[str] = Field(None, description="In-depth jurisprudential opinion from Sarvam-105B")
    recommended_legal_roadmap: List[str] = Field(default_factory=list, description="Prioritized roadmap of legal actions")
