from datetime import timedelta

import pytest

from festival.artists import Artist
from festival.venues import Venue
from festival.performances import SoloPerformance
from festival.errors import ConflictError, NotFoundError


def make_solo(*, venue, artist, start="2027-06-13T12:00:00", duration=60):
    return SoloPerformance(
        "solo", "Spectacle pytest", venue, start, duration,
        "Spectacle créé pour les tests", artist, 0
    )


def test_add_valid_performance(festival):
    artist = Artist("Artiste Pytest", "Bio test", "https://example.com/a.jpg")
    venue = Venue("Salle Pytest", 100, "Rue des tests")
    festival.add_artist(artist)
    festival.add_venue(venue)

    performance = make_solo(venue=venue.slug, artist=artist.slug)
    festival.add_performance(performance)

    assert len(festival.performances) == 24
    assert festival.get_performance_by_id(performance.id) is performance


def test_add_duplicate_performance(festival):
    existing = festival.performances[0]

    with pytest.raises(ConflictError):
        festival.add_performance(existing)

    assert len(festival.performances) == 23


def test_performance_unknown_venue(festival):
    artist_slug = festival.artists[0].slug
    performance = make_solo(venue="salle-inconnue", artist=artist_slug)

    with pytest.raises(NotFoundError):
        festival.add_performance(performance)

    assert len(festival.performances) == 23


def test_performance_unknown_artist(festival):
    venue_slug = festival.venues[0].slug
    performance = make_solo(venue=venue_slug, artist="artiste-inconnu")

    with pytest.raises(NotFoundError):
        festival.add_performance(performance)

    assert len(festival.performances) == 23


def test_performance_end_time(festival):
    performance = make_solo(
        venue=festival.venues[0].slug,
        artist=festival.artists[0].slug,
        duration=60,
    )
    assert performance.end - performance.start == timedelta(minutes=60)


def test_performance_before_festival(festival):
    performance = make_solo(
        venue=festival.venues[0].slug,
        artist=festival.artists[0].slug,
        start="2027-06-09T12:00:00",
    )

    with pytest.raises(ConflictError):
        festival.add_performance(performance)

    assert len(festival.performances) == 23
