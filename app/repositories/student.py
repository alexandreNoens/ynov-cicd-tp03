import psycopg2
from psycopg2 import errorcodes
from psycopg2.extras import RealDictCursor

from app.db import get_connection
from app.exceptions.student import (
    StudentEmailAlreadyExistsError,
    StudentNotFoundError,
)
from app.models.student import Student, StudentCreate

SORT_COLUMNS = {
    "id": "id",
    "first_name": "first_name",
    "last_name": "last_name",
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
    SELECT id,
           first_name,
           last_name,
           email, grade, field
    FROM students
    ORDER BY {sort_column} {sort_order}, id ASC
    LIMIT %s OFFSET %s
    """.format(sort_column=sort_column, sort_order=sort_order)
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()

    return [Student(**dict(row)) for row in rows]


def get_student_by_id(student_id: int) -> Student | None:
    query = """
    SELECT id,
           first_name,
           last_name,
           email, grade, field
    FROM students
    WHERE id = %s
    """
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (student_id,))
            row = cursor.fetchone()

    if row is None:
        return None

    return Student(**dict(row))


def create_student(student: StudentCreate) -> Student:
    query = """
    INSERT INTO students (first_name, last_name, email, grade, field)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        student.first_name,
                        student.last_name,
                        student.email,
                        student.grade,
                        student.field,
                    ),
                )
                created_student_id = cursor.fetchone()[0]
    except psycopg2.IntegrityError as exc:
        if exc.pgcode == errorcodes.UNIQUE_VIOLATION:
            raise StudentEmailAlreadyExistsError() from exc
        raise  # pragma: no cover

    created_student = get_student_by_id(created_student_id)
    if created_student is None:
        raise RuntimeError("created student could not be retrieved")

    return created_student


def update_student(student_id: int, student: StudentCreate) -> Student:
    query = """
    UPDATE students
    SET first_name = %s, last_name = %s, email = %s, grade = %s, field = %s
    WHERE id = %s
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        student.first_name,
                        student.last_name,
                        student.email,
                        student.grade,
                        student.field,
                        student_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise StudentNotFoundError()
    except psycopg2.IntegrityError as exc:
        if exc.pgcode == errorcodes.UNIQUE_VIOLATION:
            raise StudentEmailAlreadyExistsError() from exc
        raise  # pragma: no cover

    updated_student = get_student_by_id(student_id)
    if updated_student is None:
        raise RuntimeError("updated student could not be retrieved")

    return updated_student


def delete_student(student_id: int) -> None:
    query = """
    DELETE FROM students
    WHERE id = %s
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (student_id,))
            if cursor.rowcount == 0:
                raise StudentNotFoundError()


def get_students_stats() -> dict[str, object]:
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS total, AVG(grade) AS average FROM students"
            )
            total_and_average_row = cursor.fetchone()

            cursor.execute(
                "SELECT field, COUNT(*) AS total FROM students GROUP BY field"
            )
            fields_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT id,
                       first_name,
                       last_name,
                       email, grade, field
                FROM students
                ORDER BY grade DESC, id ASC
                LIMIT 1
                """
            )
            best_student_row = cursor.fetchone()

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
    SELECT id,
           first_name,
           last_name,
           email, grade, field
    FROM students
    WHERE LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s
    ORDER BY id ASC
    """

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(search_query, (like_term, like_term))
            rows = cursor.fetchall()

    return [Student(**dict(row)) for row in rows]
