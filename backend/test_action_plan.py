import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

from app.database.connection import get_db
from app.database.base import Base

# Setup In-Memory SQLite for Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_action_plan_flow():
    # 1. Create a case
    case_data = {
        "title": "Breach of Employment Contract",
        "description": "The employer terminated the contract without paying the agreed severance.",
        "legal_domain": "Employment Law"
    }
    response = client.post("/api/cases", json=case_data)
    assert response.status_code == 201
    case_id = response.json()["id"]

    # 2. Generate action plan (baseline with missing downstream data)
    response = client.post(f"/api/cases/{case_id}/generate-action-plan")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0
    
    # 3. Verify ordering and structure
    for idx, step in enumerate(results):
        assert "action_title" in step
        assert "sequence_order" in step
        # Make sure they are returned in order
        if idx > 0:
            assert step["sequence_order"] >= results[idx-1]["sequence_order"]
    
    # 4. Retrieve action plan
    response = client.get(f"/api/cases/{case_id}/action-plan")
    assert response.status_code == 200
    retrieved = response.json()
    assert len(retrieved) == len(results)
    if len(retrieved) > 0:
        assert retrieved[0]["action_title"] == results[0]["action_title"]

def test_action_plan_invalid_case():
    response = client.post("/api/cases/999/generate-action-plan")
    assert response.status_code == 400

    response = client.get("/api/cases/999/action-plan")
    assert response.status_code == 404
