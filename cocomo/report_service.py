import re
import unicodedata
from datetime import datetime
from io import BytesIO

from .services import EFFORT_MULTIPLIER_CODES, SCALE_FACTOR_CODES, format_currency
from .tables import FACTOR_INFO, RATING_LABELS

PRODUCT_CODES = ("RELY", "DATA", "CPLX", "RUSE", "DOCU")
PLATFORM_CODES = ("TIME", "STOR", "PVOL")
PERSONNEL_CODES = ("ACAP", "PCAP", "PCON", "AEXP", "PEXP", "LTEX")
PROJECT_CODES = ("TOOL", "SITE", "SCED")

REQUIRED_RESULT_FIELDS = (
    "ksloc",
    "scale_sum",
    "exponent_e",
    "eaf",
    "effort_pm",
    "schedule_exponent_f",
    "tdev_months",
    "average_staff",
    "rounded_staff",
    "average_monthly_salary",
    "currency",
    "total_cost",
    "size_sensitivity",
    "salary_sensitivity",
)


def sanitize_filename(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^a-zA-Z0-9\s_-]", "", ascii_value).strip().lower()
    safe = re.sub(r"[\s-]+", "_", safe)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return (safe or "proyecto")[:80]


def build_report_filename(project_name: str, generated_at: datetime | None = None) -> str:
    current_date = (generated_at or datetime.now()).date().isoformat()
    return f"reporte_cocomo_ii_{sanitize_filename(project_name)}_{current_date}.pdf"


def build_report_context(cocomo_data: dict, cocomo_result: dict) -> dict:
    """
    Prepara y valida la informacion que sera enviada a la plantilla del reporte.
    """
    _validate_inputs(cocomo_data, cocomo_result)
    generated_at = datetime.now()
    project_name = _project_name(cocomo_data)
    scale_factors = _factor_rows(cocomo_data["scale_factors"], SCALE_FACTOR_CODES, "value")
    effort_categories = [
        {"name": "Producto", "rows": _factor_rows(cocomo_data["effort_multipliers"], PRODUCT_CODES, "multiplier")},
        {"name": "Plataforma", "rows": _factor_rows(cocomo_data["effort_multipliers"], PLATFORM_CODES, "multiplier")},
        {"name": "Personal", "rows": _factor_rows(cocomo_data["effort_multipliers"], PERSONNEL_CODES, "multiplier")},
        {"name": "Proyecto", "rows": _factor_rows(cocomo_data["effort_multipliers"], PROJECT_CODES, "multiplier")},
    ]

    interpretation = (
        f"El proyecto requiere aproximadamente {_fmt(cocomo_result['effort_pm'], 2)} personas-mes de esfuerzo. "
        f"El tiempo nominal estimado es de {_fmt(cocomo_result['tdev_months'], 2)} meses, con un personal "
        f"promedio de {_fmt(cocomo_result['average_staff'], 2)} integrantes. Para efectos practicos, se recomienda "
        f"un equipo de {cocomo_result['rounded_staff']} personas. Considerando un salario mensual promedio de "
        f"S/ {format_currency(cocomo_result['average_monthly_salary'])}, el costo laboral estimado es de "
        f"S/ {format_currency(cocomo_result['total_cost'])}."
    )

    return {
        "app_name": "Estimador COCOMO II",
        "generated_at": generated_at,
        "project_name": project_name,
        "currency": cocomo_result.get("currency", "PEN"),
        "ksloc": cocomo_result["ksloc"],
        "result": cocomo_result,
        "scale_factors": scale_factors,
        "effort_categories": effort_categories,
        "formulas": _build_formulas(cocomo_result),
        "interpretation": interpretation,
        "conclusion": (
            "La estimacion obtenida mediante COCOMO II proporciona una referencia cuantitativa para la "
            "planificacion del proyecto. Los resultados dependen del tamaño estimado, los factores de escala, "
            "los multiplicadores de esfuerzo y el salario mensual ingresado. Por ello, cualquier modificacion "
            "en estas variables puede alterar el esfuerzo, tiempo y costo calculados."
        ),
    }


def html_to_pdf(html_content: str, css_path: str, context: dict | None = None) -> bytes:
    try:
        from weasyprint import CSS, HTML

        return HTML(string=html_content).write_pdf(stylesheets=[CSS(filename=css_path)])
    except Exception:
        if context is None:
            raise
        return _fallback_reportlab_pdf(context)


