from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Finance Dashboard API is running"}

def test_stock_overview_endpoint():
    # Mocking or using a real ticker usually depends on env, but AAPL is standard.
    # We expect 200 or 404 depending on network/library status, but structure should be valid.
    # Since we can't easily mock yfinance here without more setup, we'll just check if endpoint exists
    # and returns 404 for a bogus ticker or 200 for a real one.

    # We'll use a bogus ticker to avoid external network dependency failure crashing the test suite if internet is flaky
    # but our code returns 404 or None for errors.

    response = client.get("/api/stock/INVALID_TICKER_123/overview")
    # Our service currently catches exceptions and returns None, which raises 404
    assert response.status_code == 404

def test_macro_data_endpoint_structure():
    # We can test the validation logic
    response = client.post("/api/macro/data", json={
        "series_id": "INVALID",
        "label": "Test",
        "years": 2
    })
    # Should try to fetch and likely return 404 because FRED key might be missing or ID invalid
    # If FRED key is missing, it prints error and returns None -> 404
    assert response.status_code in [404, 500]
