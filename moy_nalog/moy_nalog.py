from typing import TypeVar, Optional, Union
from datetime import datetime
import random
import string
import time

from moy_nalog.methods import BaseMethod, AuthMethod, AddIncomeMethod, UserInfoMethod
from moy_nalog.http import HttpConnection
from moy_nalog.types import Token

T = TypeVar("T")


class MoyNalog:
    def __init__(self, login: str, password: str) -> None:
        self._login: str = login
        self.__password: str = password

        self._device_id: str = self._create_device_id()

        self._connection: HttpConnection = self._init_http()

        self._auth: AuthMethod = self._init_auth_method()
        self._income: AddIncomeMethod = self._init_income_method()
        self._user_info: UserInfoMethod = self._init_user_info_method()
        self._authorized: bool = False

        self.__token: Optional[Token] = None
        self.__inn: Optional[str] = None

    def _init_http(self) -> HttpConnection:
        return HttpConnection()

    def _init_auth_method(self) -> AuthMethod:
        return AuthMethod(
            self._connection, self._login, self.__password, self._device_id
        )

    def _init_income_method(self) -> AddIncomeMethod:
        return AddIncomeMethod(self._connection)
    
    def _init_user_info_method(self) -> UserInfoMethod:
        return UserInfoMethod(self._connection)

    def _create_device_id(self) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=22))

    async def _make_auth(self) -> dict:
        inn, token = await self._auth.execute()
        self.__inn = inn
        self.__token = token

        self._authorized = True

    async def _get_token(self) -> str:
        if (
            self.__token
            and self.__token
            and int(time.time() * 1000) + 60 * 1000
            < int(
                datetime.fromisoformat(
                    self.__token.expire_in.replace("Z", "+00:00")
                ).timestamp()
                * 1000
            )
        ):
            return self.__token.value

        if not self._authorized:
            await self._make_auth()

        self.__token = await self._auth.get_token_by_refresh_token(
            connection=self._connection, refresh_token=self.__token.refresh_value
        )

        return self.__token.value

    async def _call(self) -> dict:
        pass

    async def add_income(
        self,
        name: str,
        amount: Union[int, float],
        quantity: int = 1,
        date: str | datetime = datetime.now(),
    ):
        await self._execute_method(
            self._income,
            inn=self.__inn,
            name=name,
            amount=amount,
            quantity=quantity,
            date=date,
        )

    async def get_user_info(self):
        return await self._execute_method(self._user_info)

    async def _execute(self, method: T, **kwargs) -> T:
        return await method.execute(**kwargs)

    async def _execute_method(self, method: BaseMethod, **kwargs) -> BaseMethod:
        token = await self._get_token()
        return await self._execute(method, token=token, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def __repr__(self) -> str:
        return "MoyNalog()"
