import pytest
import importlib
from pathlib import Path

# fixture to use a temporary sqlite db for tests
@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_app.db"
    # monkeypatch the DB_PATH used by the connection module
    monkeypatch.setenv("APP_TEST_DB", str(db_file))
    # Some modules read database.connection.DB_PATH at import time; set it explicitly
    import database.connection as conn_mod
    monkeypatch.setattr(conn_mod, "DB_PATH", str(db_file))

    # Re-init DB schema
    import database.schema as schema_mod
    importlib.reload(schema_mod)
    schema_mod.init_db()
    yield str(db_file)

    # cleanup
    try:
        Path(str(db_file)).unlink()
    except Exception:
        pass
