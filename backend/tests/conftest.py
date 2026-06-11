import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.app.api.deps import get_db
from backend.app.db.database import Base, engine
from backend.app.services.twilio_verify import twilio_verify_service

# Create all tables (in case they don't exist, though migration has run)
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Fixture that provides a database session that rolls back all operations
    after the test executes, ensuring a clean state.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """
    Fixture that provides a FastAPI TestClient with database session override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_twilio_verify(monkeypatch):
    """
    Automatically mock Twilio Verify service for all tests.
    """
    monkeypatch.setattr(twilio_verify_service, "send_otp", lambda phone, channel="sms": "pending")
    monkeypatch.setattr(twilio_verify_service, "verify_otp", lambda phone, code: code == "123456")
