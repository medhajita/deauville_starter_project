import json
from pathlib import Path
from festival.artists import Artist
from festival.venues import Venue
from festival.performances import (
    SoloPerformance,
    LineupPerformance,
    WorkshopPerformance,
)
from festival.festival import Festival
from festival.errors import StorageError

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR.parent / "data" / "festival.json"

def load_festival():

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            load_data = json.load(file)

    except OSError as e:
        raise StorageError(
            f"Impossible de lire le fichier JSON : {e}"
        ) from e

    except (json.JSONDecodeError, UnicodeError) as e:
        raise StorageError(
            f"Fichier JSON invalide : {e}"
        ) from e

    festival = Festival(
        load_data["name"],
        load_data["first_day"],
        load_data["last_day"],
        [],
        [],
        []
    )

    for x in load_data["artists"] :
        art = Artist(
            x["name"],
            x["bio"],
            x["photo_url"]
        )
        festival.add_artist(art)

    for x in load_data["venues"] :
        ven = Venue(
            x["name"],
            x["capacity"],
            x["address"]
        )
        festival.add_venue(ven)

    for x in load_data["performances"] :
        if x["kind"] == "solo":
            per = SoloPerformance(
                x["kind"],
                x["title"],
                x["venue"],
                x["start"],
                x["duration_minutes"],
                x["description"],
                x["artist"],
                x["min_age"]
            )
        elif x["kind"] == "lineup" :
            per = LineupPerformance(
                x["kind"],
                x["title"],
                x["venue"],
                x["start"],
                x["duration_minutes"],
                x["description"],
                x["host"],
                x["acts"]
            )
        elif x["kind"] == "workshop" :
            per = WorkshopPerformance(
                x["kind"],
                x["title"],
                x["venue"],
                x["start"],
                x["duration_minutes"],
                x["description"],
                x["teacher"],
                x["max_participants"],
                x["participants"]
            )
        else :
            raise ValueError(
                f"Unknown performance kind: {x['kind']}"
        )
        festival.add_performance(per)

    return festival

def save_festival(festival) :

    dict_fest = {
        "name" : festival.name,
        "first_day" : festival.first_day,
        "last_day" : festival.last_day,
        "venues" : [],
        "artists" : [],
        "performances" : []
        }

    for artist in festival.artists :
        dict_artist = {
            "name": artist.name,
            "bio": artist.bio,
            "photo_url": artist.photo_url
        }

        dict_fest["artists"].append(dict_artist)

    for venue in festival.venues :
        dict_venue = {
            "name": venue.name,
            "capacity": venue.capacity,
            "address": venue.address
        }

        dict_fest["venues"].append(dict_venue)

    for performance in festival.performances :
        if performance.kind == "solo" :
            dict_performance = {
                "kind" : performance.kind,
                "title" : performance.title,
                "venue" : performance.venue,
                "start" : performance.start.isoformat(timespec="minutes"),
                "duration_minutes" : performance.duration_minutes,
                "description" : performance.description,
                "artist" : performance.artist,
                "min_age" : performance.min_age
            }
        elif performance.kind == "lineup" :
            dict_performance = {
                "kind" : performance.kind,
                "title" : performance.title,
                "venue" : performance.venue,
                "start" : performance.start.isoformat(timespec="minutes"),
                "duration_minutes" : performance.duration_minutes,
                "description" : performance.description,
                "host" : performance.host,
                "acts" : performance.acts
            }
        elif performance.kind == "workshop":
            dict_performance = {
                "kind": performance.kind,
                "title": performance.title,
                "venue": performance.venue,
                "start": performance.start.isoformat(timespec="minutes"),
                "duration_minutes": performance.duration_minutes,
                "description": performance.description,
                "teacher": performance.teacher,
                "max_participants": performance.max_participants,
                "participants": performance.participants

            }
        else:
            raise ValueError(
                f"Unknown performance kind: {performance.kind}"
            )
        dict_fest["performances"].append(dict_performance)

    temp_path = FILE_PATH.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(
                dict_fest,
                file,
                ensure_ascii=False,
                indent=2
            )

        temp_path.replace(FILE_PATH)

    except OSError as e:
        raise StorageError(
            f"Impossible de sauvegarder le festival : {e}"
        ) from e
