from app.services.allocation_engine import AllocationEngine


def test_allocation_runs(session):
    engine = AllocationEngine(session)
    result = engine.allocate()
    assert "wide" in result
    assert len(result["wide"]) > 0
    assert any(row for row in result["long"] if row["Kind"] in {"Water", "General", "Check"})


def test_check_rotation_prefers_checker(session):
    engine = AllocationEngine(session)
    result = engine.allocate()
    water_checks = [row for row in result["long"] if row["Kind"] == "Check"]
    assert water_checks, "Expected check entries"
    assert all("ناجی" in entry["Assignee"] for entry in water_checks[: len(water_checks)])
