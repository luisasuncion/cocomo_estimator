import pytest

from cocomo.services import (
    calculate_cocomo_effort,
    calculate_eaf,
    calculate_effort_pm,
    calculate_exponent_e,
    calculate_scale_sum,
)


SCALE_VALUES = [3.72, 4.05, 2.83, 1.96, 4.73]
EFFORT_MULTIPLIER_VALUES = [
    1.10,
    1.14,
    1.17,
    1.00,
    1.11,
    1.00,
    1.00,
    0.89,
    1.00,
    1.00,
    0.90,
    1.10,
    1.00,
    0.91,
    0.90,
    0.93,
    1.00,
]


def example_cocomo_data():
    return {
        "ksloc": 8.904,
        "scale_factors": {
            "PREC": {"rating": "NM", "value": 3.72},
            "FLEX": {"rating": "LO", "value": 4.05},
            "RESL": {"rating": "HI", "value": 2.83},
            "TEAM": {"rating": "HI", "value": 1.96},
            "PMAT": {"rating": "NM", "value": 4.73},
        },
        "effort_multipliers": {
            "RELY": {"rating": "HI", "value": 1.10},
            "DATA": {"rating": "HI", "value": 1.14},
            "CPLX": {"rating": "HI", "value": 1.17},
            "RUSE": {"rating": "NM", "value": 1.00},
            "DOCU": {"rating": "HI", "value": 1.11},
            "TIME": {"rating": "NM", "value": 1.00},
            "STOR": {"rating": "NM", "value": 1.00},
            "PVOL": {"rating": "LO", "value": 0.89},
            "ACAP": {"rating": "NM", "value": 1.00},
            "PCAP": {"rating": "NM", "value": 1.00},
            "PCON": {"rating": "HI", "value": 0.90},
            "AEXP": {"rating": "LO", "value": 1.10},
            "PEXP": {"rating": "NM", "value": 1.00},
            "LTEX": {"rating": "HI", "value": 0.91},
            "TOOL": {"rating": "HI", "value": 0.90},
            "SITE": {"rating": "HI", "value": 0.93},
            "SCED": {"rating": "NM", "value": 1.00},
        },
    }


def test_calculate_scale_sum_with_five_factors():
    assert calculate_scale_sum(SCALE_VALUES) == pytest.approx(17.29)


def test_calculate_scale_sum_rejects_missing_factors():
    with pytest.raises(ValueError, match="cinco factores"):
        calculate_scale_sum(SCALE_VALUES[:4])


def test_calculate_exponent_e():
    assert calculate_exponent_e(SCALE_VALUES) == pytest.approx(1.0829)


def test_calculate_eaf_with_seventeen_multipliers():
    assert calculate_eaf(EFFORT_MULTIPLIER_VALUES) == pytest.approx(1.0929453044536028)


def test_calculate_eaf_rejects_missing_multipliers():
    with pytest.raises(ValueError, match="17 multiplicadores"):
        calculate_eaf(EFFORT_MULTIPLIER_VALUES[:16])


def test_calculate_effort_pm_rejects_zero_ksloc():
    with pytest.raises(ValueError, match="KSLOC"):
        calculate_effort_pm(0, 1.0829, 1.0929)


def test_calculate_effort_pm_rejects_negative_ksloc():
    with pytest.raises(ValueError, match="KSLOC"):
        calculate_effort_pm(-1, 1.0829, 1.0929)


def test_calculate_effort_pm():
    effort = calculate_effort_pm(8.904, 1.0829, 1.0929453044536028)
    assert effort == pytest.approx(34.2966, rel=1e-4)


def test_calculate_cocomo_effort_with_example_values():
    result = calculate_cocomo_effort(example_cocomo_data())

    assert result["scale_sum"] == pytest.approx(17.29)
    assert result["exponent_e"] == pytest.approx(1.0829)
    assert result["eaf"] == pytest.approx(1.0929, rel=1e-4)
    assert result["effort_pm"] == pytest.approx(34.2966, rel=1e-4)
