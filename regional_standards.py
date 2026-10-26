"""
Regional Land Measurement Standards Database for Indian Revenue Records.
Maps States, Districts, and Tehsils to standard local area measurement units
and provides exact conversion factors to Square Meters (m^2), Acres, Hectares, and Sq Feet.
"""

from typing import Dict, Any, Optional

# Master conversion factors
SQ_M_PER_ACRE = 4046.8564224
SQ_M_PER_HECTARE = 10000.0
SQ_FT_PER_SQ_M = 10.76391041671
SQ_YARDS_PER_SQ_M = 1.1959900463

REGIONAL_STANDARDS: Dict[str, Dict[str, Any]] = {
    "PUNJAB_HARYANA_STANDARD": {
        "name": "Punjab & Haryana Standard (Kanal-Marla System)",
        "states": ["Punjab", "Haryana", "Chandigarh"],
        "primary_units": ["Kanal", "Marla", "Sarsahi", "Killa", "Acre", "Ghumao"],
        "subunits": {
            "sarsahi": {"ratio_to_marla": 1 / 9, "sq_meters": 25.29285264 / 9},
            "marla": {"ratio_to_kanal": 1 / 20, "sq_meters": 25.29285264},      # 9 sarsahi = 272.25 sq ft
            "kanal": {"ratio_to_acre": 1 / 8, "sq_meters": 505.8570528},        # 20 marla = 5445 sq ft
            "killa": {"ratio_to_acre": 1.0, "sq_meters": 4046.8564224},         # 8 kanal = 1 acre
            "ghumao": {"ratio_to_acre": 1.0, "sq_meters": 4046.8564224},        # 8 kanal = 1 acre
            "acre": {"ratio_to_acre": 1.0, "sq_meters": 4046.8564224},
            "bigha_punjab": {"ratio_to_acre": 0.5, "sq_meters": 2023.4282112},  # 4 kanal in some areas
            "biswa_punjab": {"ratio_to_acre": 0.5 / 20, "sq_meters": 101.17141056}
        },
        "description": "Standard Karam = 66 inches (5.5 ft). 1 Acre = 8 Kanals = 160 Marlas = 1,440 Sarsahis."
    },
    "UP_PUCCA_BIGHA": {
        "name": "Uttar Pradesh Standard / Pucca Bigha",
        "states": ["Uttar Pradesh", "Uttarakhand", "Delhi"],
        "districts": [
            "meerut", "aligarh", "bulandshahr", "mathura", "agra", "muzaffarnagar",
            "ghaziabad", "hapur", "gautam buddha nagar", "baghpat", "moradabad",
            "saharanpur", "bareilly", "lucknow", "kanpur", "ayodhya", "varanasi"
        ],
        "primary_units": ["Bigha", "Biswa", "Biswansi", "Gatha"],
        "subunits": {
            "biswansi": {"ratio_to_biswa": 1 / 20, "sq_meters": 6.3232125},    # 1 sq gatha (99 in x 99 in = 68.0625 sq ft)
            "biswa": {"ratio_to_bigha": 1 / 20, "sq_meters": 126.46425},       # 20 biswansi = 1361.25 sq ft = 151.25 sq yards
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 2529.285},           # 20 biswa = 3025 sq yards = 27,225 sq ft = 5/8 acre
            "pucca_bigha": {"ratio_to_bigha": 1.0, "sq_meters": 2529.285},
            "kuchha_bigha": {"ratio_to_bigha": 1 / 3, "sq_meters": 843.095},   # 1/3 pucca bigha = 9075 sq ft = 1008.33 sq yards
            "dhur": {"ratio_to_biswa": 1 / 20, "sq_meters": 6.3232125},        # Eastern UP equivalent to biswansi
            "katha": {"ratio_to_bigha": 1 / 20, "sq_meters": 126.46425}
        },
        "description": "Pucca Bigha: 1 Bigha = 20 Biswa = 400 Biswansi = 3,025 sq yards = 2,529.285 sq meters (27,225 sq ft)."
    },
    "UP_KUCHHA_BIGHA": {
        "name": "Western Uttar Pradesh Kuchha Bigha",
        "states": ["Uttar Pradesh"],
        "districts": ["bijnor", "rampur", "pilibhit", "shahjahanpur", "budaun"],
        "primary_units": ["Kuchha Bigha", "Biswa", "Biswansi"],
        "subunits": {
            "biswansi": {"ratio_to_biswa": 1 / 20, "sq_meters": 2.1077375},
            "biswa": {"ratio_to_bigha": 1 / 20, "sq_meters": 42.15475},
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 843.095},            # 1/3 of Pucca Bigha (9075 sq ft)
            "kuchha_bigha": {"ratio_to_bigha": 1.0, "sq_meters": 843.095}
        },
        "description": "Kuchha Bigha: 1 Kuchha Bigha = 1/3 Pucca Bigha = 843.095 sq meters (9,075 sq ft)."
    },
    "RAJASTHAN_STANDARD": {
        "name": "Rajasthan Bigha-Biswa Standard",
        "states": ["Rajasthan"],
        "primary_units": ["Bigha", "Biswa", "Biswansi"],
        "subunits": {
            "biswansi": {"ratio_to_biswa": 1 / 20, "sq_meters": 6.3232125},
            "biswa": {"ratio_to_bigha": 1 / 20, "sq_meters": 126.46425},
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 2529.285},           # Pucca Bigha in Rajasthan: 27,225 sq ft
            "pucca_bigha": {"ratio_to_bigha": 1.0, "sq_meters": 2529.285},
            "kuchha_bigha": {"ratio_to_bigha": 1618.74 / 2529.285, "sq_meters": 1618.7425} # Kuchha: 1618.74 sq m = 17,424 sq ft (4/10 acre)
        },
        "description": "Rajasthan Standard: 1 Pucca Bigha = 20 Biswa = 2,529.285 sq meters; 1 Kuchha Bigha = 1,618.74 sq meters."
    },
    "HIMACHAL_STANDARD": {
        "name": "Himachal Pradesh Bigha Standard",
        "states": ["Himachal Pradesh"],
        "primary_units": ["Bigha", "Biswa", "Biswansi"],
        "subunits": {
            "biswansi": {"ratio_to_biswa": 1 / 20, "sq_meters": 40.0 / 20},     # 2 sq m
            "biswa": {"ratio_to_bigha": 1 / 20, "sq_meters": 40.0},             # 40 sq m (or 40.47 sq m)
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 800.0}                # HP Land Revenue standard: 800 sq meters (or 809.37 sq m = 1/5 acre)
        },
        "description": "Himachal Pradesh: 1 Bigha = 20 Biswas = 800.0 sq meters (or 809.37 sq m = 1/5 acre = 8,712 sq ft)."
    },
    "BIHAR_STANDARD": {
        "name": "Bihar & Jharkhand Katha-Bigha Standard",
        "states": ["Bihar", "Jharkhand"],
        "primary_units": ["Bigha", "Katha", "Dhur", "Dhurki"],
        "subunits": {
            "dhurki": {"ratio_to_dhur": 1 / 20, "sq_meters": 0.31616},
            "dhur": {"ratio_to_katha": 1 / 20, "sq_meters": 6.3232125},
            "katha": {"ratio_to_bigha": 1 / 20, "sq_meters": 126.46425},       # 1361.25 sq ft
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 2529.285}
        },
        "description": "Bihar Standard: 1 Bigha = 20 Katha = 400 Dhur = 2,529.285 sq meters (Pucca standard)."
    },
    "BENGAL_STANDARD": {
        "name": "West Bengal & Assam Bigha-Katha-Chhatak",
        "states": ["West Bengal", "Assam", "Tripura"],
        "primary_units": ["Bigha", "Katha", "Chhatak", "Decimal", "Satak"],
        "subunits": {
            "chhatak": {"ratio_to_katha": 1 / 16, "sq_meters": 4.180637},       # 45 sq ft
            "katha": {"ratio_to_bigha": 1 / 20, "sq_meters": 66.89019},         # 720 sq ft
            "bigha": {"ratio_to_bigha": 1.0, "sq_meters": 1337.8038},           # 14,400 sq ft = 1/3 acre
            "decimal": {"ratio_to_acre": 1 / 100, "sq_meters": 40.468564},      # 1/100 acre = 435.6 sq ft
            "satak": {"ratio_to_acre": 1 / 100, "sq_meters": 40.468564}
        },
        "description": "Bengal Standard: 1 Bigha = 20 Katha = 320 Chhatak = 14,400 sq ft = 1,337.8 sq meters (1/3 acre)."
    },
    "MAHARASHTRA_GUJARAT_STANDARD": {
        "name": "Maharashtra & Gujarat Metric / Guntha Standard",
        "states": ["Maharashtra", "Gujarat", "Goa"],
        "primary_units": ["Hectare", "Are", "Guntha", "Vigha", "Acre"],
        "subunits": {
            "sq_meter": {"sq_meters": 1.0},
            "guntha": {"sq_meters": 101.17141056},                              # 121 sq yards = 1089 sq ft (33 ft x 33 ft)
            "gunta": {"sq_meters": 101.17141056},
            "are": {"sq_meters": 100.0},                                        # 1 Are = 100 sq meters
            "r": {"sq_meters": 100.0},                                          # 7/12 notation: Hectare-Are (Ha-R)
            "hectare": {"sq_meters": 10000.0},                                  # 1 Hectare = 100 Ares = 10,000 sq m
            "acre": {"sq_meters": 4046.8564224},                                # 40 Gunthas = 1 Acre
            "vigha_gujarat": {"sq_meters": 1618.7425},                          # 16 Gunthas = 17,424 sq ft = 0.4 acre
            "vasa": {"sq_meters": 80.937125}                                    # 1/20 Vigha
        },
        "description": "Maharashtra & Gujarat: 1 Hectare = 100 Ares = 10,000 sq m; 1 Guntha = 101.17 sq m (40 Gunthas = 1 Acre)."
    },
    "SOUTH_INDIA_STANDARD": {
        "name": "South India (Tamil Nadu, Karnataka, AP, Telangana, Kerala)",
        "states": ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala"],
        "primary_units": ["Acre", "Cent", "Ground", "Guntha", "Ankanam"],
        "subunits": {
            "cent": {"ratio_to_acre": 1 / 100, "sq_meters": 40.468564},         # 435.6 sq ft
            "ground": {"sq_meters": 222.967296},                                # 2400 sq ft (Tamil Nadu standard)
            "guntha": {"sq_meters": 101.17141056},                              # 1089 sq ft (Karnataka / Telangana)
            "ankanam": {"sq_meters": 6.689019},                                 # 72 sq ft (AP / Nellore standard)
            "acre": {"sq_meters": 4046.8564224},                                # 100 Cents
            "hectare": {"sq_meters": 10000.0}
        },
        "description": "South India: 1 Acre = 100 Cents = 4,046.86 sq meters; 1 Ground = 2,400 sq ft = 222.97 sq meters."
    },
    "METRIC_STANDARD": {
        "name": "Standard International Metric & Statutory Units",
        "states": ["All India"],
        "primary_units": ["Square Meter", "Hectare", "Are", "Acre", "Square Feet", "Square Yard"],
        "subunits": {
            "sq_meter": {"sq_meters": 1.0},
            "square_meter": {"sq_meters": 1.0},
            "sq_m": {"sq_meters": 1.0},
            "m2": {"sq_meters": 1.0},
            "are": {"sq_meters": 100.0},
            "hectare": {"sq_meters": 10000.0},
            "ha": {"sq_meters": 10000.0},
            "acre": {"sq_meters": 4046.8564224},
            "sq_foot": {"sq_meters": 0.09290304},
            "sq_ft": {"sq_meters": 0.09290304},
            "sq_yard": {"sq_meters": 0.83612736},
            "gaz": {"sq_meters": 0.83612736}
        },
        "description": "Universal Metric & Imperial standard units."
    }
}


