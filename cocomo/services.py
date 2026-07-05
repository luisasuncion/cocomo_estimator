from math import ceil, prod
from typing import Iterable

from flask import session

from .tables import (
    PERSONNEL_DRIVERS,
    PLATFORM_DRIVERS,
    PRODUCT_DRIVERS,
    PROJECT_DRIVERS,
    SCALE_FACTORS,
)

COCOMO_A = 2.94
COCOMO_B = 0.91
COCOMO_C = 3.67
COCOMO_D = 0.28
DEFAULT_CURRENCY = "PEN"

SCALE_FACTOR_CODES = ("PREC", "FLEX", "RESL", "TEAM", "PMAT")
EFFORT_MULTIPLIER_CODES = (
    "RELY",
    "DATA",
    "CPLX",
    "RUSE",
    "DOCU",
    "TIME",
    "STOR",
    "PVOL",
    "ACAP",
    "PCAP",
    "PCON",
    "AEXP",
    "PEXP",
    "LTEX",
    "TOOL",
    "SITE",
    "SCED",
)


def default_selection(table):
    return {
        code: {"rating": "NM" if "NM" in options else next(iter(options)), "value": options.get("NM", next(iter(options.values())))}
        for code, options in table.items()
    }


def default_data():
    return {
        "project_name": "",
        "ksloc": None,
        "average_monthly_salary": None,
        "currency": DEFAULT_CURRENCY,
        "scale_factors": default_selection(SCALE_FACTORS),
        "effort_multipliers": {
            **default_selection(PRODUCT_DRIVERS),
            **default_selection(PLATFORM_DRIVERS),
            **default_selection(PERSONNEL_DRIVERS),
            **default_selection(PROJECT_DRIVERS),
        },
    }


def get_data():
    data = session.get("cocomo_data")
    if not data:
        data = default_data()
        session["cocomo_data"] = data
    return data


def save_project_size(project_name, ksloc):
    data = get_data()
    data["project_name"] = project_name.strip()
    data["ksloc"] = ksloc
    session["cocomo_data"] = data
    session.pop("cocomo_result", None)
    session.modified = True


def save_scale_factors(selection):
    data = get_data()
    data["scale_factors"] = selection
    session["cocomo_data"] = data
    session.pop("cocomo_result", None)
    session.modified = True


def save_effort_group(selection):
    data = get_data()
    effort = data.get("effort_multipliers", {})
    effort.update(selection)
    data["effort_multipliers"] = effort
    session["cocomo_data"] = data
    session.pop("cocomo_result", None)
    session.modified = True


def save_economic_data(average_monthly_salary, currency=DEFAULT_CURRENCY):
    data = get_data()
    data["average_monthly_salary"] = average_monthly_salary
    data["currency"] = currency or DEFAULT_CURRENCY
    session["cocomo_data"] = data
    session.pop("cocomo_result", None)
    session.modified = True


def calculate_scale_sum(scale_values: Iterable[float]) -> float:
    values = list(scale_values)

    if len(values) != 5:
        raise ValueError("Se requieren exactamente cinco factores de escala.")

    return sum(values)


def calculate_exponent_e(scale_values: Iterable[float]) -> float:
    scale_sum = calculate_scale_sum(scale_values)
    return COCOMO_B + (0.01 * scale_sum)


def calculate_eaf(effort_multiplier_values: Iterable[float]) -> float:
    values = list(effort_multiplier_values)

    if len(values) != 17:
        raise ValueError("Se requieren exactamente 17 multiplicadores de esfuerzo.")

    return prod(values)


def calculate_effort_pm(ksloc: float, exponent_e: float, eaf: float) -> float:
    if ksloc <= 0:
        raise ValueError("Las KSLOC deben ser mayores que cero.")

    if exponent_e <= 0:
        raise ValueError("El exponente E debe ser mayor que cero.")

    if eaf <= 0:
        raise ValueError("El EAF debe ser mayor que cero.")

    return COCOMO_A * (ksloc ** exponent_e) * eaf


def calculate_schedule_exponent(exponent_e: float) -> float:
    if exponent_e <= 0:
        raise ValueError("El exponente E debe ser mayor que cero.")

    return COCOMO_D + (0.2 * (exponent_e - COCOMO_B))


def calculate_tdev(effort_pm: float, schedule_exponent: float) -> float:
    if effort_pm <= 0:
        raise ValueError("El esfuerzo PM debe ser mayor que cero.")

    if schedule_exponent <= 0:
        raise ValueError("El exponente de tiempo debe ser mayor que cero.")

    return COCOMO_C * (effort_pm ** schedule_exponent)


def calculate_average_staff(effort_pm: float, tdev: float) -> float:
    if effort_pm <= 0:
        raise ValueError("El esfuerzo PM debe ser mayor que cero.")

    if tdev <= 0:
        raise ValueError("El tiempo TDEV debe ser mayor que cero.")

    return effort_pm / tdev


def calculate_total_cost(effort_pm: float, average_monthly_salary: float) -> float:
    if effort_pm <= 0:
        raise ValueError("El esfuerzo PM debe ser mayor que cero.")

    if average_monthly_salary <= 0:
        raise ValueError("El salario mensual promedio debe ser mayor que cero.")

    return effort_pm * average_monthly_salary


