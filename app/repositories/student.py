import sqlite3

from app.db import get_connection
from app.exceptions.student import (
    StudentEmailAlreadyExistsError,
    StudentNotFoundError,
)
from app.models.student import Student, StudentCreate

SORT_COLUMNS = {
    "id": "id",
    "firstName": "firstName",
    "lastName": "lastName",
    "email": "email",
    "grade": "grade",
    "field": "field",
}

SORT_ORDERS = {"asc": "ASC", "desc": "DESC"}


def list_students(
    page: int = 1,
    limit: int = 10,
    sort: str = "id",
    order: str = "asc",
) -> list[Student]:
    offset = (page - 1) * limit
    sort_column = SORT_COLUMNS[sort]
    sort_order = SORT_ORDERS[order]
    query = """
    SELECT id, firstName, lastName, email, grade, field
    FROM students
    ORDER BY {sort_column} {sort_order}, id ASC
    LIMIT ? OFFSET ?
    """.format(sort_column=sort_column, sort_order=sort_order)
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, (limit, offset)).fetchall()

    return [Student(**dict(row)) for row in rows]


def get_student_by_id(student_id: int) -> Student | None:
    query = """
    SELECT id, firstName, lastName, email, grade, field
    FROM students
    WHERE id = ?
    """
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(query, (student_id,)).fetchone()

    if row is None:
        return None

    return Student(**dict(row))


def create_student(student: StudentCreate) -> Student:
    query = """
    INSERT INTO students (firstName, lastName, email, grade, field)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    student.firstName,
                    student.lastName,
                    student.email,
                    student.grade,
                    student.field,
                ),
            )
            created_student_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        if "students.email" in str(exc):
            raise StudentEmailAlreadyExistsError() from exc
        raise  # pragma: no cover

    created_student = get_student_by_id(created_student_id)
    if created_student is None:
        raise RuntimeError("created student could not be retrieved")

    return created_student


def update_student(student_id: int, student: StudentCreate) -> Student:
    query = """
    UPDATE students
    SET firstName = ?, lastName = ?, email = ?, grade = ?, field = ?
    WHERE id = ?
    """
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                query,
                (
                    student.firstName,
                    student.lastName,
                    student.email,
                    student.grade,
                    student.field,
                    student_id,
                ),
            )
            if cursor.rowcount == 0:
                raise StudentNotFoundError()
    except sqlite3.IntegrityError as exc:
        if "students.email" in str(exc):
            raise StudentEmailAlreadyExistsError() from exc
        raise  # pragma: no cover

    updated_student = get_student_by_id(student_id)
    if updated_student is None:
        raise RuntimeError("updated student could not be retrieved")

    return updated_student


def delete_student(student_id: int) -> None:
    query = """
    DELETE FROM students
    WHERE id = ?
    """
    with get_connection() as connection:
        cursor = connection.execute(query, (student_id,))
        if cursor.rowcount == 0:
            raise StudentNotFoundError()


def get_students_stats() -> dict[str, object]:
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        total_and_average_row = connection.execute(
            "SELECT COUNT(*) AS total, AVG(grade) AS average FROM students"
        ).fetchone()

        fields_rows = connection.execute(
            "SELECT field, COUNT(*) AS total FROM students GROUP BY field"
        ).fetchall()

        best_student_row = connection.execute(
            """
            SELECT id, firstName, lastName, email, grade, field
            FROM students
            ORDER BY grade DESC, id ASC
            LIMIT 1
            """
        ).fetchone()

    total_students = int(total_and_average_row["total"])
    average_grade_value = total_and_average_row["average"]
    average_grade = (
        round(float(average_grade_value), 2)
        if average_grade_value is not None
        else 0.0
    )

    students_by_field = {
        "informatique": 0,
        "mathématiques": 0,
        "physique": 0,
        "chimie": 0,
    }
    for row in fields_rows:
        students_by_field[row["field"]] = int(row["total"])

    best_student = (
        Student(**dict(best_student_row))
        if best_student_row is not None
        else None
    )

    return {
        "totalStudents": total_students,
        "averageGrade": average_grade,
        "studentsByField": students_by_field,
        "bestStudent": best_student,
    }


def search_students(query: str) -> list[Student]:
    normalized_query = query.strip().lower()
    like_term = f"%{normalized_query}%"
    search_query = """
    SELECT id, firstName, lastName, email, grade, field
    FROM students
    WHERE LOWER(firstName) LIKE ? OR LOWER(lastName) LIKE ?
    ORDER BY id ASC
    """

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            search_query, (like_term, like_term)
        ).fetchall()

    return [Student(**dict(row)) for row in rows]
