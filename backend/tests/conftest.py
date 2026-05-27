import os
import tempfile

import pytest

# Use a throwaway SQLite file and force mock LLM mode before app import.
os.environ.pop("ANTHROPIC_API_KEY", None)
_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
