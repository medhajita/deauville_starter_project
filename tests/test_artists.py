import pytest
from festival.artists import Artist
from festival.errors import ConflictError, NotFoundError
from storage.json_storage import load_festival

@pytest.fixture
def festival():
    return load_festival()

def test_add_artist(festival):
    assert len(festival.artists) == 12, "Test Failed , artists is not equal to 12"
    festival.add_artist(Artist("Test Comedian","Artiste pour les tests", "https://example.com/photo.jpg"))
    assert len(festival.artists) == 13, "Test Failed , artists is not equal to 13"
    found_artist = festival.get_artist_by_slug("test-comedian")
    assert found_artist.name == "Test Comedian", "Test Failed, no artist with Test Comedian name"

def test_add_duplicate_artist(festival):
    art1 = festival.artists[0]
    with pytest.raises(ConflictError):
        festival.add_artist(art1)
    assert len(festival.artists) == 12, "Test Failed , artists is not equal to 12"

def test_artist_not_found(festival):
    with pytest.raises(NotFoundError):
        festival.get_artist_by_slug("artiste-inconnu")

