from collections.abc import Callable

from fastapi.testclient import TestClient


def test_get_students_returns_json_array_with_status_200(
    client: TestClient,
) -> None:
    response = client.get("/students")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload == [
        {
            "id": 1,
            "firstName": "Harry",
            "lastName": "Potter",
            "email": "harry.potter@hogwarts.edu",
            "grade": 17.5,
            "field": "informatique",
        },
        {
            "id": 2,
            "firstName": "Hermione",
            "lastName": "Granger",
            "email": "hermione.granger@hogwarts.edu",
            "grade": 19.8,
            "field": "mathématiques",
        },
        {
            "id": 3,
            "firstName": "Ron",
            "lastName": "Weasley",
            "email": "ron.weasley@hogwarts.edu",
            "grade": 14.2,
            "field": "chimie",
        },
        {
            "id": 4,
            "firstName": "Luna",
            "lastName": "Lovegood",
            "email": "luna.lovegood@hogwarts.edu",
            "grade": 16.1,
            "field": "physique",
        },
        {
            "id": 5,
            "firstName": "Draco",
            "lastName": "Malfoy",
            "email": "draco.malfoy@hogwarts.edu",
            "grade": 13.7,
            "field": "informatique",
        },
    ]


def test_get_students_pagination_returns_first_page(
    client: TestClient,
) -> None:
    response = client.get("/students?page=1&limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["id"] == 1
    assert payload[1]["id"] == 2


def test_get_students_pagination_returns_second_page(
    client: TestClient,
) -> None:
    response = client.get("/students?page=2&limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["id"] == 3
    assert payload[1]["id"] == 4


def test_get_students_sort_by_grade_desc_returns_expected_order(
    client: TestClient,
) -> None:
    response = client.get("/students?sort=grade&order=desc")

    assert response.status_code == 200
    payload = response.json()
    assert [student["firstName"] for student in payload] == [
        "Hermione",
        "Harry",
        "Luna",
        "Ron",
        "Draco",
    ]


def test_get_students_search_returns_200_with_case_insensitive_matches(
    client: TestClient,
) -> None:
    response = client.get("/students/search?q=grAn")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["firstName"] == "Hermione"


def test_get_students_search_returns_400_when_q_is_missing(
    client: TestClient,
) -> None:
    response = client.get("/students/search")

    assert response.status_code == 400
    assert response.json() == {"detail": "query parameter q is required"}


def test_get_students_search_returns_400_when_q_is_empty(
    client: TestClient,
) -> None:
    response = client.get("/students/search?q=   ")

    assert response.status_code == 400
    assert response.json() == {"detail": "query parameter q is required"}


def test_get_students_stats_returns_200_and_expected_stats(
    client: TestClient,
) -> None:
    response = client.get("/students/stats")

    assert response.status_code == 200
    payload = response.json()
    assert payload["totalStudents"] == 5
    assert payload["averageGrade"] == 16.26
    assert payload["studentsByField"] == {
        "informatique": 2,
        "mathématiques": 1,
        "physique": 1,
        "chimie": 1,
    }
    assert payload["bestStudent"]["firstName"] == "Hermione"
    assert payload["bestStudent"]["grade"] == 19.8


def test_get_student_returns_json_object_with_status_200_when_found(
    client: TestClient,
) -> None:
    response = client.get("/students/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["firstName"] == "Harry"


def test_get_student_returns_404_when_id_does_not_exist(
    client: TestClient,
) -> None:
    response = client.get("/students/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "student not found"}


def test_get_student_returns_400_when_id_is_not_a_valid_number(
    client: TestClient,
) -> None:
    response = client.get("/students/not-a-number")

    assert response.status_code == 400
    assert response.json() == {"detail": "student id must be a valid number"}


def test_post_student_returns_201_and_created_student(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post("/students", json=student_payload_factory())

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 6
    assert payload["firstName"] == "Neville"
    assert payload["email"] == "neville.longbottom@hogwarts.edu"


def test_post_student_returns_400_when_a_required_field_is_missing(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    payload = student_payload_factory()
    payload.pop("email")
    response = client.post("/students", json=payload)

    assert response.status_code == 400


def test_post_student_returns_400_when_first_name_is_too_short(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post(
        "/students", json=student_payload_factory(firstName="N")
    )

    assert response.status_code == 400


def test_post_student_returns_400_when_last_name_is_too_short(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post(
        "/students", json=student_payload_factory(lastName="L")
    )

    assert response.status_code == 400


def test_post_student_returns_400_when_email_is_invalid(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post(
        "/students",
        json=student_payload_factory(email="invalid-email"),
    )

    assert response.status_code == 400


def test_post_student_returns_409_when_email_already_exists(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post(
        "/students",
        json=student_payload_factory(email="harry.potter@hogwarts.edu"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "student email already exists"}


def test_post_student_returns_400_when_grade_is_below_range(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post("/students", json=student_payload_factory(grade=-1))

    assert response.status_code == 400


def test_post_student_returns_400_when_grade_is_above_range(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post("/students", json=student_payload_factory(grade=21))

    assert response.status_code == 400


def test_post_student_returns_400_when_field_is_invalid(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post(
        "/students",
        json=student_payload_factory(field="biologie"),
    )

    assert response.status_code == 400


def test_put_student_returns_200_and_updated_student_when_successful(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.put(
        "/students/1",
        json=student_payload_factory(
            firstName="Harry",
            lastName="Potter",
            email="harry.j.potter@hogwarts.edu",
            grade=18.5,
            field="physique",
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["email"] == "harry.j.potter@hogwarts.edu"
    assert payload["grade"] == 18.5
    assert payload["field"] == "physique"


def test_put_student_returns_404_when_id_does_not_exist(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.put("/students/999", json=student_payload_factory())

    assert response.status_code == 404
    assert response.json() == {"detail": "student not found"}


def test_put_student_returns_400_when_id_is_not_a_valid_number(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.put(
        "/students/not-a-number", json=student_payload_factory()
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "student id must be a valid number"}


def test_put_student_returns_400_when_payload_is_invalid(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.put(
        "/students/1",
        json=student_payload_factory(firstName="N"),
    )

    assert response.status_code == 400


def test_put_student_returns_409_when_email_already_exists(
    client: TestClient,
    student_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.put(
        "/students/1",
        json=student_payload_factory(email="hermione.granger@hogwarts.edu"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "student email already exists"}


def test_delete_student_returns_200_with_confirmation_message(
    client: TestClient,
) -> None:
    response = client.delete("/students/1")

    assert response.status_code == 200
    assert response.json() == {"message": "student deleted"}


def test_delete_student_returns_404_when_id_does_not_exist(
    client: TestClient,
) -> None:
    response = client.delete("/students/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "student not found"}


def test_delete_student_returns_400_when_id_is_not_a_valid_number(
    client: TestClient,
) -> None:
    response = client.delete("/students/not-a-number")

    assert response.status_code == 400
    assert response.json() == {"detail": "student id must be a valid number"}
