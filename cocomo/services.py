from math import prod
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
    session.modified = True


def save_scale_factors(selection):
    data = get_data()
    data["scale_factors"] = selection
    session["cocomo_data"] = data
    session.modified = True


def save_effort_group(selection):
    data = get_data()
    effort = data.get("effort_multipliers", {})
    effort.update(selection)
    data["effort_multipliers"] = effort
    session["cocomo_data"] = data
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

        values.append(float(value))

    return values


def calculate_cocomo_effort(cocomo_data: dict) -> dict:
    """
    Calcula suma de factores, exponente E, EAF y esfuerzo PM.
    """
    if not isinstance(cocomo_data, dict):
        raise ValueError("No se encontraron datos para realizar la estimacion.")

    if cocomo_data.get("ksloc") is None:
        raise ValueError("Falta ingresar las KSLOC del proyecto.")

    ksloc = float(cocomo_data["ksloc"])
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
