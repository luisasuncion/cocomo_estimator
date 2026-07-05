import pytest

from cocomo.services import (
    calculate_average_staff,
    calculate_cocomo_final,
    calculate_cocomo_effort,
    calculate_eaf,
    calculate_effort_pm,
    calculate_exponent_e,
    calculate_scale_sum,
    calculate_salary_sensitivity,
    calculate_schedule_exponent,
    calculate_size_sensitivity,
    calculate_tdev,
    calculate_total_cost,
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


def test_calculate_schedule_exponent():
    assert calculate_schedule_exponent(1.0829) == pytest.approx(0.31458)


def test_calculate_tdev():
    tdev = calculate_tdev(34.29663562044247, 0.31458)
    assert tdev == pytest.approx(11.1590, rel=1e-4)


def test_calculate_tdev_rejects_zero_pm():
    with pytest.raises(ValueError, match="PM"):
        calculate_tdev(0, 0.31458)


def test_calculate_average_staff():
    assert calculate_average_staff(34.29663562044247, 11.159005386429609) == pytest.approx(3.0734, rel=1e-4)


def test_calculate_total_cost():
    assert calculate_total_cost(34.29663562044247, 2500.0) == pytest.approx(85741.5891, rel=1e-4)


def test_calculate_total_cost_rejects_zero_salary():
    with pytest.raises(ValueError, match="salario"):
        calculate_total_cost(34.29663562044247, 0)


def test_calculate_total_cost_rejects_negative_salary():
    with pytest.raises(ValueError, match="salario"):
        calculate_total_cost(34.29663562044247, -2500)


def test_size_sensitivity_optimistic():
    scenarios = calculate_size_sensitivity(8.904, 1.0829, 1.0929453044536028, 2500.0)

    assert scenarios[0]["name"] == "Optimista"
    assert scenarios[0]["ksloc"] == pytest.approx(8.0136)
    assert scenarios[0]["effort_pm"] == pytest.approx(30.5985, rel=1e-4)


def test_size_sensitivity_base():
    scenarios = calculate_size_sensitivity(8.904, 1.0829, 1.0929453044536028, 2500.0)

    assert scenarios[1]["name"] == "Base"
    assert scenarios[1]["ksloc"] == pytest.approx(8.904)
    assert scenarios[1]["total_cost"] == pytest.approx(85741.5891, rel=1e-4)


def test_size_sensitivity_pessimistic():
    scenarios = calculate_size_sensitivity(8.904, 1.0829, 1.0929453044536028, 2500.0)

    assert scenarios[2]["name"] == "Pesimista"
    assert scenarios[2]["ksloc"] == pytest.approx(9.7944)
    assert scenarios[2]["effort_pm"] == pytest.approx(38.0256, rel=1e-4)


def test_salary_sensitivity_low_salary():
    scenarios = calculate_salary_sensitivity(34.29663562044247, 2500.0)

    assert scenarios[0]["name"] == "Bajo"
    assert scenarios[0]["average_monthly_salary"] == pytest.approx(2250.0)
    assert scenarios[0]["total_cost"] == pytest.approx(77167.4301, rel=1e-4)


def test_salary_sensitivity_high_salary():
    scenarios = calculate_salary_sensitivity(34.29663562044247, 2500.0)

    assert scenarios[2]["name"] == "Alto"
    assert scenarios[2]["average_monthly_salary"] == pytest.approx(2750.0)
    assert scenarios[2]["total_cost"] == pytest.approx(94315.7480, rel=1e-4)


def test_calculate_cocomo_final_with_example_values():
    data = example_cocomo_data()
    data["average_monthly_salary"] = 2500.0
    data["currency"] = "PEN"

    result = calculate_cocomo_final(data)

    assert result["effort_pm"] == pytest.approx(34.2966, rel=1e-4)
    assert result["schedule_exponent_f"] == pytest.approx(0.31458)
    assert result["tdev_months"] == pytest.approx(11.1590, rel=1e-4)
    assert result["average_staff"] == pytest.approx(3.0734, rel=1e-4)
    assert result["rounded_staff"] == 4
    assert result["total_cost"] == pytest.approx(85741.5891, rel=1e-4)
    assert len(result["size_sensitivity"]) == 3
    assert len(result["salary_sensitivity"]) == 3
