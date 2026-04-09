import pytest
from pydantic import ValidationError

from app.models.student import Student


def student_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "firstName": "Harry",
        "lastName": "Potter",
        "email": "harry.potter@hogwarts.edu",
        "grade": 17.5,
        "field": "informatique",
    }
    payload.update(overrides)
    return payload


def test_id_default_is_none() -> None:
    student = Student(**student_payload())
    assert student.id is None


def test_id_accepts_integer() -> None:
    student = Student(**student_payload(id=10))
    assert student.id == 10


def test_first_name_valid() -> None:
    student = Student(**student_payload(firstName="Albus"))
    assert student.firstName == "Albus"


def test_first_name_too_short_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(firstName="A"))


def test_last_name_valid() -> None:
    student = Student(**student_payload(lastName="Granger"))
    assert student.lastName == "Granger"


def test_last_name_too_short_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(lastName="G"))


def test_email_valid() -> None:
    student = Student(**student_payload(email="luna.lovegood@hogwarts.edu"))
    assert student.email == "luna.lovegood@hogwarts.edu"


def test_email_invalid_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(email="invalid-email"))


@pytest.mark.parametrize("grade", [0, 20, 14.5])
def test_grade_valid_values(grade: float) -> None:
    student = Student(**student_payload(grade=grade))
    assert student.grade == grade


@pytest.mark.parametrize("grade", [-0.1, 20.1])
def test_grade_out_of_range_raises_error(grade: float) -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(grade=grade))


@pytest.mark.parametrize(
    "field", ["informatique", "mathématiques", "physique", "chimie"]
)
def test_field_valid_values(field: str) -> None:
    student = Student(**student_payload(field=field))
    assert student.field == field


def test_field_invalid_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(field="biologie"))
