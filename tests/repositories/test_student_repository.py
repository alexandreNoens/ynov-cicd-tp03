from collections.abc import Callable

import pytest

from app.db import get_connection
from app.exceptions.student import (
    StudentEmailAlreadyExistsError,
    StudentNotFoundError,
)
from app.models.student import Student, StudentCreate
from app.repositories.student import (
    create_student,
    delete_student,
    get_student_by_id,
    get_students_stats,
    list_students,
    search_students,
    update_student,
)


def test_list_students_returns_students_ordered_by_id() -> None:
    students = list_students()

    assert isinstance(students, list)
    assert len(students) == 5
    assert all(isinstance(student, Student) for student in students)
    assert [student.id for student in students] == [1, 2, 3, 4, 5]
    assert students[0].firstName == "Harry"
    assert students[1].firstName == "Hermione"


def test_get_student_by_id_returns_student_when_found() -> None:
    student = get_student_by_id(1)

    assert isinstance(student, Student)
    assert student.id == 1
    assert student.firstName == "Harry"


def test_get_student_by_id_returns_none_when_missing() -> None:
    student = get_student_by_id(999)

    assert student is None


def test_create_student_returns_created_student_with_generated_id(
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    created_student = create_student(student_create_factory())

    assert isinstance(created_student, Student)
    assert created_student.id == 6
    assert created_student.firstName == "Neville"
    assert created_student.email == "neville.longbottom@hogwarts.edu"


def test_create_student_raises_error_when_email_already_exists(
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    with pytest.raises(StudentEmailAlreadyExistsError):
        create_student(
            student_create_factory(
                firstName="Harry",
                lastName="Potter",
                email="harry.potter@hogwarts.edu",
                grade=18,
                field="informatique",
            )
        )


def test_update_student_returns_updated_student_when_found(
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    updated_student = update_student(
        1,
        student_create_factory(
            firstName="Harry",
            lastName="Potter",
            email="harry.j.potter@hogwarts.edu",
            grade=18.5,
            field="physique",
        ),
    )

    assert isinstance(updated_student, Student)
    assert updated_student.id == 1
    assert updated_student.email == "harry.j.potter@hogwarts.edu"
    assert updated_student.grade == 18.5
    assert updated_student.field == "physique"


def test_update_student_raises_not_found_when_student_does_not_exist(
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    with pytest.raises(StudentNotFoundError):
        update_student(999, student_create_factory())


def test_update_student_raises_email_conflict_when_email_belongs_to_another(
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    with pytest.raises(StudentEmailAlreadyExistsError):
        update_student(
            1,
            student_create_factory(email="hermione.granger@hogwarts.edu"),
        )


def test_delete_student_removes_student_when_found() -> None:
    delete_student(1)

    student = get_student_by_id(1)

    assert student is None


def test_delete_student_raises_not_found_when_student_does_not_exist() -> None:
    with pytest.raises(StudentNotFoundError):
        delete_student(999)


def test_get_students_stats_returns_expected_aggregates() -> None:
    stats = get_students_stats()

    assert stats["totalStudents"] == 5
    assert stats["averageGrade"] == 16.26
    assert stats["studentsByField"] == {
        "informatique": 2,
        "mathématiques": 1,
        "physique": 1,
        "chimie": 1,
    }
    best_student = stats["bestStudent"]
    assert isinstance(best_student, Student)
    assert best_student.firstName == "Hermione"
    assert best_student.grade == 19.8


def test_search_students_returns_case_insensitive_matches() -> None:
    students = search_students("grAn")

    assert len(students) == 1
    assert students[0].firstName == "Hermione"


def test_search_students_returns_empty_list_when_no_match() -> None:
    students = search_students("xyz")

    assert students == []


def test_get_students_stats_returns_empty_values_when_no_student() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM students")

    stats = get_students_stats()

    assert stats["totalStudents"] == 0
    assert stats["averageGrade"] == 0.0
    assert stats["studentsByField"] == {
        "informatique": 0,
        "mathématiques": 0,
        "physique": 0,
        "chimie": 0,
    }
    assert stats["bestStudent"] is None


def test_create_student_raises_runtime_error_when_created_student_not_found(
    monkeypatch: pytest.MonkeyPatch,
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    monkeypatch.setattr(
        "app.repositories.student.get_student_by_id",
        lambda _student_id: None,
    )

    with pytest.raises(RuntimeError):
        create_student(student_create_factory())


def test_update_student_raises_runtime_error_when_updated_student_not_found(
    monkeypatch: pytest.MonkeyPatch,
    student_create_factory: Callable[..., StudentCreate],
) -> None:
    monkeypatch.setattr(
        "app.repositories.student.get_student_by_id",
        lambda _student_id: None,
    )

    with pytest.raises(RuntimeError):
        update_student(1, student_create_factory())
