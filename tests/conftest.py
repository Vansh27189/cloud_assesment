"""Pytest test configuration and fixtures."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure workspace root is at top of python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app
from app.services.task_store import task_store


@pytest.fixture(scope="session")
def client():
    """Create a persistent FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_task_store():
    """Ensure task store is clean for independent test runs."""
    task_store.clear()
    yield
    task_store.clear()
