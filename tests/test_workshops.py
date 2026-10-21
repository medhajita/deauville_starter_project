import pytest

from festival.performances import WorkshopPerformance
from festival.errors import ConflictError, ValidationError


def get_workshop_with_places(festival):
    return next(
        p for p in festival.performances
        if isinstance(p, WorkshopPerformance) and festival.get_places_left(p) > 0
    )


def get_any_workshop(festival):
    return next(p for p in festival.performances if isinstance(p, WorkshopPerformance))


def test_register_participant(festival):
    workshop = get_workshop_with_places(festival)
    initial = len(workshop.participants)

    festival.add_participant(workshop.id, "Participant Pytest")

    assert len(workshop.participants) == initial + 1
    assert "Participant Pytest" in workshop.participants


def test_duplicate_participant(festival):
    workshop = get_workshop_with_places(festival)
    festival.add_participant(workshop.id, "Participant Pytest")

    with pytest.raises(ConflictError):
        festival.add_participant(workshop.id, "participant pytest")


def test_empty_participant_name(festival):
    workshop = get_any_workshop(festival)
    with pytest.raises(ValidationError):
        festival.add_participant(workshop.id, "   ")


def test_workshop_full(festival):
    workshop = get_any_workshop(festival)
    places_left = festival.get_places_left(workshop)
    for i in range(places_left):
        festival.add_participant(workshop.id, f"Participant remplissage pytest {i}")

    assert festival.get_places_left(workshop) == 0
    with pytest.raises(ConflictError):
        festival.add_participant(workshop.id, "Participant en trop")


def test_places_left_decreases(festival):
    workshop = get_workshop_with_places(festival)
    before = festival.get_places_left(workshop)

    festival.add_participant(workshop.id, "Participant Pytest")

    assert festival.get_places_left(workshop) == before - 1


def test_register_on_non_workshop(festival):
    non_workshop = next(
        p for p in festival.performances
        if not isinstance(p, WorkshopPerformance)
    )
    with pytest.raises(ValidationError):
        festival.add_participant(non_workshop.id, "Participant Pytest")
