"""
Pydantic Schemas for Land Deed Verification & Ingestion
Covers Deed Metadata, Tabular Ownership Shares, and Visual Authenticity Markers.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate in pixels")
    y: int = Field(..., description="Top-left Y coordinate in pixels")
    width: int = Field(..., description="Width of bounding box in pixels")
    height: int = Field(..., description="Height of bounding box in pixels")


class VisualArtifact(BaseModel):
    id: str = Field(..., description="Unique artifact identifier")
    type: str = Field(..., description="Type of visual artifact (revenue_stamp, signature, marginal_remark)")
    bounding_box: BoundingBox = Field(..., description="Bounding box on document")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    label: str = Field(..., description="Specific label e.g., 'Official Revenue Stamp', 'Tehsildar Signature'")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional detected attributes (e.g., ink color, circularity)")


class VisualVerificationReport(BaseModel):
    mandatory_stamps_present: bool = Field(..., description="True if required revenue/official stamps are detected")
    signatures_present: bool = Field(..., description="True if required signatures (Tehsildar/Patwari/Officer) are detected")
    kaifiyat_present: bool = Field(..., description="True if marginal remarks (Kaifiyat) are found")
    authenticity_status: str = Field(..., description="VERIFIED, FLAGGED_SUSPICIOUS, or INCOMPLETE")
    authenticity_score: float = Field(..., description="Overall document authenticity score (0.0 to 1.0)")
    revenue_stamps: List[VisualArtifact] = Field(default_factory=list, description="Detected official stamps")
    signatures: List[VisualArtifact] = Field(default_factory=list, description="Detected signatures")
    marginal_remarks: List[VisualArtifact] = Field(default_factory=list, description="Detected marginal remark regions (Kaifiyat)")


class PlotArea(BaseModel):
    stated_value: float = Field(..., description="Stated numeric value of plot area")
    stated_unit: str = Field(..., description="Unit as stated in document (e.g., Bigha, Katha, Hectare, Acre, Biswa)")
    standardized_sq_meters: Optional[float] = Field(None, description="Normalized area converted to Square Meters")
    standardized_hectares: Optional[float] = Field(None, description="Normalized area converted to Hectares")


class TenureHolder(BaseModel):
    holder_name: str = Field(..., description="Name of the recorded tenure holder / owner (खातेदार का नाम)")
    relation_type: Optional[str] = Field(None, description="Father / Husband / Guardian (पिता/पति)")
    relation_name: Optional[str] = Field(None, description="Name of relative/father/husband")
    share_fraction: Optional[str] = Field(None, description="Share in fractional notation e.g., 1/2, 1/4, 4 aana")
    share_percentage: float = Field(..., description="Ownership share percentage (0.0 to 100.0%)")
    allocated_area: Optional[str] = Field(None, description="Proportional area allocated to this holder")
    status: Optional[str] = Field("Recorded Owner", description="Tenancy status e.g., Sankramaniya Bhumidhar, Co-owner")


class LandParcelDetails(BaseModel):
    khasra_numbers: List[str] = Field(default_factory=list, description="List of Khasra / Survey / Plot numbers (खसरा संख्या)")
    khata_number: Optional[str] = Field(None, description="Khata / Account number (खाता संख्या)")
    khatoni_number: Optional[str] = Field(None, description="Khatoni / Ledger number (खतौनी संख्या)")
    plot_area: PlotArea = Field(..., description="Total plot area and units")
    land_type: Optional[str] = Field("Agricultural", description="Classification of land (e.g. Agricultural, Abadi, Commercial)")
    boundaries: Optional[Dict[str, str]] = Field(None, description="Chauhaddi / 4 boundaries (North, South, East, West)")


class GeographicJurisdiction(BaseModel):
    state: Optional[str] = Field(None, description="State (राज्य)")
    district: Optional[str] = Field(None, description="District (ज़िला)")
    tehsil: Optional[str] = Field(None, description="Tehsil / Taluk (तहसील)")
    pargana: Optional[str] = Field(None, description="Pargana (परगना)")
    village_mauza: Optional[str] = Field(None, description="Village / Mauza (ग्राम/मौज़ा)")
    patwar_circle: Optional[str] = Field(None, description="Patwar Circle / Halka (पटवार हल्का)")


class DeedMetadata(BaseModel):
    deed_type: str = Field(..., description="Type of document (e.g., Khatauni, Sale Deed, Jamabandi, Patta, Gift Deed)")
    deed_number: Optional[str] = Field(None, description="Deed / Document / Registration number")
    execution_date: Optional[str] = Field(None, description="Date of document execution or issuance")
    registration_date: Optional[str] = Field(None, description="Date of official registration")
    sub_registrar_office: Optional[str] = Field(None, description="Sub-Registrar Office (SRO) / Revenue Authority")
    geographic_jurisdiction: GeographicJurisdiction = Field(..., description="Jurisdiction details")
    land_parcel_details: LandParcelDetails = Field(..., description="Land parcel identifiers and metrics")
    marginal_remarks_kaifiyat_text: Optional[str] = Field(None, description="Transcribed marginal remarks / Kaifiyat text")


class DocumentVerificationSummary(BaseModel):
    document_name: str
    document_type: str
    processed_at: str
    authenticity_status: str
    mandatory_stamps_present: bool
    signatures_present: bool
    kaifiyat_present: bool
    confidence_scores: Dict[str, float]
    verification_notes: List[str] = Field(default_factory=list)


class LandDeedVerificationOutput(BaseModel):
    """
    Final Expected Output:
    A structured JSON object containing parsed deed metadata, ownership shares,
    and a flag indicating whether mandatory stamps or signatures are present.
    """
    document_verification_summary: DocumentVerificationSummary
    visual_authenticity_markers: VisualVerificationReport
    parsed_deed_metadata: DeedMetadata
    ownership_shares: List[TenureHolder]
    raw_extracted_text_preview: Optional[str] = None
