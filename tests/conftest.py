import os
from typing import NoReturn

import pytest

from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session")
def initialize_test_db(request) -> NoReturn:
    """
    A fixture for testing the database.
    """

    db_url = os.environ.get("DATABASE_URL", "sqlite://:memory:")
    initializer(["database.user.models"], db_url=db_url, app_label="models")
    request.addfinalizer(finalizer)
