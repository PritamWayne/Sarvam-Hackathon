"""
Unit Test Suite for Area Unit Normalization & Arithmetic Validation Engine.
"""

import unittest
from fractions import Fraction
from regional_standards import resolve_regional_standard
from area_normalizer import AreaNormalizer
from arithmetic_validator import ArithmeticValidator


class TestAreaUnitNormalization(unittest.TestCase):

    def test_regional_standard_resolution(self):
        # UP Pucca
        std_up = resolve_regional_standard(state="Uttar Pradesh", district="Meerut")
        self.assertIn("Pucca", std_up["name"])

        # UP Kuchha
        std_kuchha = resolve_regional_standard(state="Uttar Pradesh", district="Bijnor")
        self.assertIn("Kuchha", std_kuchha["name"])

        # Punjab
        std_pb = resolve_regional_standard(state="Punjab", district="Ludhiana")
        self.assertIn("Punjab", std_pb["name"])

        # Maharashtra
        std_mh = resolve_regional_standard(state="Maharashtra", district="Pune")
        self.assertIn("Maharashtra", std_mh["name"])

    def test_up_pucca_bigha_conversion(self):
        norm = AreaNormalizer(state="Uttar Pradesh", district="Meerut")
        # 1 Pucca Bigha = 2,529.285 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("1 Bigha"), 2529.285, places=2)
        # 20 Biswa = 1 Bigha = 2,529.285 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("20 Biswa"), 2529.285, places=2)
        # 2 Bigha 10 Biswa = 2.5 Bigha = 6,323.2125 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("2 Bigha 10 Biswa"), 6323.2125, places=2)

    def test_punjab_kanal_marla_conversion(self):
        norm = AreaNormalizer(state="Punjab", district="Jalandhar")
        # 8 Kanal = 1 Acre = 4046.8564 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("8 Kanal"), 4046.8564, places=2)
        # 1 Kanal = 20 Marla = 505.857 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("1 Kanal"), 505.857, places=2)
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("20 Marla"), 505.857, places=2)

    def test_maharashtra_metric_conversion(self):
        norm = AreaNormalizer(state="Maharashtra")
        # 1 Hectare = 10,000 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("1 Hectare"), 10000.0, places=2)
        # 1 Are = 100 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("1 Are"), 100.0, places=2)
        # 1 Ha 20 R = 12,000 sq meters
        self.assertAlmostEqual(norm.normalize_area_to_sq_meters("1 Ha 20 R"), 12000.0, places=2)

    def test_hissedari_fraction_parsing(self):
        norm = AreaNormalizer()
        self.assertEqual(norm.parse_hissedari_fraction("1/3"), Fraction(1, 3))
        self.assertEqual(norm.parse_hissedari_fraction("5/12"), Fraction(5, 12))
        self.assertEqual(norm.parse_hissedari_fraction("25%"), Fraction(1, 4))
        self.assertEqual(norm.parse_hissedari_fraction(0.5), Fraction(1, 2))
        # 8 Annas = 8/16 = 1/2
        self.assertEqual(norm.parse_hissedari_fraction("8 Annas"), Fraction(1, 2))
        # 4 Annas = 4/16 = 1/4
        self.assertEqual(norm.parse_hissedari_fraction("4 Annas"), Fraction(1, 4))
        # 5 Biswa out of 20 = 1/4
        self.assertEqual(norm.parse_hissedari_fraction("5 Biswa"), Fraction(1, 4))

    def test_conservation_audit_balanced(self):
        validator = ArithmeticValidator(state="Punjab", district="Jalandhar")
        result = validator.audit_plot(
            plot_id="Khasra 100",
            total_plot_area="8 Kanal",
            co_sharers_data=[
                {"name": "A", "share": "1/2"},
                {"name": "B", "share": "1/4"},
                {"name": "C", "share": "1/4"}
            ]
        )
        self.assertEqual(result.status, "CONSERVED")
        self.assertEqual(result.sum_shares_fraction, Fraction(1, 1))
        self.assertAlmostEqual(result.area_delta_sq_m, 0.0, places=2)

    def test_conservation_audit_surplus(self):
        # Surplus land created out of thin air
        validator = ArithmeticValidator(state="Uttar Pradesh", district="Meerut")
        result = validator.audit_plot(
            plot_id="Khasra 200",
            total_plot_area="2 Bigha",
            co_sharers_data=[
                {"name": "A", "share": "1/2"},
                {"name": "B", "share": "1/2"},
                {"name": "C", "share": "1/4"}  # Sum = 5/4 = 125%
            ]
        )
        self.assertEqual(result.status, "SURPLUS_ALERT")
        self.assertEqual(result.risk_level, "CRITICAL")
        self.assertGreater(result.area_delta_sq_m, 0.0)

    def test_conservation_audit_deficit(self):
        # Deficit / Unaccounted land
        validator = ArithmeticValidator(state="Maharashtra", district="Pune")
        result = validator.audit_plot(
            plot_id="Gat 300",
            total_plot_area="1 Hectare",
            co_sharers_data=[
                {"name": "A", "share": "1/3"},
                {"name": "B", "share": "1/3"}  # Sum = 2/3 = 66.67%
            ]
        )
        self.assertEqual(result.status, "DEFICIT_ALERT")
        self.assertLess(result.area_delta_sq_m, 0.0)


if __name__ == "__main__":
    unittest.main()