def resolve_regional_standard(
    state: Optional[str] = None,
    district: Optional[str] = None,
    tehsil: Optional[str] = None,
    preferred_unit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Determines the appropriate local measurement standard definition based on state, district, or tehsil.
    Resolves specific variants (e.g. Pucca vs Kuchha Bigha, Kanal-Marla vs Bigha-Biswa).
    """
    state_clean = (state or "").strip().lower()
    dist_clean = (district or "").strip().lower()
    tehsil_clean = (tehsil or "").strip().lower()
    unit_clean = (preferred_unit or "").strip().lower()

    # District specific overrides
    if dist_clean in ["bijnor", "rampur", "pilibhit", "shahjahanpur", "budaun"] or "kuchha" in unit_clean:
        return REGIONAL_STANDARDS["UP_KUCHHA_BIGHA"]

    if any(s in state_clean for s in ["punjab", "haryana", "chandigarh"]) or any(u in unit_clean for u in ["kanal", "marla", "sarsahi", "killa"]):
        return REGIONAL_STANDARDS["PUNJAB_HARYANA_STANDARD"]

    if "himachal" in state_clean:
        return REGIONAL_STANDARDS["HIMACHAL_STANDARD"]

    if any(s in state_clean for s in ["rajasthan"]):
        return REGIONAL_STANDARDS["RAJASTHAN_STANDARD"]

    if any(s in state_clean for s in ["bihar", "jharkhand"]):
        return REGIONAL_STANDARDS["BIHAR_STANDARD"]

    if any(s in state_clean for s in ["bengal", "assam", "tripura"]):
        return REGIONAL_STANDARDS["BENGAL_STANDARD"]

    if any(s in state_clean for s in ["maharashtra", "gujarat", "goa"]) or any(u in unit_clean for u in ["guntha", "gunta", "are", "ha", "hectare", "vigha"]):
        return REGIONAL_STANDARDS["MAHARASHTRA_GUJARAT_STANDARD"]

    if any(s in state_clean for s in ["tamil nadu", "karnataka", "andhra", "telangana", "kerala"]) or any(u in unit_clean for u in ["cent", "ground", "ankanam"]):
        return REGIONAL_STANDARDS["SOUTH_INDIA_STANDARD"]

    if any(s in state_clean for s in ["uttar pradesh", "up", "uttarakhand", "delhi"]):
        return REGIONAL_STANDARDS["UP_PUCCA_BIGHA"]

    # Fallback by unit inference
    if any(u in unit_clean for u in ["bigha", "biswa"]):
        return REGIONAL_STANDARDS["UP_PUCCA_BIGHA"]
    
    if any(u in unit_clean for u in ["guntha", "are", "hectare"]):
        return REGIONAL_STANDARDS["MAHARASHTRA_GUJARAT_STANDARD"]

    if any(u in unit_clean for u in ["cent", "ground"]):
        return REGIONAL_STANDARDS["SOUTH_INDIA_STANDARD"]

    return REGIONAL_STANDARDS["UP_PUCCA_BIGHA"]
