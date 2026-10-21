import pytest
from storage.json_storage import load_festival


@pytest.fixture
def festival():
    return load_festival()
