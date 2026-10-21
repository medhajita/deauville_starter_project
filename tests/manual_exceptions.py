
from storage.json_storage import load_festival
from festival.errors import NotFoundError , ValidationError, ConflictError ,StorageError
from festival.festival import Festival, WorkshopPerformance
from festival.performances import LineupPerformance
import json

festival = load_festival()

try :
    festival.get_artist_by_slug("artiste_inconnu_test")
except NotFoundError:
    print("TEST A1 : OK")
else :
    raise AssertionError

try :
    festival.get_venue_by_slug("salle-inconnue-tes")
except NotFoundError:
    print("TEST A2 : OK")
else :
    raise AssertionError

try :
    festival.get_performance_by_id("performance-inconnue-tes")
except NotFoundError:
    print("TEST A3 : OK")
else :
    raise AssertionError

#Verification de ValidationError

try :
    fest = Festival("","2027-06-10","2027-06-13",[],[],[])
except ValidationError:
    print("TEST B1 : OK")
else :
    raise AssertionError

try :
    festival.add_participant("la-cabane-2027-06-11-1030","   ")
except ValidationError:
    print("TEST B2 : OK")
else :
    raise AssertionError

non_workshop = next(
    p for p in festival.performances
    if not isinstance(p, WorkshopPerformance)
)

try:
    festival.add_participant(non_workshop.id, "Alex")

except ValidationError:
    print("TEST B3 : OK")

else:
    raise AssertionError

artist = festival.artists[0]

try :
    festival.add_artist(artist)
except ConflictError as e:
    print("TEST C1 : OK")
    print("Cause du conflit :", e)
else :
    raise AssertionError

assert len(festival.artists) == 12, "TEST C1 : ÉCHEC, le nombre d'artistes a changé"

performance = festival.performances[0]

try :
    festival.add_performance(performance)
except ConflictError as e:
    print("TEST C2 : OK")
    print("Cause du conflit :", e)
else :
    raise AssertionError

assert len(festival.performances) == 23, "TEST C2 : ÉCHEC, le nombre de performances a changé"


performance1 = festival.performances[0]

artistes_utilises = {performance1.host, *performance1.acts}

autres_artistes = [
    artist.slug
    for artist in festival.artists
    if artist.slug not in artistes_utilises
]

performance2 = LineupPerformance(
    kind="lineup",
    title="Test conflit horaire",
    venue="grand-casino",
    start="2027-06-10T21:00:00",
    duration_minutes=60,
    description="Test de conflit horaire",
    host=autres_artistes[0],
    acts=autres_artistes[1:5]
)

try :
    festival.add_performance(performance2)
except ConflictError as e:
    print("TEST C3 : OK")
    print("Cause du conflit :", e)
else :
    raise AssertionError

assert len(festival.performances) == 23, "TEST C3 : ÉCHEC, le nombre de performances a changé"



workshop_id = "la-cabane-2027-06-11-1030"
participant = "Participant Test C4"

festival.add_participant(workshop_id, participant)

try:
    festival.add_participant(workshop_id, participant)

except ConflictError as e:
    print("TEST C4 : OK")
    print("Cause du conflit :", e)

else:
    raise AssertionError("TEST C4 : ÉCHEC, doublon accepté")

old_performance = festival.performances[0]

old_id = old_performance.id
old_title = old_performance.title
old_venue = old_performance.venue

new_performance = LineupPerformance(
    kind="lineup",
    title="Opening Gala modifié",
    venue="salle-inconnue",
    start="2027-06-10T20:30:00",
    duration_minutes=120,
    description="Test du rollback",
    host=old_performance.host,
    acts=list(old_performance.acts)
)

try:
    festival.update_performance(old_id, new_performance)

except NotFoundError as e:
    print("TEST D1 : OK")
    print("Erreur détectée :", e)

else:
    raise AssertionError("TEST D1 : ÉCHEC, modification acceptée")

restored = festival.get_performance_by_id(old_id)

assert restored.title == old_title
assert restored.venue == old_venue
assert restored is old_performance

print("TEST D2 : OK - Ancienne performance restaurée")

assert len(festival.performances) == 23

print("TEST D3 : OK - Toujours 23 performances")


from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from festival.errors import StorageError
import storage.json_storage as json_storage


with TemporaryDirectory() as temp_dir:

    fake_path = Path(temp_dir) / "festival_inexistant.json"

    with patch.object(json_storage, "FILE_PATH", fake_path):

        try:
            json_storage.load_festival()

        except StorageError as e:
            print("TEST S1 : OK")
            print("Erreur détectée :", e)

            assert isinstance(e.__cause__, FileNotFoundError)

        else:
            raise AssertionError(
                "TEST S1 : ÉCHEC, StorageError non déclenchée"
            )


with TemporaryDirectory() as temp_dir:

    invalid_path = Path(temp_dir) / "festival_invalide.json"

    invalid_path.write_text(
        '{"name": "Festival", "artists": [',
        encoding="utf-8"
    )

    with patch.object(json_storage, "FILE_PATH", invalid_path):

        try:
            json_storage.load_festival()

        except StorageError as e:
            print("TEST S2 : OK")
            print("Erreur détectée :", e)

            assert isinstance(e.__cause__, json.JSONDecodeError)

        else:
            raise AssertionError(
                "TEST S2 : ÉCHEC, StorageError non déclenchée"
            )


test_festival = json_storage.load_festival()

with TemporaryDirectory() as temp_dir:

    invalid_path = (
        Path(temp_dir)
        / "dossier_inexistant"
        / "festival.json"
    )

    with patch.object(json_storage, "FILE_PATH", invalid_path):

        try:
            json_storage.save_festival(test_festival)

        except StorageError as e:
            print("TEST S3 : OK")
            print("Erreur détectée :", e)

            assert isinstance(e.__cause__, OSError)

        else:
            raise AssertionError(
                "TEST S3 : ÉCHEC, StorageError non déclenchée"
            )

