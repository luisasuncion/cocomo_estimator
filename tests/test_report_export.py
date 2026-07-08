from datetime import datetime

from cocomo import create_app
from cocomo.report_service import build_report_context, build_report_filename, sanitize_filename
from cocomo.services import calculate_cocomo_final
from tests.test_services import example_cocomo_data


def complete_report_data():
    data = example_cocomo_data()
    data["project_name"] = "Sistema Web Medicamentos / HRDT 2026"
    data["average_monthly_salary"] = 2500.0
    data["currency"] = "PEN"
    return data, calculate_cocomo_final(data)


def test_export_without_session_redirects_to_summary():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        response = client.get("/exportar-reporte")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/resumen")


def test_export_with_incomplete_data_redirects_to_summary():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cocomo_data"] = {"project_name": "Proyecto incompleto"}
            session["cocomo_result"] = {}

        response = client.get("/exportar-reporte")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/resumen")


def test_export_with_valid_results_returns_pdf():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")
    data, result = complete_report_data()

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cocomo_data"] = data
            session["cocomo_result"] = result

        response = client.get("/exportar-reporte")

    assert response.status_code == 200
    assert response.content_type == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_export_content_disposition_uses_sanitized_filename():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")
    data, result = complete_report_data()

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cocomo_data"] = data
            session["cocomo_result"] = result

        response = client.get("/exportar-reporte")

    disposition = response.headers["Content-Disposition"]
    assert "attachment;" in disposition
    assert "reporte_cocomo_ii_sistema_web_medicamentos_hrdt_2026_" in disposition
    assert disposition.endswith('.pdf"')


def test_sanitize_filename_removes_dangerous_characters():
    assert sanitize_filename("../Sistema Clínico: Medicamentos 2026!") == "sistema_clinico_medicamentos_2026"


def test_build_report_filename_uses_date():
    filename = build_report_filename("Sistema X", datetime(2026, 7, 4, 10, 30))
    assert filename == "reporte_cocomo_ii_sistema_x_2026-07-04.pdf"


def test_report_context_includes_project_name_and_ksloc():
    data, result = complete_report_data()
    report = build_report_context(data, result)

    assert report["project_name"] == "Sistema Web Medicamentos / HRDT 2026"
    assert report["ksloc"] == result["ksloc"]


def test_report_context_includes_e_and_eaf():
    data, result = complete_report_data()
    report = build_report_context(data, result)

    assert report["result"]["exponent_e"] == result["exponent_e"]
    assert report["result"]["eaf"] == result["eaf"]


def test_report_context_includes_pm_tdev_and_cost():
    data, result = complete_report_data()
    report = build_report_context(data, result)

    assert report["result"]["effort_pm"] == result["effort_pm"]
    assert report["result"]["tdev_months"] == result["tdev_months"]
    assert report["result"]["total_cost"] == result["total_cost"]


def test_report_context_includes_sensitivity():
    data, result = complete_report_data()
    report = build_report_context(data, result)

    assert len(report["result"]["size_sensitivity"]) == 3
    assert len(report["result"]["salary_sensitivity"]) == 3


def test_report_context_translates_ratings():
    data, result = complete_report_data()
    report = build_report_context(data, result)

    assert report["scale_factors"][0]["rating_label"] == "Nominal (NM)"
    assert report["scale_factors"][1]["rating_label"] == "Bajo (LO)"
