"""Routes conformes au contrat API.md du dépôt de départ."""

from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from festival.artists import Artist
from festival.errors import (
    ConflictError,
    NotFoundError,
    StorageError,
    ValidationError,
)
from festival.performances import (
    LineupPerformance,
    SoloPerformance,
    WorkshopPerformance,
)
from storage import json_storage

from .schemas import (
    ArtistCreate,
    LineupCreate,
    ParticipantCreate,
    PerformanceCreate,
    SoloCreate,
    WorkshopCreate,
)

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Deauville Festival du Rire 2027", version="1.0.0")

write_lock = Lock()


@app.exception_handler(NotFoundError)
def not_found_handler(request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def conflict_handler(request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def validation_handler(request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(StorageError)
def storage_handler(request, exc: StorageError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def load_data():
    try:
        return json_storage.load_festival()
    except (KeyError, TypeError, ValueError, ValidationError, ConflictError, NotFoundError) as exc:
        raise StorageError(f"Le fichier du festival contient des données invalides : {exc}") from exc


def save_data(festival):
    try:
        json_storage.save_festival(festival)
    except (TypeError, ValueError) as exc:
        raise StorageError(f"Impossible de sauvegarder le festival : {exc}") from exc


def artist_json(artist) -> dict:
    return {
        "slug": artist.slug,
        "name": artist.name,
        "bio": artist.bio,
        "photo_url": artist.photo_url,
    }


def venue_json(venue) -> dict:
    return {
        "slug": venue.slug,
        "name": venue.name,
        "capacity": venue.capacity,
        "address": venue.address,
    }


def performance_json(festival, performance) -> dict:
    return festival.get_performance_details(performance)


def build_performance(body: PerformanceCreate):
    common = (
        body.kind,
        body.title,
        body.venue,
        body.start.isoformat(timespec="minutes"),
        body.duration_minutes,
        body.description,
    )
    try:
        if isinstance(body, SoloCreate):
            return SoloPerformance(*common, body.artist, body.min_age)
        if isinstance(body, LineupCreate):
            return LineupPerformance(*common, body.host, body.acts)
        if isinstance(body, WorkshopCreate):
            return WorkshopPerformance(
                *common,
                body.teacher,
                body.max_participants,
                body.participants,
            )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    raise ValidationError("Type de performance invalide.")


# ------------------------------- Lecture ----------------------------------

@app.get("/api/festival")
def get_festival():
    festival = load_data()
    first = date.fromisoformat(festival.first_day)
    last = date.fromisoformat(festival.last_day)
    days = []
    current = first
    while current <= last:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return {
        "name": festival.name,
        "first_day": festival.first_day,
        "last_day": festival.last_day,
        "days": days,
    }


@app.get("/api/venues")
def get_venues():
    festival = load_data()
    return [venue_json(venue) for venue in festival.get_venues()]


@app.get("/api/artists")
def get_artists():
    festival = load_data()
    return [artist_json(artist) for artist in festival.get_artists_sorted()]


@app.get("/api/artists/{slug}")
def get_artist(slug: str):
    festival = load_data()
    artist = festival.get_artist_by_slug(slug)
    data = artist_json(artist)
    data["performances"] = [
        performance_json(festival, perf)
        for perf in festival.get_artist_performances(slug)
    ]
    return data


@app.get("/api/programme")
def get_programme(day: date | None = None, venue: str | None = None):
    festival = load_data()
    if venue is not None:
        festival.get_venue_by_slug(venue)  # 404 même si aucun spectacle
    performances = festival.get_programme()
    if day is not None:
        performances = [p for p in performances if p.festival_day == day.isoformat()]
    if venue is not None:
        performances = [p for p in performances if p.venue == venue]
    return [performance_json(festival, p) for p in performances]


@app.get("/api/performances/{performance_id}")
def get_performance(performance_id: str):
    festival = load_data()
    performance = festival.get_performance_by_id(performance_id)
    return performance_json(festival, performance)


@app.get("/api/now")
def get_now(at: datetime | None = Query(default=None)):
    if at is not None and at.tzinfo is not None:
        raise HTTPException(status_code=422, detail="L'heure doit être locale, sans fuseau horaire.")
    festival = load_data()
    moment = at if at is not None else datetime.now()
    return {
        "at": moment.isoformat(timespec="minutes"),
        "now_playing": [
            performance_json(festival, p) for p in festival.get_now_playing(moment)
        ],
        "up_next": [
            performance_json(festival, p) for p in festival.get_up_next(moment)
        ],
    }


# ---------------------------- Administration -------------------------------

@app.post("/api/artists", status_code=201)
def create_artist(body: ArtistCreate):
    with write_lock:
        festival = load_data()
        try:
            artist = Artist(body.name, body.bio, body.photo_url)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        festival.add_artist(artist)
        save_data(festival)
        return artist_json(artist)


@app.post("/api/performances", status_code=201)
def create_performance(body: PerformanceCreate):
    with write_lock:
        festival = load_data()
        performance = build_performance(body)
        festival.add_performance(performance)
        save_data(festival)
        return performance_json(festival, performance)


@app.put("/api/performances/{performance_id}")
def update_performance(performance_id: str, body: PerformanceCreate):
    with write_lock:
        festival = load_data()
        new_performance = build_performance(body)
        festival.update_performance(performance_id, new_performance)
        save_data(festival)
        return performance_json(festival, new_performance)


@app.delete("/api/performances/{performance_id}", status_code=204)
def delete_performance(performance_id: str):
    with write_lock:
        festival = load_data()
        festival.delete_performance(performance_id)
        save_data(festival)
    return Response(status_code=204)


@app.post("/api/performances/{performance_id}/participants", status_code=201)
def add_participant(performance_id: str, body: ParticipantCreate):
    with write_lock:
        festival = load_data()
        performance = festival.get_performance_by_id(performance_id)
        if not isinstance(performance, WorkshopPerformance):
            raise ValidationError("This performance is not a workshop.")
        try:
            updated = festival.add_participant(performance_id, body.name)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        save_data(festival)
        return performance_json(festival, updated)



app.mount("/admin", StaticFiles(directory=ROOT / "web" / "admin", html=True), name="admin")
app.mount("/", StaticFiles(directory=ROOT / "web" / "public", html=True), name="public")
