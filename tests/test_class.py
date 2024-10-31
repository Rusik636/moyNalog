import pytest

from moy_nalog.exceptions import RefreshTokenNotFoundError
from moy_nalog.moy_nalog import MoyNalog

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_auth():
    nalog = MoyNalog("hello", "world")
    try:
        await nalog._make_auth()
    except Exception as ex:
        assert(ex, RefreshTokenNotFoundError)
