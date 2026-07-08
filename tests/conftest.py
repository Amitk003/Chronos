import os
import pytest

from app import storage, scheduler

TEST_DB = "test_chronos.db"


@pytest.fixture(autouse=True, scope="session")
def setup_test_env():
    for f in [TEST_DB, "chronos.db", "chronos_jobs.sqlite"]:
        if os.path.exists(f):
            os.remove(f)

    old_db_path = storage.get_db_path()
    storage.set_db_path(TEST_DB)
    scheduler.start("sqlite://")

    yield

    scheduler.shutdown()
    storage.set_db_path(old_db_path)
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass
