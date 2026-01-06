import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.pmot import create_random_pmot


def test_create_pmot(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters", "short_story": "A story"}
    response = client.post(
        f"{settings.API_V1_STR}/pmots/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_pmot(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    response = client.get(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == pmot.title
    assert content["description"] == pmot.description
    assert content["id"] == str(pmot.id)
    assert content["owner_id"] == str(pmot.owner_id)


def test_read_pmot_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/pmots/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "PMOT not found"


def test_read_pmot_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    response = client.get(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_pmots(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_pmot(db)
    create_random_pmot(db)
    response = client.get(
        f"{settings.API_V1_STR}/pmots/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_pmot(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(pmot.id)
    assert content["owner_id"] == str(pmot.owner_id)


def test_update_pmot_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/pmots/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "PMOT not found"


def test_update_pmot_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_pmot(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    response = client.delete(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "PMOT deleted successfully"


def test_delete_pmot_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/pmots/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "PMOT not found"


def test_delete_pmot_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    pmot = create_random_pmot(db)
    response = client.delete(
        f"{settings.API_V1_STR}/pmots/{pmot.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
