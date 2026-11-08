"""Pytest fixtures for API integration testing."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a reusable FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client

