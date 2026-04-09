import json
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

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

router = APIRouter(tags=["students"])


@router.get("/students", response_model=list[Student])
def get_students(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    sort: Literal[
        "id",
        "firstName",
        "lastName",
        "email",
        "grade",
        "field",
    ] = "id",
    order: Literal["asc", "desc"] = "asc",
) -> list[Student]:
    return list_students(page=page, limit=limit, sort=sort, order=order)


@router.get("/students/search", response_model=list[Student])
def get_students_search(q: str | None = Query(default=None)) -> list[Student]:
    if q is None or not q.strip():
        raise HTTPException(
            status_code=400, detail="query parameter q is required"
        )

    return search_students(q)


@router.post("/students", response_model=Student, status_code=201)
def post_student(payload: dict[str, Any]) -> Student:
    try:
        student_to_create = StudentCreate(**payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=json.loads(exc.json())
        ) from exc

    try:
        return create_student(student_to_create)
    except StudentEmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="student email already exists",
        ) from exc


@router.put("/students/{student_id}", response_model=Student)
def put_student(student_id: str, payload: dict[str, Any]) -> Student:
    try:
        parsed_student_id = int(student_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="student id must be a valid number",
        ) from exc

    try:
        student_to_update = StudentCreate(**payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=400, detail=json.loads(exc.json())
        ) from exc

    try:
        return update_student(parsed_student_id, student_to_update)
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail="student not found"
        ) from exc
    except StudentEmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="student email already exists",
        ) from exc


@router.get("/students/stats")
def get_students_stats_route() -> dict[str, object]:
    return get_students_stats()


@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str) -> Student:
    try:
        parsed_student_id = int(student_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="student id must be a valid number",
        ) from exc

    student = get_student_by_id(parsed_student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="student not found")

    return student


@router.delete("/students/{student_id}")
def delete_student_by_id(student_id: str) -> dict[str, str]:
    try:
        parsed_student_id = int(student_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="student id must be a valid number",
        ) from exc

    try:
        delete_student(parsed_student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail="student not found"
        ) from exc

    return {"message": "student deleted"}
