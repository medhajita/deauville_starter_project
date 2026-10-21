import json

import pytest

import storage.json_storage as json_storage
from festival.errors import StorageError


def test_load_valid_json(festival):
    assert len(festival.artists) == 12
    assert len(festival.venues) == 4
    assert len(festival.performances) == 23


def test_invalid_json(tmp_path, monkeypatch):
    fake_file = tmp_path / "festival_invalide.json"
    fake_file.write_text('{"name": "Festival",', encoding="utf-8")
    monkeypatch.setattr(json_storage, "FILE_PATH", fake_file)

    with pytest.raises(StorageError) as error:
        json_storage.load_festival()

    assert isinstance(error.value.__cause__, json.JSONDecodeError)


def test_missing_json(tmp_path, monkeypatch):
    fake_file = tmp_path / "festival_inexistant.json"
    monkeypatch.setattr(json_storage, "FILE_PATH", fake_file)

    with pytest.raises(StorageError) as error:
        json_storage.load_festival()

    assert isinstance(error.value.__cause__, FileNotFoundError)


def test_save_and_reload(festival, tmp_path, monkeypatch):
    fake_file = tmp_path / "festival.json"
    monkeypatch.setattr(json_storage, "FILE_PATH", fake_file)

    json_storage.save_festival(festival)
    restored = json_storage.load_festival()

    assert fake_file.is_file()
    assert restored.name == festival.name
    assert len(restored.artists) == len(festival.artists)
    assert len(restored.venues) == len(festival.venues)
    assert len(restored.performances) == len(festival.performances)


def test_save_error(festival, tmp_path, monkeypatch):
    fake_file = tmp_path / "dossier_inexistant" / "festival.json"
    monkeypatch.setattr(json_storage, "FILE_PATH", fake_file)

    with pytest.raises(StorageError) as error:
        json_storage.save_festival(festival)

    assert isinstance(error.value.__cause__, OSError)
