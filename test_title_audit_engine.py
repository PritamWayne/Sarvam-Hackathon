"""
Comprehensive Test Suite for Step 4: Discrepancy & Title Audit Engine (Sarvam-105B).
Verifies:
1. Reconstructed family tree mapping against official land records.
2. Statutory succession rule execution (Class I legal heirs, HSA 1956 & 2005 Amendment).
3. Red Flag 1: Legal heir omitted without registered relinquishment deed (Haq-Tyag).
4. Red Flag 2: Mutation recorded during minority of an heir without guardian representation.
5. Red Flag 3: Area transferred exceeding transferor's recorded share.
6. Structured discrepancy matrix generation with severity, exact line items, and bounding boxes.
7. Sarvam-105B intelligence integration & reporting in Markdown and JSON.
"""

from fractions import Fraction
import json
import unittest

from schema import PersonNode, RelationshipEdge, VanshavaliTree
from title_audit_models import (
    LandRecordDocument,
    RecordedCoSharer,
    MutationRecord,
    MutationType,
    BoundingBox,
    DocumentLineItem,
    LegalSeverity,
    DefectCategory,
)
from title_audit_engine import TitleAuditEngine


class TestTitleAuditEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TitleAuditEngine(state="Uttar Pradesh", district="Meerut", tehsil="Mawana")

        # -------------------------------------------------------------
        # Reconstruct Standard 3-Generation Vanshavali
        # Gen 0: Late Ram Lal (Ancestral Head, deceased)
        # Gen 1:
        #   - Suresh Kumar (Son, deceased 2012)
        #   - Ramesh Kumar (Son, alive - Adverse uncle)
        #   - Kamla Devi (Daughter, alive - Omitted sister)
        # Gen 2:
        #   - Amit Kumar (Claimant, Son of Suresh Kumar, born 2002, minor in 2014)
        #   - Sunita Kumari (Daughter of Suresh Kumar, alive)
        #   - Shanti Devi (Widow of Suresh Kumar, alive)
        # -------------------------------------------------------------
        self.ancestral_head = PersonNode(
            person_id="P01",
            name="Ram Lal",
            aliases=["Late Ram Lal", "Ram Lal Sharma"],
            gender="male",
            status="deceased",
            generation_level=0,
            date_marker="Demised 1995",
            is_claimant=False,
            is_ancestral_head=True
        )

        self.members = [
            self.ancestral_head,
            PersonNode(
                person_id="P02",
                name="Suresh Kumar",
                aliases=["Suresh Chand"],
                gender="male",
                status="deceased",
                generation_level=1,
                date_marker="Demised 2012",
                is_claimant=False,
                is_ancestral_head=False
            ),
            PersonNode(
                person_id="P03",
                name="Ramesh Kumar",
                aliases=["Ramesh Chand"],
                gender="male",
                status="alive",
                generation_level=1,
                date_marker="b. 1968",
                is_claimant=False,
                is_ancestral_head=False
            ),
            PersonNode(
                person_id="P04",
                name="Kamla Devi",
                aliases=["Kamlesh Devi"],
                gender="female",
                status="alive",
                generation_level=1,
                date_marker="b. 1972",
                is_claimant=False,
                is_ancestral_head=False
            ),
            PersonNode(
                person_id="P05",
                name="Shanti Devi",
                aliases=["Smt. Shanti Devi"],
                gender="female",
                status="alive",
                generation_level=1,
                date_marker="Widow of Suresh",
                is_claimant=False,
                is_ancestral_head=False
            ),
            PersonNode(
                person_id="P06",
                name="Amit Kumar",
                aliases=["Amit Sharma"],
                gender="male",
                status="alive",
                generation_level=2,
                date_marker="b. 2002 (Age 12 in 2014)",
                is_claimant=True,
                is_ancestral_head=False
            ),
            PersonNode(
                person_id="P07",
                name="Sunita Kumari",
                aliases=["Sunita"],
                gender="female",
                status="alive",
                generation_level=2,
                date_marker="b. 2004",
                is_claimant=False,
                is_ancestral_head=False
            )
        ]

        self.relationships = [
            RelationshipEdge(source_id="P01", target_id="P02", relation_type="parent_of"),
            RelationshipEdge(source_id="P01", target_id="P03", relation_type="parent_of"),
            RelationshipEdge(source_id="P01", target_id="P04", relation_type="parent_of"),
            RelationshipEdge(source_id="P02", target_id="P05", relation_type="spouse_of"),
            RelationshipEdge(source_id="P02", target_id="P06", relation_type="parent_of"),
            RelationshipEdge(source_id="P02", target_id="P07", relation_type="parent_of")
        ]

        self.vanshavali = VanshavaliTree(
            ancestral_head=self.ancestral_head,
            members=self.members,
            relationships=self.relationships
        )

        # Baseline Land Parcel: 12 Bighas (12 * 2529.285 = 30,351.42 m² in Pucca Bigha)
        self.total_area_sq_m = 30351.42
        self.total_area_raw = "12 Bigha 0 Biswa"

    def test_statutory_succession_shares(self):
        """Test calculation of theoretical lawful shares under Hindu Succession Act."""
        shares = self.engine.succession_engine.compute_succession_shares(
            self.vanshavali, self.total_area_sq_m
        )

        shares_by_id = {s.person_id: s for s in shares}

        # 1. Gen 0 Ram Lal (deceased) had 3 children: Suresh, Ramesh, Kamla
        # Under HSA (amended 2005 & Vineeta Sharma), each of the 3 branches takes 1/3 share:
        # - Ramesh Kumar (alive): 1/3
        # - Kamla Devi (alive daughter): 1/3
        # - Suresh Kumar (deceased): 1/3 devolves equally to his Class I heirs:
        #   Widow Shanti Devi (1/3 of 1/3 = 1/9)
        #   Son Amit Kumar (Claimant) (1/3 of 1/3 = 1/9)
        #   Daughter Sunita Kumari (1/3 of 1/3 = 1/9)

        self.assertEqual(shares_by_id["P03"].statutory_fraction_str, "1/3")
        self.assertEqual(shares_by_id["P04"].statutory_fraction_str, "1/3")
        self.assertEqual(shares_by_id["P05"].statutory_fraction_str, "1/9")
        self.assertEqual(shares_by_id["P06"].statutory_fraction_str, "1/9")
        self.assertEqual(shares_by_id["P07"].statutory_fraction_str, "1/9")

        # Sum of living shares must equal 1/1 (100%)
        living_sum = (
            Fraction(shares_by_id["P03"].statutory_fraction_str) +
            Fraction(shares_by_id["P04"].statutory_fraction_str) +
            Fraction(shares_by_id["P05"].statutory_fraction_str) +
            Fraction(shares_by_id["P06"].statutory_fraction_str) +
            Fraction(shares_by_id["P07"].statutory_fraction_str)
        )
        self.assertEqual(living_sum, Fraction(1, 1))

        # Check Claimant Amit Kumar's share
        claimant_share = shares_by_id["P06"]
        self.assertTrue(claimant_share.is_claimant)
        expected_claimant_sq_m = self.total_area_sq_m / 9.0
        self.assertAlmostEqual(claimant_share.theoretical_area_sq_m, expected_claimant_sq_m, places=1)

    def test_red_flag_omitted_heir_without_haq_tyag(self):
        """Test detection of legal heir omitted from mutation without registered Haq-Tyag deed."""
        # Mutation 1: Fauti Intiqal after Ram Lal's death in 1996
        # Only sons Suresh and Ramesh were mutated; daughter Kamla Devi was omitted without Haq-Tyag!
        mut_1 = MutationRecord(
            mutation_no="INT-204",
            mutation_date_or_year="1996-05-14",
            mutation_type=MutationType.INHERITANCE_FAUTI,
            deceased_predecessor="Ram Lal",
            transferor_names=["Ram Lal (Deceased)"],
            transferee_names=["Suresh Kumar", "Ramesh Kumar"],  # Kamla Devi omitted!
            share_transferred_raw="1/2 each",
            has_registered_haq_tyag=False,                      # No registered relinquishment deed!
            haq_tyag_deed_ref=None,
            sanctioning_authority="Naib Tehsildar Mawana",
            bounding_box=BoundingBox(ymin=110.0, xmin=40.0, ymax=180.0, xmax=520.0),
            notes="Oral family arrangement recorded; no registered release deed produced."
        )

        # Official Jamabandi
        jamabandi = LandRecordDocument(
            doc_id="JAM-1425F",
            doc_type="Jamabandi / Khatauni",
            fasli_year_or_period="1425 Fasli (2018)",
            state="Uttar Pradesh",
            district="Meerut",
            tehsil="Mawana",
            village="Hastinapur",
            khasra_numbers=["452/1", "452/2"],
            khata_khewat_no="Khata 84",
            total_area_raw="12 Bigha 0 Biswa",
            total_area_sq_m=self.total_area_sq_m,
            co_sharers=[
                RecordedCoSharer(
                    name="Ramesh Kumar",
                    share_raw="1/2",
                    share_fraction="1/2",
                    recorded_area_sq_m=self.total_area_sq_m * 0.5
                ),
                RecordedCoSharer(
                    name="Suresh Kumar",
                    share_raw="1/2",
                    share_fraction="1/2",
                    recorded_area_sq_m=self.total_area_sq_m * 0.5
                )
            ]
        )

        report = self.engine.audit_title(
            vanshavali=self.vanshavali,
            land_record=jamabandi,
            mutations=[mut_1]
        )

        # Verify defect detected
        omission_defects = [
            d for d in report.discrepancy_matrix
            if d.defect_category == DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG
        ]
        self.assertTrue(len(omission_defects) >= 1)
        kamla_defect = next(d for d in omission_defects if "Kamla Devi" in d.title)
        self.assertEqual(kamla_defect.severity, LegalSeverity.HIGH)
        self.assertIn("Registration Act 1908, Section 17(1)(b)", kamla_defect.statutory_violations[1])
        self.assertIsNotNone(kamla_defect.bounding_box)

    def test_red_flag_unrepresented_minor_mutation(self):
        """Test detection of mutation executed during minority without lawful guardian or Sec 8 HMGA sanction."""
        # Mutation 2: In 2014, after Suresh Kumar's death, Ramesh Kumar had mutation recorded
        # while Amit Kumar was only 12 years old (minor), without appointment of guardian or court sanction!
        mut_minor = MutationRecord(
            mutation_no="INT-389",
            mutation_date_or_year="2014-08-20",
            mutation_type=MutationType.INHERITANCE_FAUTI,
            deceased_predecessor="Suresh Kumar",
            transferor_names=["Suresh Kumar (Deceased)"],
            transferee_names=["Ramesh Kumar"],               # Entire share mutated to uncle Ramesh!
            minor_heirs_involved=True,
            minor_names=["Amit Kumar", "Sunita Kumari"],
            guardian_represented=False,                      # Minor was unrepresented!
            district_court_permission_sec8=False,            # No court permission under HMGA Sec 8
            bounding_box=BoundingBox(ymin=220.0, xmin=45.0, ymax=290.0, xmax=540.0),
            notes="Mutation entered without appointment of legal guardian or notice to minor's mother."
        )

        jamabandi = LandRecordDocument(
            doc_id="JAM-1425F",
            doc_type="Khatauni",
            fasli_year_or_period="1425 Fasli",
            state="Uttar Pradesh",
            district="Meerut",
            tehsil="Mawana",
            village="Hastinapur",
            khasra_numbers=["452/1"],
            khata_khewat_no="Khata 84",
            total_area_raw="12 Bigha 0 Biswa",
            total_area_sq_m=self.total_area_sq_m,
            co_sharers=[
                RecordedCoSharer(name="Ramesh Kumar", share_raw="1/1", share_fraction="1/1")
            ]
        )

        report = self.engine.audit_title(
            vanshavali=self.vanshavali,
            land_record=jamabandi,
            mutations=[mut_minor]
        )

        minor_defects = [
            d for d in report.discrepancy_matrix
            if d.defect_category == DefectCategory.UNREPRESENTED_MINOR_MUTATION
        ]
        self.assertTrue(len(minor_defects) >= 1)
        defect = minor_defects[0]
        self.assertEqual(defect.severity, LegalSeverity.CRITICAL)
        self.assertIn("Hindu Minority and Guardianship Act 1956, Section 6 & 8(2)", defect.statutory_violations)
        self.assertEqual(defect.bounding_box.ymin, 220.0)

    def test_red_flag_excess_area_conveyance(self):
        """Test detection of transferor selling land exceeding recorded holding (Nemo dat quod non habet)."""
        # Baseline Jamabandi: Ramesh Kumar owns 1/3 share = 4 Bighas (10,117.14 m²)
        jamabandi = LandRecordDocument(
            doc_id="JAM-1420F",
            doc_type="Jamabandi",
            fasli_year_or_period="1420 Fasli",
            state="Uttar Pradesh",
            district="Meerut",
            tehsil="Mawana",
            village="Hastinapur",
            khasra_numbers=["452/1"],
            khata_khewat_no="Khata 50",
            total_area_raw="12 Bigha 0 Biswa",
            total_area_sq_m=self.total_area_sq_m,
            co_sharers=[
                RecordedCoSharer(
                    name="Ramesh Kumar",
                    share_raw="1/3",
                    share_fraction="1/3",
                    recorded_area_sq_m=10117.14  # 4 Bighas
                ),
                RecordedCoSharer(
                    name="Suresh Kumar",
                    share_raw="2/3",
                    share_fraction="2/3",
                    recorded_area_sq_m=20234.28  # 8 Bighas
                )
            ]
        )

        # Mutation 3: Ramesh Kumar executes Sale Deed conveying 6 Bighas (15,175.71 m²)
        # to third-party buyer Harish Chand, exceeding his 4 Bigha share by 2 Bighas (+5,058.57 m²)!
        mut_sale = MutationRecord(
            mutation_no="INT-512",
            mutation_date_or_year="2020-11-10",
            mutation_type=MutationType.SALE_TRANSFER,
            transferor_names=["Ramesh Kumar"],
            transferee_names=["Harish Chand"],
            area_transferred_raw="6 Bigha 0 Biswa",
            area_transferred_sq_m=15175.71,
            bounding_box=BoundingBox(ymin=330.0, xmin=50.0, ymax=410.0, xmax=550.0),
            notes="Registered Sale Deed No. 4410/2020 Sub-Registrar Mawana."
        )

        report = self.engine.audit_title(
            vanshavali=self.vanshavali,
            land_record=jamabandi,
            mutations=[mut_sale]
        )

        excess_defects = [
            d for d in report.discrepancy_matrix
            if d.defect_category == DefectCategory.EXCESS_AREA_CONVEYANCE
        ]
        self.assertEqual(len(excess_defects), 1)
        defect = excess_defects[0]
        self.assertEqual(defect.severity, LegalSeverity.CRITICAL)
        self.assertAlmostEqual(defect.deprived_area_sq_m, 5058.57, places=1)
        self.assertIn("Transfer of Property Act 1882, Section 44 & Section 48", defect.statutory_violations)

    def test_full_title_audit_report_generation(self):
        """Test complete multi-defect audit report generation in Markdown and JSON formats."""
        mut_1 = MutationRecord(
            mutation_no="INT-204",
            mutation_date_or_year="1996-05-14",
            mutation_type=MutationType.INHERITANCE_FAUTI,
            deceased_predecessor="Ram Lal",
            transferor_names=["Ram Lal (Deceased)"],
            transferee_names=["Suresh Kumar", "Ramesh Kumar"],
            share_transferred_raw="1/2 each",
            has_registered_haq_tyag=False,
            bounding_box=BoundingBox(ymin=110.0, xmin=40.0, ymax=180.0, xmax=520.0)
        )

        mut_2 = MutationRecord(
            mutation_no="INT-389",
            mutation_date_or_year="2014-08-20",
            mutation_type=MutationType.INHERITANCE_FAUTI,
            deceased_predecessor="Suresh Kumar",
            transferor_names=["Suresh Kumar (Deceased)"],
            transferee_names=["Ramesh Kumar"],
            minor_heirs_involved=True,
            minor_names=["Amit Kumar"],
            guardian_represented=False,
            bounding_box=BoundingBox(ymin=220.0, xmin=45.0, ymax=290.0, xmax=540.0)
        )

        jamabandi = LandRecordDocument(
            doc_id="JAM-1425F",
            doc_type="Khatauni",
            fasli_year_or_period="1425 Fasli",
            state="Uttar Pradesh",
            district="Meerut",
            tehsil="Mawana",
            village="Hastinapur",
            khasra_numbers=["452/1", "452/2"],
            khata_khewat_no="Khata 84",
            total_area_raw="12 Bigha 0 Biswa",
            total_area_sq_m=self.total_area_sq_m,
            co_sharers=[
                RecordedCoSharer(name="Ramesh Kumar", share_raw="1/1", share_fraction="1/1")
            ]
        )

        report = self.engine.audit_title(
            vanshavali=self.vanshavali,
            land_record=jamabandi,
            mutations=[mut_1, mut_2]
        )

        # Check report attributes
        self.assertEqual(report.claimant_id, "P06")
        self.assertEqual(report.claimant_name, "Amit Kumar")
        self.assertEqual(report.claimant_theoretical_share, "1/9")
        self.assertEqual(report.overall_title_risk, "CRITICAL_TITLE_DEFECT")
        self.assertTrue(len(report.discrepancy_matrix) >= 2)
        self.assertTrue(len(report.recommended_legal_roadmap) >= 3)

        # Check Markdown generation
        md_report = self.engine.generate_markdown_report(report)
        self.assertIn("# Discrepancy & Title Audit Engine Report", md_report)
        self.assertIn("CRITICAL TITLE DEFECT", md_report)
        self.assertIn("Amit Kumar", md_report)
        self.assertIn("INT-204", md_report)
        self.assertIn("INT-389", md_report)
        self.assertIn("Haq-Tyag", md_report)
        self.assertIn("Sarvam-105B", md_report)

        # Check JSON export
        json_report = self.engine.generate_json_report(report)
        parsed_json = json.loads(json_report)
        self.assertEqual(parsed_json["claimant_id"], "P06")
        self.assertEqual(parsed_json["overall_title_risk"], "CRITICAL_TITLE_DEFECT")


if __name__ == "__main__":
    unittest.main()
