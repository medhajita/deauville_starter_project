import pytest
from storage.json_storage import load_festival
from festival.errors import NotFoundError

@pytest.fixture
def festival():
    return  load_festival()

def test_festival_has_12_artists(festival):
    assert len(festival.artists) == 12

def test_artist_not_found(festival):
    with pytest.raises(NotFoundError):
        festival.get_artist_by_slug("artiste-inconnu")

@pytest.mark.parametrize(
    "attribute , expected",
    [
      ("artists", 12),
      ("venues", 4),
      ("performances", 23)
      ]
)

def test_festival_counts(festival,attribute,expected):
    result = len(getattr(festival, attribute))
    assert result == expected


