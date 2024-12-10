import pytest

from moy_nalog import MoyNalog
from moy_nalog.exceptions import AuthorizationError


@pytest.mark.asyncio
async def test_user_method() -> None:
    nalog = MoyNalog("12345678", "strong-password")
    try:
        await nalog.get_user_info()
    except Exception as ex:
        assert isinstance(ex, AuthorizationError)
