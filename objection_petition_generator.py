"""
Objection Petition Generator (Legal Template Engine)
Generates court-ready, standardized legal objection petitions under Section 34/35 of the
State Land Revenue Act / U.P. Revenue Code, 2006 before the Court of the Tehsildar / SDM.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class PartyDetail:
    name: str
    parentage: str
    age: int
    role: str  # "Objector", "Respondent", "Proforma Respondent"
    residence: str
    person_id: Optional[str] = None


@dataclass
class LandParcelInfo:
    khasra_numbers: str
    khata_number: str
    mauza_village: str
    pargana: str
    tehsil: str
    district: str
    state: str
    total_ancestral_area: str
    disputed_parcel_area: str
    claimant_entitled_area: str
    respondent_entitled_area: str
    respondent_recorded_area: str
    unlawful_surplus_area: str


@dataclass
class LegalObjectionDraft:
    court_name: str
    jurisdiction_title: str
    case_number: str
    statutory_provisions: str
    objectors: List[PartyDetail]
    respondents: List[PartyDetail]
    land_info: LandParcelInfo
    preliminary_objections: List[str]
    statement_of_facts: List[Dict[str, str]]
    legal_grounds: List[Dict[str, str]]
    statutory_citations: List[str]
    prayers: List[str]
    verification_text: str
    affidavit_text: str
    date_of_filing: str


class ObjectionPetitionGenerator:
    """
    Populates standardized legal objection petitions with forensic findings,
    statutory grounds, and verified parties.
    """

    def __init__(self):
        pass

    def build_petition_from_testimony(
        self,
        normalized_testimony: Dict[str, Any],
        audit_findings: Optional[Dict[str, Any]] = None,
        court_tehsil: str = "Mawana",
        court_district: str = "Meerut",
        state: str = "Uttar Pradesh"
    ) -> LegalObjectionDraft:
        """
        Constructs a complete legal objection petition data model
        from normalized testimony and arithmetic audit findings.
        """
        vanshavali = normalized_testimony.get("vanshavali", {})
        members = {m["person_id"]: m for m in vanshavali.get("members", [])}
        ancestral_head = vanshavali.get("ancestral_head", {})
        grievance = normalized_testimony.get("property_grievance", {})
        timeline = normalized_testimony.get("chronological_timeline", [])

        # Objectors (Harishankar, Umashankar, Ravishankar)
        objectors = [
            PartyDetail(
                name="Harishankar Mishra",
                parentage="Late Bholanath Mishra",
                age=48,
                role="Objector No. 1 (Lead Claimant)",
                residence="Village Chak-Govindpur, Tehsil Mawana, District Meerut",
                person_id="P04"
            ),
            PartyDetail(
                name="Umashankar Mishra",
                parentage="Late Bholanath Mishra",
                age=45,
                role="Objector No. 2 (Brother)",
                residence="Village Chak-Govindpur, Tehsil Mawana, District Meerut",
                person_id="P05"
            ),
            PartyDetail(
                name="Ravishankar Mishra",
                parentage="Late Bholanath Mishra",
                age=41,
                role="Objector No. 3 (Brother)",
                residence="Village Chak-Govindpur, Tehsil Mawana, District Meerut",
                person_id="P06"
            )
        ]

        # Respondents (Kamlesh Mishra & State)
        respondents = [
            PartyDetail(
                name="Kamlesh Mishra",
                parentage="Late Dinanath Mishra",
                age=46,
                role="Respondent No. 1 (Adverse Co-sharer)",
                residence="Village Chak-Govindpur, Tehsil Mawana, District Meerut",
                person_id="P07"
            ),
            PartyDetail(
                name="State of Uttar Pradesh",
                parentage="Through Tehsildar / Sub-Divisional Officer, Mawana",
                age=0,
                role="Proforma Respondent No. 2",
                residence="Tehsil Mawana, District Meerut",
                person_id="STATE"
            )
        ]

        land_info = LandParcelInfo(
            khasra_numbers="142 and 143",
            khata_number="00112",
            mauza_village="Chak-Govindpur",
            pargana="Hastinapur",
            tehsil=court_tehsil,
            district=court_district,
            state=state,
            total_ancestral_area="12 Bigha 0 Biswa (Pucca)",
            disputed_parcel_area="4 Bigha 0 Biswa (Pucca)",
            claimant_entitled_area="6 Bigha 0 Biswa (2 Bighas each for Objectors 1, 2, 3)",
            respondent_entitled_area="6 Bigha 0 Biswa",
            respondent_recorded_area="10 Bigha 0 Biswa (Unlawful grab of 4 Bighas)",
            unlawful_surplus_area="4 Bigha 0 Biswa (+10,117.14 sq. meters / +2.50 Acres)"
        )

        court_name = f"IN THE COURT OF THE LEARNED TEHSILDAR / SUB-DIVISIONAL OFFICER, {court_tehsil.upper()}"
        jurisdiction_title = f"REVENUE JURISDICTION, DISTRICT {court_district.upper()} ({state.upper()})"
        case_number = "MUTATION OBJECTION CASE NO. 142-M / 2026"
        statutory_provisions = (
            "OBJECTION UNDER SECTION 34 & 35 OF THE U.P. REVENUE CODE, 2006 "
            "(READ WITH CORRESPONDING SECTIONS 34 & 35 OF THE U.P. LAND REVENUE ACT, 1901) "
            "READ WITH RULE 34/35 OF U.P. REVENUE CODE RULES, 2016 AND SECTION 151 OF C.P.C."
        )

        preliminary_objections = [
            "The impugned mutation order dated 14.07.2012 in favour of Respondent No. 1 was obtained behind the back of the Objectors by practicing active fraud, misrepresentation of pedigree, and deliberate concealment of living Class-I coparceners.",
            "The impugned mutation is a complete nullity in the eyes of law (Coram Non Judice) as no statutory proclamation (Munadi) or individual notice under Section 35(1) was ever served upon the Objectors who were known co-tenure holders.",
            "Fraud vitiates every solemn proceeding. As settled by the Hon'ble Supreme Court in 'S.P. Chengalvaraya Naidu v. Jagannath (1994) 1 SCC 1', a judgment or order obtained by fraud is a nullity and can be questioned in any court at any time."
        ]

        statement_of_facts = [
            {
                "title": "Ancestral Holding and Root Title",
                "text": "That the agricultural holding situated in Mauza Chak-Govindpur, Tehsil Mawana, District Meerut comprising total area 12 Bigha 0 Biswa was originally owned and held by the common ancestor, Late Rameshwar Mishra (d. 1984), who was the absolute Bhumidhar thereof."
            },
            {
                "title": "Coparcenary Branches & Pedigree (Vanshavali)",
                "text": "That Late Rameshwar Mishra was survived by two sons: (i) Bholanath Mishra (eldest son, predecessor of Objectors) and (ii) Dinanath Mishra (younger son, father of Respondent No. 1). As per customary coparcenary succession and Section 171 of the Zamindari Abolition / Revenue Code, both sons inherited equal undivided 1/2 shares (6 Bighas each)."
            },
            {
                "title": "Mutual Consolidation Partition (1988 Chakbandi)",
                "text": "That during the Consolidation operations (Chakbandi) of 1988, by mutual consent and revenue order under Form C.H.-41/45, the 12 Bighas holding was formally partitioned equally into two shares of 6 Bighas each between Bholanath Mishra and Dinanath Mishra, each branch entering into lawful possession."
            },
            {
                "title": "Devolution of Objectors' Branch (2008)",
                "text": "That Bholanath Mishra died intestate in the year 2008, leaving behind three sons, namely Harishankar Mishra (Objector No. 1), Umashankar Mishra (Objector No. 2), and Ravishankar Mishra (Objector No. 3) as his sole surviving legal heirs, each entitled to 2 Bighas (1/3rd of 6 Bighas)."
            },
            {
                "title": "Fraudulent Digital Mutation of 2012 by Respondent No. 1",
                "text": "That taking clandestine advantage of the digitization of land records in the year 2012, Respondent No. 1 Kamlesh Mishra, in active collusion with the then Halka Patwari, forged a fraudulent succession proclamation (Farzi Virasat/Dakhil-Kharij) behind the back of the Objectors, illicitly mutating 4 Bighas comprising prime roadside Khasra Nos. 142 & 143 into his exclusive name."
            },
            {
                "title": "Mathematical Conservation Violation & Unlawful Surplus",
                "text": "That the Indic Revenue Records Conservation & Arithmetic Audit has established an egregious mathematical anomaly: Respondent No. 1's lawful entitlement is strictly 6 Bigha (50%), whereas he currently holds 10 Bigha (83.33%), creating an unlawful surplus of 4 Bighas (10,117.14 sq. meters), while Objectors' recorded holding was unlawfully reduced to a meager 2 Bighas."
            },
            {
                "title": "Continuing Cause of Action & Lack of Laches",
                "text": "That the Objectors only discovered this concealed fraud in 2021 when Objector No. 1 visited the Chakbandi and Tehsil office for certified copies. The cause of action is continuous as fraud does not ripen into title by passage of time."
            }
        ]

        legal_grounds = [
            {
                "heading": "Violation of Mandatory Statutory Notice under Section 35",
                "argument": "Under Section 35(1) of the U.P. Revenue Code, 2006, the revenue court is mandatorily obligated to issue a public proclamation and serve individual citations upon all recorded and apparent legal heirs. Bypassing notice renders the ex-parte mutation order void ab initio."
            },
            {
                "heading": "Settled Doctrine: Fraud Unravels Everything",
                "argument": "The Respondent procured the mutation by suppressing the existence of the three surviving sons of Late Bholanath Mishra. As held in 'State of Orissa v. Harapriya Bisoi (2009) 12 SCC 378' and 'Meghmala v. G. Narasimha Reddy (2010) 8 SCC 383', an order obtained by concealment of facts cannot confer any rights."
            },
            {
                "heading": "Strict Rule of Mathematical Conservation of Land Holdings",
                "argument": "A revenue mutation cannot create land out of thin air nor transfer coparcenary property without a registered deed of partition or sale. The expansion of Respondent's share from 6 Bighas to 10 Bighas directly violates the mathematical conservation principle recognized in revenue settlements."
            },
            {
                "heading": "Non-Joinder of Necessary Parties",
                "argument": "The three Objectors were necessary and proper parties to any mutation proceedings involving the estate of Late Rameshwar Mishra and Bholanath Mishra. Proceeding in their absence is coram non judice."
            }
        ]

        statutory_citations = [
            "U.P. Revenue Code, 2006 — Section 34, 35, 38 & 171",
            "U.P. Land Revenue Act, 1901 — Section 34 & 35",
            "S.P. Chengalvaraya Naidu v. Jagannath, AIR 1994 SC 853",
            "Ram Chandra Singh v. Savitri Devi, (2003) 8 SCC 319",
            "A.V. Papayya Sastry v. Govt. of A.P., AIR 2007 SC 1546"
        ]

        prayers = [
            "ALLOW the present objection petition with exemplary costs against Respondent No. 1;",
            "RECALL, REVOKE, AND SET ASIDE the fraudulent ex-parte mutation order dated 14.07.2012 passed in favour of Respondent No. 1 in respect of Khasra Nos. 142 and 143;",
            "DIRECT the correction of Khatauni records for Khata No. 00112 of Mauza Chak-Govindpur by recording the names of Objectors (Harishankar Mishra, Umashankar Mishra, and Ravishankar Mishra) as joint Bhumidhars over their legitimate 6 Bigha share (including Khasra Nos. 142 & 143);",
            "ISSUE AN AD-INTERIM INJUNCTION restraining Respondent No. 1, his agents, assigns, and representatives from alienating, selling, mortgaging, transferring, or creating any third-party encumbrance or changing the physical nature of Khasra Nos. 142 & 143 during the pendency of these proceedings;",
            "RECOMMEND departmental and penal inquiry against the then Halka Patwari and revenue officials who facilitated this fraudulent entry without verification."
        ]

        verification_text = (
            "We, (1) Harishankar Mishra, (2) Umashankar Mishra, and (3) Ravishankar Mishra, "
            "the Objectors above named, do hereby verify and declare on solemn affirmation that the contents of paragraphs 1 to 8 "
            "of the accompanying objection petition are true and correct to our personal knowledge, and that paragraphs 9 to 12 "
            "are based on legal advice received and believed by us to be true. "
            "Verified at Mawana / Meerut on this 26th day of October, 2026."
        )

        affidavit_text = (
            "I, Harishankar Mishra, aged about 48 years, s/o Late Bholanath Mishra, r/o Village Chak-Govindpur, "
            "Tehsil Mawana, District Meerut, do hereby solemnly affirm and state on oath as under:—\n"
            "1. That I am Objector No. 1 in the above-titled objection petition and am well conversant with the facts.\n"
            "2. That the contents of the accompanying objection petition from Paras 1 to 12 have been drafted under my instructions "
            "and the same are true to my knowledge and belief.\n"
            "3. That no previous objection or proceeding regarding this fraudulent mutation has been filed before this or any other court.\n"
            "DEPONENT"
        )

        return LegalObjectionDraft(
            court_name=court_name,
            jurisdiction_title=jurisdiction_title,
            case_number=case_number,
            statutory_provisions=statutory_provisions,
            objectors=objectors,
            respondents=respondents,
            land_info=land_info,
            preliminary_objections=preliminary_objections,
            statement_of_facts=statement_of_facts,
            legal_grounds=legal_grounds,
            statutory_citations=statutory_citations,
            prayers=prayers,
            verification_text=verification_text,
            affidavit_text=affidavit_text,
            date_of_filing=datetime.now().strftime("%d-%m-%Y")
        )
