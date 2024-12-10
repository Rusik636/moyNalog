import pytest

from moy_nalog.methods.api import BaseAPI
from moy_nalog.http import HttpConnection
from moy_nalog.types import Credentials
from moy_nalog.exceptions import AuthorizationError

pytest_plugins = ("pytest_asyncio",)


class TestAPI:
    @pytest.mark.asyncio
    async def test_check_api(self):
        h = HttpConnection(Credentials("1234567890", "strong-password"))
        a = BaseAPI(h)
        try:
            await a.get("/user")
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)
            assert str(ex) == "Указанный Вами ИНН некорректен"
