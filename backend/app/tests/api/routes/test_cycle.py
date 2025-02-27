from datetime import date

def test_day_info_valid(client):
    response = client.get("/cycle/day-info?query_date=2024-03-10&cycle_length=28&period_length=5&include_details=true")
    assert response.status_code == 200
    data = response.json()
    assert "cycleDay" in data
    assert "phase" in data
    assert "date" in data

def test_day_info_default_values(client):
    response = client.get("/cycle/day-info")
    assert response.status_code == 200
    data = response.json()
    assert "cycleDay" in data
    assert "phase" in data
    assert "date" in data

def test_invalid_cycle_length(client):
    response = client.get("/cycle/day-info?cycle_length=40")  # Invalid (above 35)
    assert response.status_code == 422  # FastAPI's auto-validation

def test_invalid_period_length(client):
    response = client.get("/cycle/day-info?period_length=0")  # Invalid (less than 1)
    assert response.status_code == 422  # FastAPI validation

def test_future_last_period_start_date(client):
    future_date = (date.today().replace(year=date.today().year + 1)).isoformat()
    response = client.get(f"/cycle/day-info?last_period_start_date={future_date}")
    assert response.status_code == 400  # Our custom validation
    assert response.json()["detail"] == "The last period start date cannot be in the future."
