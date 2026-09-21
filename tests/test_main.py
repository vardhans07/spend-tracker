import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_expense_success():
    response = client.post("/expenses", json={
        "amount": 250.0,
        "category": "Groceries",
        "date": "2026-09-15",
        "note": "Supermarket"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 250.0
    assert data["category"] == "Groceries"
    assert "id" in data

def test_create_expense_validation_error():
    # Negative amount should fail
    response = client.post("/expenses", json={
        "amount": -50.0,
        "category": "Groceries",
        "date": "2026-09-15"
    })
    assert response.status_code == 422

def test_filter_expenses_and_date_validation():
    client.post("/expenses", json={"amount": 100, "category": "Food", "date": "2026-09-01"})
    client.post("/expenses", json={"amount": 200, "category": "Travel", "date": "2026-09-10"})

    # Filter by category
    res = client.get("/expenses?category=Food")
    assert len(res.json()) == 1
    assert res.json()[0]["category"] == "Food"

    # Start date after end date should fail
    invalid_range = client.get("/expenses?start_date=2026-09-15&end_date=2026-09-01")
    assert invalid_range.status_code == 400

def test_summary_aggregations():
    client.post("/expenses", json={"amount": 100.0, "category": "Food", "date": "2026-09-01"})
    client.post("/expenses", json={"amount": 50.0, "category": "Food", "date": "2026-09-05"})
    client.post("/expenses", json={"amount": 75.0, "category": "Utilities", "date": "2026-09-06"})

    res = client.get("/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_spend"] == 225.0
    assert data["by_category"]["Food"] == 150.0
    assert data["by_category"]["Utilities"] == 75.0
