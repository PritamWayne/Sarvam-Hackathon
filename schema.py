"""
Normalized Schema Models for Step 2: Oral Testimony Parsing & Normalization
Captures:
- Named Entities (Ancestral head, descendants, living relatives, claimant)
- Vanshavali (Family Tree with nodes, relationship edges, date markers)
- Stated Succession Order
- Property Grievance Alleged by Claimant
- Chronological Timeline Markers
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PersonNode(BaseModel):
    person_id: str = Field(..., description="Unique identifier for the individual (e.g., P01, P02)")
    name: str = Field(..., description="Name or recognized title in oral testimony")
    aliases: List[str] = Field(default_factory=list, description="Alternative names, nicknames or regional honorifics")
    gender: Literal["male", "female", "other", "unknown"] = Field(..., description="Gender of the individual")
    status: Literal["alive", "deceased", "unknown"] = Field(..., description="Vital status as stated in testimony")
    generation_level: int = Field(..., description="Generation level relative to ancestral head (0 = Ancestral Head, 1 = Children, etc.)")
    date_marker: Optional[str] = Field(None, description="Known approximate birth/death period or temporal anchor (e.g., 'd. circa 1995')")
    is_claimant: bool = Field(default=False, description="Whether this individual is the claimant giving the testimony")
    is_ancestral_head: bool = Field(default=False, description="Whether this individual is the root ancestral head (Karta/Patriarch)")


class RelationshipEdge(BaseModel):
    source_id: str = Field(..., description="Source person ID (e.g., parent, older sibling, spouse)")
    target_id: str = Field(..., description="Target person ID")
    relation_type: Literal[
        "parent_of", 
        "child_of", 
        "spouse_of", 
        "sibling_of", 
        "half_sibling_of", 
        "adopted_child_of"
    ] = Field(..., description="Standardized kinship relationship type")
    notes: Optional[str] = Field(None, description="Contextual note (e.g., 'eldest son', 'second wife')")


class VanshavaliTree(BaseModel):
    ancestral_head: PersonNode = Field(..., description="Root ancestor / original titleholder of the property")
    members: List[PersonNode] = Field(..., description="All named individuals identified in the lineage")
    relationships: List[RelationshipEdge] = Field(..., description="Kinship edges linking family members")


class SuccessionStep(BaseModel):
    step_order: int = Field(..., description="Order of devolution/succession (1, 2, 3...)")
    from_person_id: str = Field(..., description="Deceased predecessor person ID")
    to_person_ids: List[str] = Field(..., description="Successor/heir person IDs entitled under stated custom or law")
    basis_of_succession: str = Field(..., description="Customary inheritance, coparcenary share, oral partition, or testamentary will")
    approximate_year_or_era: Optional[str] = Field(None, description="Date marker or landmark event (e.g. '1982 Chakbandi', '2004')")
    contested: bool = Field(default=False, description="Whether this succession step is disputed or accepted by all branches")


class PropertyGrievance(BaseModel):
    disputed_asset_description: str = Field(..., description="Description of the disputed ancestral land, ancestral home, khasra/survey numbers")
    location_details: Optional[str] = Field(None, description="Village, Mauza, Tehsil/Taluka, District if mentioned in testimony")
    claimed_share: Optional[str] = Field(None, description="Proportion or parcel claimed (e.g. '1/3rd share', '4 bighas in eastern plot')")
    adverse_party_ids: List[str] = Field(default_factory=list, description="IDs of family members or external parties alleged to have committed the wrong")
    allegation_category: Literal[
        "fraudulent_mutation",
        "encroachment",
        "unauthorized_sale",
        "exclusion_from_partition",
        "denial_of_share",
        "forged_gift_or_will",
        "other"
    ] = Field(..., description="Categorization of the legal/property grievance")
    grievance_narrative: str = Field(..., description="Detailed description of the alleged illicit act or dispute")
    relief_sought: str = Field(..., description="What the claimant is demanding (e.g., revenue mutation correction, physical demarcation, share restoration)")


class ChronologicalEvent(BaseModel):
    event_order: int = Field(..., description="Sequential chronological position")
    temporal_anchor: str = Field(..., description="Stated date, year, or landmark (e.g. '1975 floods', 'father's demise in 1998')")
    description: str = Field(..., description="Summary of the historical/legal event")
    actors_involved: List[str] = Field(default_factory=list, description="Names or IDs of persons involved")


class OralTestimonyNormalizedSchema(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Schema specification version")
    testimony_metadata: dict = Field(default_factory=dict, description="Metadata regarding audio input, duration, language, and STT model")
    verbatim_transcript: str = Field(..., description="Full verbatim transcript returned by Saaras speech-to-text")
    summary_of_statement: str = Field(..., description="High-level summary of claimant's oral testimony")
    vanshavali: VanshavaliTree = Field(..., description="Reconstructed family tree hierarchy and kinship graph")
    stated_succession_order: List[SuccessionStep] = Field(..., description="Stated generational succession and inheritance progression")
    property_grievance: PropertyGrievance = Field(..., description="The specific property claim and grievance alleged")
    chronological_timeline: List[ChronologicalEvent] = Field(default_factory=list, description="Chronological timeline of landmark family events")
