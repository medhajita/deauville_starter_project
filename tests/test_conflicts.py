import pytest

from festival.festival import Festival
from festival.artists import Artist
from festival.venues import Venue
from festival.performances import SoloPerformance
from festival.errors import ConflictError


@pytest.fixture
def schedule():
    f = Festival("Festival test", "2027-06-10", "2027-06-13", [], [], [])
    venue = Venue("Salle Alpha", 100, "Rue Alpha")
    a1 = Artist("Artiste Alpha", "Bio", "https://example.com/a.jpg")
    a2 = Artist("Artiste Beta", "Bio", "https://example.com/b.jpg")
    f.add_venue(venue)
    f.add_artist(a1)
    f.add_artist(a2)
    return f, venue, a1, a2


def solo(title, venue_slug, artist_slug, start):
    return SoloPerformance(
        "solo", title, venue_slug, start, 60,
        "Spectacle de test", artist_slug, 0
    )


def test_same_venue_overlapping(schedule):
    f, venue, a1, a2 = schedule
    f.add_performance(solo("Premier", venue.slug, a1.slug, "2027-06-10T18:00:00"))

    with pytest.raises(ConflictError, match="busy"):
        f.add_performance(solo("Deuxième", venue.slug, a2.slug, "2027-06-10T18:20:00"))

    assert len(f.performances) == 1


def test_same_artist_overlapping(schedule):
    f, venue, a1, a2 = schedule
    other_venue = Venue("Salle Beta", 80, "Rue Beta")
    f.add_venue(other_venue)
    f.add_performance(solo("Premier", venue.slug, a1.slug, "2027-06-10T18:00:00"))

    with pytest.raises(ConflictError, match="artist"):
        f.add_performance(solo("Deuxième", other_venue.slug, a1.slug, "2027-06-10T18:20:00"))

    assert len(f.performances) == 1


def test_29_minutes_gap_rejected(schedule):
    f, venue, a1, a2 = schedule
    f.add_performance(solo("Premier", venue.slug, a1.slug, "2027-06-10T18:00:00"))
    with pytest.raises(ConflictError):
        f.add_performance(solo("Deuxième", venue.slug, a2.slug, "2027-06-10T19:29:00"))

    assert len(f.performances) == 1


def test_exactly_30_minutes_gap_accepted(schedule):
    f, venue, a1, a2 = schedule
    f.add_performance(solo("Premier", venue.slug, a1.slug, "2027-06-10T18:00:00"))
    second = solo("Deuxième", venue.slug, a2.slug, "2027-06-10T19:30:00")
    f.add_performance(second)

    assert len(f.performances) == 2
    assert f.get_performance_by_id(second.id) is second
