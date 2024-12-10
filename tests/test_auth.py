from httpx import AsyncClient, HTTPStatusError
import pytest

from moy_nalog.http import HttpAuth, BASE_URL
from moy_nalog.types import Credentials
from moy_nalog.exceptions import AuthorizationError

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def auth_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("hello", "world"),
    )


@pytest.fixture
def incorrect_inn_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("1234567890", "world"),
    )


@pytest.fixture
def incorrect_inn_or_password_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("3664069397", "super-strong-password"),
    )


class TestAuth:
    def test_bearer_auth(self, auth_instance: HttpAuth):
        auth = auth_instance
        assert auth._create_bearer_auth_header("123") == {"authorization": "Bearer 123"}

    @pytest.mark.asyncio
    async def test_request(self, auth_instance: HttpAuth):
        try:
            await auth_instance.make_request("/token", {"hello": "world"})
        except Exception as ex:
            assert isinstance(ex, HTTPStatusError)

    @pytest.mark.asyncio
    async def test_refresh_token(self, auth_instance: HttpAuth):
        try:
            await auth_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)

    def test_properties(self, auth_instance: HttpAuth):
        assert not auth_instance.access_token_is_active
        assert not auth_instance.is_authed

    def test_len_of_device_id(self, auth_instance: HttpAuth):
        assert len(auth_instance._create_device_id()) in (21, 22)
        # 10.12.24 on lknpd.nalog.ru length of device id is 21


class TestServerResponseMessages:
    @pytest.mark.asyncio
    async def test_incorrect_inn(self, incorrect_inn_instance: HttpAuth):
        try:
            await incorrect_inn_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)
            assert str(ex) == "Указанный Вами ИНН некорректен"

    @pytest.mark.asyncio
    async def test_incorrect_inn_or_password(
        self, incorrect_inn_or_password_instance: HttpAuth
    ) -> None:
        try:
            await incorrect_inn_or_password_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)
            print(ex)
            assert str(ex) == "Неверный логин или пароль"
