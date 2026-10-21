from datetime import timedelta


def test_programme_sorted(festival):
    programme = festival.get_programme()
    starts = [performance.start for performance in programme]
    assert starts == sorted(starts)
    assert len(programme) == 23


def test_programme_by_day(festival):
    programme = festival.get_programme_by_day("2027-06-11")
    assert len(programme) > 0
    assert all(p.festival_day == "2027-06-11" for p in programme)


def test_programme_by_venue(festival):
    venue_slug = festival.venues[0].slug
    programme = festival.get_programme_by_venue(venue_slug)
    assert len(programme) > 0
    assert all(p.venue == venue_slug for p in programme)


def test_artist_show_count(festival):
    artist_slug = festival.artists[0].slug
    shows = festival.get_artist_performances(artist_slug)
    assert festival.get_artist_show_count(artist_slug) == len(shows)
    assert all(artist_slug in festival.get_performance_artists(p) for p in shows)


def test_now_playing(festival):
    first = festival.get_programme()[0]
    moment = first.start + timedelta(minutes=1)
    assert first in festival.get_now_playing(moment)


def test_up_next(festival):
    earliest = festival.get_programme()[0]
    next_shows = festival.get_up_next(earliest.start - timedelta(minutes=1))
    assert len(next_shows) == 3
    assert [p.start for p in next_shows] == sorted(p.start for p in next_shows)


def test_performance_details(festival):
    performance = festival.get_programme()[0]
    details = festival.get_performance_details(performance)
    assert details["id"] == performance.id
    assert details["title"] == performance.title
    assert details["venue"] == performance.venue
    assert "artists" in details
    assert details["capacity"] > 0
