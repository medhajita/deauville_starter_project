from copy import copy

import pytest

from festival.errors import NotFoundError


def test_update_performance_valid(festival):
    old = festival.performances[0]
    new = copy(old)
    new.title = old.title + " - nouvelle version"

    updated = festival.update_performance(old.id, new)

    assert updated is new
    assert festival.get_performance_by_id(old.id) is new
    assert updated.title.endswith("nouvelle version")
    assert len(festival.performances) == 23


def test_update_rollback_unknown_venue(festival):
    old = festival.performances[0]
    old_id = old.id
    old_title = old.title
    old_venue = old.venue
    old_position = festival.performances.index(old)

    invalid = copy(old)
    invalid.venue = "salle-inconnue"

    with pytest.raises(NotFoundError):
        festival.update_performance(old_id, invalid)

    restored = festival.get_performance_by_id(old_id)
    assert restored is old
    assert restored.title == old_title
    assert restored.venue == old_venue
    assert festival.performances[old_position] is old
    assert len(festival.performances) == 23


def test_delete_performance(festival):
    old = festival.performances[0]
    festival.delete_performance(old.id)
    assert len(festival.performances) == 22
    with pytest.raises(NotFoundError):
        festival.get_performance_by_id(old.id)
