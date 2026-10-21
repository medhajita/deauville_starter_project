import pytest

from festival.venues import Venue
from festival.errors import ConflictError, NotFoundError


def test_add_venue(festival):
    assert len(festival.venues) == 4

    festival.add_venue(Venue("Salle Test", 100, "10 rue Test, Deauville"))

    assert len(festival.venues) == 5
    found = festival.get_venue_by_slug("salle-test")
    assert found.name == "Salle Test"


def test_add_duplicate_venue(festival):
    venue = festival.venues[0]

    with pytest.raises(ConflictError):
        festival.add_venue(venue)

    assert len(festival.venues) == 4


def test_venue_not_found(festival):
    with pytest.raises(NotFoundError):
        festival.get_venue_by_slug("salle-inconnue")
