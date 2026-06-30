from cocomo import create_app


def test_results_requires_previous_calculation():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")

    with app.test_client() as client:
        response = client.get("/resultados")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/resumen")
