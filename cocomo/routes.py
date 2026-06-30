from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .services import (
    calculate_cocomo_effort,
    get_data,
    save_effort_group,
    save_project_size,
    save_scale_factors,
)
from .tables import (
    FACTOR_INFO,
    PERSONNEL_DRIVERS,
    PLATFORM_DRIVERS,
    PRODUCT_DRIVERS,
    PROJECT_DRIVERS,
    RATING_LABELS,
    SCALE_FACTORS,
)
from .validators import validate_ksloc, validate_ratings

bp = Blueprint("wizard", __name__)

STEPS = [
    ("size", "Tamano"),
    ("scale", "Factores de escala"),
    ("product", "Producto"),
    ("platform", "Plataforma"),
    ("personnel", "Personal"),
    ("project", "Proyecto"),
    ("summary", "Resumen"),
    ("results", "Resultado"),
]


def render_step(template, active_step, table=None, group_key=None, errors=None):
    data = get_data()
    saved_group = data.get(group_key, {}) if group_key else {}
    active_index = [key for key, _label in STEPS].index(active_step) if active_step else -1
    return render_template(
        template,
        active_step=active_step,
        active_index=active_index,
        data=data,
        errors=errors or [],
        factor_info=FACTOR_INFO,
        group_key=group_key,
        rating_labels=RATING_LABELS,
        saved_group=saved_group,
        steps=STEPS,
        table=table,
    )


def save_group_or_show(template, active_step, table, group_key, next_endpoint):
    selection, errors = validate_ratings(request.form, table)
    if errors:
        return render_step(template, active_step, table, group_key, errors)

    if group_key == "scale_factors":
        save_scale_factors(selection)
    else:
        save_effort_group(selection)

    return redirect(url_for(next_endpoint))


@bp.get("/")
def index():
    return render_template("index.html", active_step=None, active_index=-1, steps=STEPS)


@bp.route("/tamano", methods=["GET", "POST"])
def size():
    if request.method == "POST":
        ksloc, error = validate_ksloc(request.form.get("ksloc"))
        if error:
            return render_step("step_size.html", "size", errors=[error])
        save_project_size(request.form.get("project_name", ""), ksloc)
        return redirect(url_for("wizard.scale"))
    return render_step("step_size.html", "size")


@bp.route("/factores-escala", methods=["GET", "POST"])
def scale():
    if request.method == "POST":
        return save_group_or_show("step_scale.html", "scale", SCALE_FACTORS, "scale_factors", "wizard.product")
    return render_step("step_scale.html", "scale", SCALE_FACTORS, "scale_factors")


@bp.route("/producto", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        return save_group_or_show("step_product.html", "product", PRODUCT_DRIVERS, "effort_multipliers", "wizard.platform")
    return render_step("step_product.html", "product", PRODUCT_DRIVERS, "effort_multipliers")


@bp.route("/plataforma", methods=["GET", "POST"])
def platform():
    if request.method == "POST":
        return save_group_or_show("step_platform.html", "platform", PLATFORM_DRIVERS, "effort_multipliers", "wizard.personnel")
    return render_step("step_platform.html", "platform", PLATFORM_DRIVERS, "effort_multipliers")


@bp.route("/personal", methods=["GET", "POST"])
def personnel():
    if request.method == "POST":
        return save_group_or_show("step_personnel.html", "personnel", PERSONNEL_DRIVERS, "effort_multipliers", "wizard.project")
    return render_step("step_personnel.html", "personnel", PERSONNEL_DRIVERS, "effort_multipliers")


@bp.route("/proyecto", methods=["GET", "POST"])
def project():
    if request.method == "POST":
        return save_group_or_show("step_project.html", "project", PROJECT_DRIVERS, "effort_multipliers", "wizard.summary")
    return render_step("step_project.html", "project", PROJECT_DRIVERS, "effort_multipliers")


@bp.get("/resumen")
def summary():
    data = get_data()
    return render_template(
        "summary.html",
        active_step="summary",
        active_index=[key for key, _label in STEPS].index("summary"),
        data=data,
        factor_info=FACTOR_INFO,
        rating_labels=RATING_LABELS,
        steps=STEPS,
    )


@bp.post("/calcular")
def calculate():
    cocomo_data = session.get("cocomo_data")

    if not cocomo_data:
        flash("No se encontraron datos para realizar la estimacion.", "danger")
        return redirect(url_for("wizard.index"))

    try:
        result = calculate_cocomo_effort(cocomo_data)
    except (KeyError, TypeError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("wizard.summary"))

    session["cocomo_result"] = result
    session.modified = True

    return redirect(url_for("wizard.results"))


@bp.get("/resultados")
def results():
    result = session.get("cocomo_result")

    if not result:
        flash("Primero debe realizar el calculo de la estimacion.", "warning")
        return redirect(url_for("wizard.summary"))

    return render_template(
        "results.html",
        active_step="results",
        active_index=[key for key, _label in STEPS].index("results"),
        result=result,
        steps=STEPS,
    )


@bp.post("/reiniciar")
def reset():
    session.pop("cocomo_data", None)
    session.pop("cocomo_result", None)
    return redirect(url_for("wizard.index"))
