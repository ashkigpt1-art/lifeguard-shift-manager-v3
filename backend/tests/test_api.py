from fastapi.testclient import TestClient


def test_health(client: TestClient):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_lifeguard_crud(client: TestClient):
    payload = {
        "name": "تست",
        "experience": "medium",
        "present": True,
        "role": "ناجی",
        "lunch_at": "-",
        "backup_name": "-",
        "swap_at": "-",
    }
    create = client.post("/api/v1/lifeguards", json=payload)
    assert create.status_code == 200
    guard_id = create.json()["id"]

    update = client.put(f"/api/v1/lifeguards/{guard_id}", json={"team": "B"})
    assert update.status_code == 200
    assert update.json()["team"] == "B"

    delete = client.delete(f"/api/v1/lifeguards/{guard_id}")
    assert delete.status_code == 200


def test_allocate_endpoint(client: TestClient):
    resp = client.post("/api/v1/allocate")
    assert resp.status_code == 200
    data = resp.json()
    assert "wide" in data and "long" in data
    assert data["caption"].startswith("تاریخ")
