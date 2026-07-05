from cocomo import create_app
from tests.test_services import example_cocomo_data


def test_results_requires_previous_calculation():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        response = client.get("/resultados")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/resumen")


def test_economics_persists_salary_in_session():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cocomo_data"] = example_cocomo_data()

        response = client.post("/calcular")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/costos")

        response = client.post(
            "/costos",
            data={"average_monthly_salary": "2500.00", "currency": "PEN"},
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/resultados")

        with client.session_transaction() as session:
            assert session["cocomo_data"]["average_monthly_salary"] == 2500.0
            assert session["cocomo_data"]["currency"] == "PEN"


def test_complete_calculation_stores_final_result():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["cocomo_data"] = example_cocomo_data()

        client.post("/calcular")
        client.post("/costos", data={"average_monthly_salary": "2500", "currency": "PEN"})

        with client.session_transaction() as session:
            result = session["cocomo_result"]

        assert result["effort_pm"] > 0
        assert result["tdev_months"] > 0
        assert result["average_staff"] > 0
        assert result["rounded_staff"] == 4
        assert result["total_cost"] > 0
        assert len(result["size_sensitivity"]) == 3
        assert len(result["salary_sensitivity"]) == 3
