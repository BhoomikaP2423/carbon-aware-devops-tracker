from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def setup_function():
    main.builds.clear()
    main.deployments.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_carbon_calculation():
    client.post("/builds?duration_seconds=3600&cpu_cores=1")
    response = client.get("/carbon-report")
    assert response.json()["estimated_build_carbon_kg"] == 0.0455


def test_optimize_recommends_replicas():
    client.post("/deployments?replica_count=3&duration_seconds=3600")
    response = client.get("/optimize")
    assert response.json()["recommended_replicas"] == 3