def calculate_size_sensitivity(
    base_ksloc: float,
    exponent_e: float,
    eaf: float,
    average_monthly_salary: float,
) -> list[dict]:
    scenarios = [
        ("Optimista", 0.90),
        ("Base", 1.00),
        ("Pesimista", 1.10),
    ]
    schedule_exponent = calculate_schedule_exponent(exponent_e)
    results = []

    for name, multiplier in scenarios:
        scenario_ksloc = base_ksloc * multiplier
        effort_pm = calculate_effort_pm(scenario_ksloc, exponent_e, eaf)
        tdev = calculate_tdev(effort_pm, schedule_exponent)
        average_staff = calculate_average_staff(effort_pm, tdev)
        total_cost = calculate_total_cost(effort_pm, average_monthly_salary)

        results.append(
            {
                "name": name,
                "ksloc": scenario_ksloc,
                "effort_pm": effort_pm,
                "tdev_months": tdev,
                "average_staff": average_staff,
                "total_cost": total_cost,
            }
        )

    return results


def calculate_salary_sensitivity(effort_pm: float, average_monthly_salary: float) -> list[dict]:
    scenarios = [
        ("Bajo", 0.90),
        ("Base", 1.00),
        ("Alto", 1.10),
    ]
    results = []

    for name, multiplier in scenarios:
        scenario_salary = average_monthly_salary * multiplier
        total_cost = calculate_total_cost(effort_pm, scenario_salary)
        results.append(
            {
                "name": name,
                "average_monthly_salary": scenario_salary,
                "total_cost": total_cost,
            }
        )

    return results


def _extract_values(data: dict, group_key: str, required_codes: Iterable[str]) -> list[float]:
    group = data.get(group_key)

    if not isinstance(group, dict):
        raise ValueError(f"No se encontraron los datos requeridos para {group_key}.")

    values = []
    for code in required_codes:
        try:
            value = group[code]["value"]
        except KeyError as exc:
            raise ValueError(f"Falta el valor de {code}.") from exc

        try:
            values.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"El valor de {code} debe ser numerico.") from exc

    return values


def calculate_cocomo_effort(cocomo_data: dict) -> dict:
    """
    Calcula suma de factores, exponente E, EAF y esfuerzo PM.
    """
    if not isinstance(cocomo_data, dict):
        raise ValueError("No se encontraron datos para realizar la estimacion.")

    if cocomo_data.get("ksloc") is None:
        raise ValueError("Falta ingresar las KSLOC del proyecto.")

    try:
        ksloc = float(cocomo_data["ksloc"])
    except (TypeError, ValueError) as exc:
        raise ValueError("KSLOC debe ser numerico.") from exc
    scale_values = _extract_values(cocomo_data, "scale_factors", SCALE_FACTOR_CODES)
    effort_multiplier_values = _extract_values(
        cocomo_data,
        "effort_multipliers",
        EFFORT_MULTIPLIER_CODES,
    )

    scale_sum = calculate_scale_sum(scale_values)
    exponent_e = COCOMO_B + (0.01 * scale_sum)
    eaf = calculate_eaf(effort_multiplier_values)
    effort_pm = calculate_effort_pm(ksloc, exponent_e, eaf)

    return {
        "ksloc": ksloc,
        "scale_sum": scale_sum,
        "exponent_e": exponent_e,
        "eaf": eaf,
        "effort_pm": effort_pm,
        "constant_a": COCOMO_A,
    }


def calculate_cocomo_final(cocomo_data: dict) -> dict:
    """
    Calcula esfuerzo, tiempo nominal, personal, costo y sensibilidad.
    """
    result = calculate_cocomo_effort(cocomo_data)

    if cocomo_data.get("average_monthly_salary") is None:
        raise ValueError("Falta ingresar el salario mensual promedio.")

    try:
        average_monthly_salary = float(cocomo_data["average_monthly_salary"])
    except (TypeError, ValueError) as exc:
        raise ValueError("El salario mensual promedio debe ser numerico.") from exc
    if average_monthly_salary <= 0:
        raise ValueError("El salario mensual promedio debe ser mayor que cero.")

    currency = cocomo_data.get("currency") or DEFAULT_CURRENCY
    schedule_exponent = calculate_schedule_exponent(result["exponent_e"])
    tdev = calculate_tdev(result["effort_pm"], schedule_exponent)
    average_staff = calculate_average_staff(result["effort_pm"], tdev)
    total_cost = calculate_total_cost(result["effort_pm"], average_monthly_salary)

    result.update(
        {
            "schedule_exponent_f": schedule_exponent,
            "tdev_months": tdev,
            "average_staff": average_staff,
            "rounded_staff": ceil(average_staff),
            "average_monthly_salary": average_monthly_salary,
            "currency": currency,
            "total_cost": total_cost,
            "constant_c": COCOMO_C,
            "constant_d": COCOMO_D,
            "constant_b": COCOMO_B,
            "size_sensitivity": calculate_size_sensitivity(
                result["ksloc"],
                result["exponent_e"],
                result["eaf"],
                average_monthly_salary,
            ),
            "salary_sensitivity": calculate_salary_sensitivity(
                result["effort_pm"],
                average_monthly_salary,
            ),
        }
    )

    return result


def format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")