def _validate_inputs(cocomo_data: dict, cocomo_result: dict) -> None:
    if not isinstance(cocomo_data, dict) or not isinstance(cocomo_result, dict):
        raise ValueError("No existen resultados disponibles para generar el reporte.")

    if not _project_name(cocomo_data):
        raise ValueError("Falta el nombre del proyecto para generar el reporte.")

    if cocomo_data.get("ksloc") is None:
        raise ValueError("Falta el tamaño KSLOC para generar el reporte.")

    _validate_group(cocomo_data, "scale_factors", SCALE_FACTOR_CODES)
    _validate_group(cocomo_data, "effort_multipliers", EFFORT_MULTIPLIER_CODES)

    for field in REQUIRED_RESULT_FIELDS:
        if field not in cocomo_result:
            raise ValueError("Los resultados de la estimacion estan incompletos.")


def _validate_group(cocomo_data: dict, group_key: str, codes: tuple[str, ...]) -> None:
    group = cocomo_data.get(group_key)
    if not isinstance(group, dict):
        raise ValueError("Los factores de la estimacion estan incompletos.")

    for code in codes:
        item = group.get(code)
        if not isinstance(item, dict) or "rating" not in item or "value" not in item:
            raise ValueError(f"Falta el valor calculado de {code}.")


def _project_name(cocomo_data: dict) -> str:
    project = cocomo_data.get("project")
    if isinstance(project, dict) and project.get("name"):
        return str(project["name"]).strip()
    return str(cocomo_data.get("project_name") or "Proyecto sin nombre").strip()


def _factor_rows(group: dict, codes: tuple[str, ...], value_key: str) -> list[dict]:
    rows = []
    for code in codes:
        item = group[code]
        rating = item["rating"]
        rows.append(
            {
                "code": code,
                "name": FACTOR_INFO[code][0],
                "rating": rating,
                "rating_label": f"{RATING_LABELS[rating]} ({rating})",
                value_key: float(item["value"]),
            }
        )
    return rows


def _build_formulas(result: dict) -> list[dict]:
    return [
        {
            "title": "Exponente E",
            "lines": [
                "E = B + 0.01 x ΣWj",
                f"E = 0.91 + 0.01 x {_fmt(result['scale_sum'], 2)}",
                f"E = {_fmt(result['exponent_e'], 4)}",
            ],
        },
        {"title": "EAF", "lines": ["EAF = ∏ EMi", f"EAF = {_fmt(result['eaf'], 4)}"]},
        {
            "title": "Esfuerzo",
            "lines": [
                "PM = A x Size^E x EAF",
                f"PM = 2.94 x ({_fmt(result['ksloc'], 3)})^{_fmt(result['exponent_e'], 4)} x {_fmt(result['eaf'], 4)}",
                f"PM = {_fmt(result['effort_pm'], 2)} personas-mes",
            ],
        },
        {
            "title": "Exponente de tiempo",
            "lines": [
                "F = 0.28 + 0.2 x (E - 0.91)",
                f"F = {_fmt(result['schedule_exponent_f'], 4)}",
            ],
        },
        {
            "title": "Tiempo nominal",
            "lines": ["TDEV = 3.67 x PM^F", f"TDEV = {_fmt(result['tdev_months'], 2)} meses"],
        },
        {
            "title": "Personal",
            "lines": ["Personal = PM / TDEV", f"Personal = {_fmt(result['average_staff'], 2)} personas"],
        },
        {
            "title": "Costo",
            "lines": [
                "Costo = PM x salario mensual promedio",
                f"Costo = S/ {format_currency(result['total_cost'])}",
            ],
        },
    ]


def _fallback_reportlab_pdf(context: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, pageCompression=0)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Reporte de estimacion COCOMO II", styles["Title"]),
        Paragraph(f"Proyecto: {context['project_name']}", styles["Normal"]),
        Paragraph(f"KSLOC: {_fmt(context['ksloc'], 3)}", styles["Normal"]),
        Paragraph(f"E: {_fmt(context['result']['exponent_e'], 4)}", styles["Normal"]),
        Paragraph(f"EAF: {_fmt(context['result']['eaf'], 4)}", styles["Normal"]),
        Paragraph(f"PM: {_fmt(context['result']['effort_pm'], 2)} personas-mes", styles["Normal"]),
        Paragraph(f"TDEV: {_fmt(context['result']['tdev_months'], 2)} meses", styles["Normal"]),
        Paragraph(f"Costo: S/ {format_currency(context['result']['total_cost'])}", styles["Normal"]),
        Spacer(1, 12),
        Table([["Escenario", "KSLOC", "PM"]] + [
            [item["name"], _fmt(item["ksloc"], 3), _fmt(item["effort_pm"], 2)]
            for item in context["result"]["size_sensitivity"]
        ]),
    ]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _fmt(value: float, decimals: int) -> str:
    return f"{float(value):.{decimals}f}"
