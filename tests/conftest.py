import pytest

from app.constants.sectors import SECTORS


@pytest.fixture
def load_sectors():
    return SECTORS
