import os
import pytest

from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = os.environ.get("DATABASE_URL", "sqlite://:memory:")
    initializer(["database.user.models"], db_url=db_url, app_label="models")
    request.addfinalizer(finalizer)
