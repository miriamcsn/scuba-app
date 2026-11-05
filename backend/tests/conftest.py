import os
import sys
import tempfile
from pathlib import Path

import pytest

# Os testes rodam com SQLite num arquivo temporário: não precisam de MySQL.
# A variável precisa estar definida antes de importar o app, porque o engine
# do banco é criado no import de app.database.
TEST_DB = Path(tempfile.gettempdir()) / "scuba-test.db"
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{TEST_DB}")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def client():
    if TEST_DB.exists():
        TEST_DB.unlink()

    from fastapi.testclient import TestClient
    from app.main import app

    # O "with" dispara o evento de startup, que cria as tabelas.
    with TestClient(app) as test_client:
        yield test_client
