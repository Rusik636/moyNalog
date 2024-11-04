import datetime

import pytest

from moy_nalog.exceptions import RefreshTokenNotFoundError, NalogMethodError
from moy_nalog.moy_nalog import MoyNalog

pytest_plugins = ("pytest_asyncio",)


class TestClass:
    nalog = MoyNalog("hello", "world")
    
    @pytest.mark.asyncio
    async def test_auth_exception(self):
        try:
            await self.nalog.add_income("name", 123, datetime.datetime.now())
        except Exception as ex:
            # test exception
            assert isinstance(ex, NalogMethodError)
            # test message text from lknpd.nalog.ru API
            assert str(ex).lower() == "указанный вами инн некорректен"
