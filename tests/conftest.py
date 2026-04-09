from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.db import reset_db
from app.main import app
from app.models.student import StudentCreate


def _default_student_payload() -> dict[str, object]:
    return {
        "firstName": "Neville",
        "lastName": "Longbottom",
        "email": "neville.longbottom@hogwarts.edu",
        "grade": 15.4,
        "field": "physique",
    }


@pytest.fixture(autouse=True)
def reset_database() -> None:
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
