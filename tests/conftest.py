from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import reset_db
from app.main import app
from app.models.student import StudentCreate


def _default_student_payload() -> dict[str, object]:
    return {
        "first_name": "neville",
        "last_name": "longbottom",
        "email": "neville.longbottom@hogwarts.edu",
        "grade": 15.4,
        "field": "physique",
    }


def _requires_database(request: pytest.FixtureRequest) -> bool:
    test_path = Path(str(request.node.fspath))
    return test_path.parent.name in {
        "repositories",
        "routes",
    } or test_path.name in {
        "test_health.py",
        "test_lifespan.py",
    }


@pytest.fixture(autouse=True)
def reset_database(request: pytest.FixtureRequest) -> None:
    if not _requires_database(request):
        return

    reset_db()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def student_payload_factory() -> Callable[..., dict[str, object]]:
    def make_payload(**overrides: object) -> dict[str, object]:
        payload = _default_student_payload()
        payload.update(overrides)
        return payload

    return make_payload


@pytest.fixture
def student_create_factory() -> Callable[..., StudentCreate]:
    def make_student(**overrides: object) -> StudentCreate:
        payload = _default_student_payload()
        payload.update(overrides)
        return StudentCreate(**payload)

    return make_student
