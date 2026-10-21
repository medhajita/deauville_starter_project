
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import app
from festival.venues import Venue
from storage import json_storage


@pytest.fixture
def client(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / "data" / "festival.json"
    destination = tmp_path / "festival.json"
    shutil.copyfile(source, destination)
    monkeypatch.setattr(json_storage, "FILE_PATH", destination)
    with TestClient(app) as api_client:
        yield api_client


def test_festival_details(client):
    response = client.get("/api/festival")
    assert response.status_code == 200
    data = response.json()
    assert data["days"] == [
        "2027-06-10", "2027-06-11", "2027-06-12", "2027-06-13"
    ]
    assert data["name"]


def test_venues_are_in_insertion_order(client):
    result = client.get("/api/venues")
    assert result.status_code == 200
    venues = result.json()
    assert len(venues) == 4
    assert all(set(v) == {"slug", "name", "capacity", "address"} for v in venues)


def test_artists_are_sorted(client):
    result = client.get("/api/artists")
    assert result.status_code == 200
    artists = result.json()
    assert len(artists) == 12
    assert [artist["slug"] for artist in artists] == sorted(
        artist["slug"] for artist in artists
    )


def test_artist_details_and_performances(client):
    slug = client.get("/api/artists").json()[0]["slug"]
    response = client.get(f"/api/artists/{slug}")
    assert response.status_code == 200
    assert response.json()["slug"] == slug
    assert isinstance(response.json()["performances"], list)


def test_artist_not_found(client):
    response = client.get("/api/artists/artiste-introuvable")
    assert response.status_code == 404
    assert isinstance(response.json()["detail"], str)


def test_programme_and_filters(client):
    response = client.get("/api/programme")
    assert response.status_code == 200
    programme = response.json()
    assert len(programme) == 23
    assert all("summary" in p and "venue_name" in p for p in programme)

    venue = programme[0]["venue"]
    day = programme[0]["festival_day"]
    response = client.get("/api/programme", params={"day": day, "venue": venue})
    assert response.status_code == 200
    assert all(p["venue"] == venue and p["festival_day"] == day for p in response.json())


def test_programme_invalid_date_is_422(client):
    response = client.get("/api/programme?day=June%2011")
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_programme_unknown_venue_is_404(client):
    response = client.get("/api/programme?venue=salle-inconnue")
    assert response.status_code == 404


def test_performance_details(client):
    performance_id = client.get("/api/programme").json()[0]["id"]
    response = client.get(f"/api/performances/{performance_id}")
    assert response.status_code == 200
    assert response.json()["id"] == performance_id
    assert "end" in response.json()
    assert "capacity" in response.json()


def test_now_returns_three_following_shows_maximum(client):
    response = client.get("/api/now", params={"at": "2027-06-10T20:30"})
    assert response.status_code == 200
    data = response.json()
    assert data["at"] == "2027-06-10T20:30"
    assert isinstance(data["now_playing"], list)
    assert len(data["up_next"]) <= 3


def test_create_artist_and_persist(client):
    response = client.post(
        "/api/artists", json={"name": "Artiste API", "bio": "Test"}
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "artiste-api"
    assert len(json_storage.load_festival().artists) == 13


def test_duplicate_artist_is_409(client):
    body = {"name": "Artiste API"}
    assert client.post("/api/artists", json=body).status_code == 201
    result = client.post("/api/artists", json=body)
    assert result.status_code == 409
    assert len(json_storage.load_festival().artists) == 13


def test_missing_artist_name_is_422(client):
    response = client.post("/api/artists", json={"bio": "Sans nom"})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def _prepare_unique_artist_and_venue(client):
    """Crée une salle et un artiste sans conflit avec le programme officiel."""
    assert client.post("/api/artists", json={"name": "Artiste API", "bio": "Test"}).status_code == 201
    festival = json_storage.load_festival()
    festival.add_venue(Venue("Salle API", 60, "Adresse de test"))
    json_storage.save_festival(festival)


def _solo_body():
    return {
        "kind": "solo",
        "title": "Spectacle API",
        "venue": "salle-api",
        "start": "2027-06-10T12:00",
        "duration_minutes": 40,
        "description": "Créé depuis les tests API",
        "artist": "artiste-api",
        "min_age": 0,
    }


def test_create_performance_and_persist(client):
    _prepare_unique_artist_and_venue(client)
    response = client.post("/api/performances", json=_solo_body())
    assert response.status_code == 201, response.text
    assert response.json()["venue"] == "salle-api"
    assert len(json_storage.load_festival().performances) == 24


def test_reject_readonly_fields_in_performance_body(client):
    body = _solo_body() | {"id": "faux-id"}
    response = client.post("/api/performances", json=body)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_put_invalid_does_not_change_original(client):
    old = client.get("/api/programme").json()[0]
    body = {
        "kind": "solo",
        "title": "Déplacement impossible",
        "venue": "salle-inconnue",
        "start": "2027-06-11T12:00",
        "duration_minutes": 40,
        "artist": client.get("/api/artists").json()[0]["slug"],
        "min_age": 0,
    }
    response = client.put(f"/api/performances/{old['id']}", json=body)
    assert response.status_code == 404
    after = client.get(f"/api/performances/{old['id']}")
    assert after.status_code == 200
    assert after.json() == old
    assert len(client.get("/api/programme").json()) == 23


def test_put_can_move_and_change_id(client):
    _prepare_unique_artist_and_venue(client)
    old = client.get("/api/programme").json()[0]
    response = client.put(f"/api/performances/{old['id']}", json=_solo_body())
    assert response.status_code == 200, response.text
    new_id = response.json()["id"]
    assert new_id != old["id"]
    assert client.get(f"/api/performances/{old['id']}").status_code == 404
    assert client.get(f"/api/performances/{new_id}").status_code == 200
    assert len(client.get("/api/programme").json()) == 23


def test_delete_performance_returns_204(client):
    old = client.get("/api/programme").json()[0]
    response = client.delete(f"/api/performances/{old['id']}")
    assert response.status_code == 204
    assert not response.content
    assert client.get(f"/api/performances/{old['id']}").status_code == 404
    assert len(json_storage.load_festival().performances) == 22


def test_workshop_registration_and_persistence(client):
    programme = client.get("/api/programme").json()
    workshop = next(
        p for p in programme if p["kind"] == "workshop" and p["places_left"] > 0
    )
    response = client.post(
        f"/api/performances/{workshop['id']}/participants",
        json={"name": "Visiteur API Unique"},
    )
    assert response.status_code == 201, response.text
    assert "Visiteur API Unique" in response.json()["participants"]
    assert response.json()["places_left"] == workshop["places_left"] - 1


def test_non_workshop_registration_is_422(client):
    solo = next(p for p in client.get("/api/programme").json() if p["kind"] == "solo")
    response = client.post(
        f"/api/performances/{solo['id']}/participants", json={"name": "Camille"}
    )
    assert response.status_code == 422


def test_corrupted_json_returns_500(client):
    json_storage.FILE_PATH.write_text("{ fichier corrompu", encoding="utf-8")
    response = client.get("/api/festival")
    assert response.status_code == 500
    assert isinstance(response.json()["detail"], str)


def test_public_and_admin_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/admin/").status_code == 200
