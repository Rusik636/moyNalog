import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple, Optional, Union
from dataclasses import dataclass

from httpx import HTTPStatusError

from moy_nalog.http import HttpConnection, HEADERS, BASE_URL
from moy_nalog.exceptions import (
    RefreshTokenNotFoundError,
    RejectedIncomeError,
    NalogMethodError,
)
from moy_nalog.types import Token, Income
from moy_nalog.loggers import methods


@dataclass
class BaseMethod:
    async def _make_request(
        self, connection: HttpConnection, url: str, type_: str = "post", **kwargs
    ) -> dict:
        async with connection as conn:
            response = (
                await conn.post(url, **kwargs)
                if type_ == "post"
                else await conn.get(url, **kwargs)
            )
            try:
                response.raise_for_status()
            except HTTPStatusError:
                methods.exception("Unexpected status code")
                raise NalogMethodError(
                    f"{response.json().get("message") or f"Unexpected {response.status_code} code"}"
                )
            return response.json()

    async def execute(self, connection: HttpConnection):
        pass


@dataclass
class AuthMethod(BaseMethod):
    connection: HttpConnection

    login: str
    password: str
    device_id: str

    _common_body: Optional[dict] = None

    def __post_init__(self):
        self._common_body = {
            "deviceInfo": {
                "sourceDeviceId": self.device_id,
                "sourceType": "WEB",
                "appVersion": "1.0.0",
                "metaDetails": {
                    "userAgent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2)"
                        " AppleWebKit/537.36 (KHTML, like Gecko)"
                        " Chrome/88.0.4324.192 Safari/537.36"
                    )
                },
            }
        }

    async def get_token_by_refresh_token(
        self, connection: HttpConnection, refresh_token
    ):
        body = {**self._common_body, "refreshToken": refresh_token}
        response = await self._make_request(connection, url="/auth/token", json=body)
        return Token(
            value=response.get("token"),
            expire_in=response.get("tokenExpireIn"),
            refresh_value=response.get("refreshToken")
            if response.get("refreshToken")
            else None,
        )

    async def execute(
        self,
    ) -> Tuple[str, Token]:
        body = {"username": self.login, "password": self.password, **self._common_body}
        response = await self._make_request(
            self.connection, url="/auth/lkfl", json=body
        )
        if response.get("refreshToken") is None:
            raise RefreshTokenNotFoundError(
                f"{response.get("message") or "Cannot get refreshToken"}"
            )
        return response.get("profile").get("inn"), Token(
            value=response.get("token"),
            expire_in=response.get("tokenExpireIn"),
            refresh_value=response.get("refreshToken"),
        )


@dataclass
class AddIncomeMethod(BaseMethod):
    connection: HttpConnection

    def _date_to_local_iso(
        self,
        date: datetime.datetime | None = None,
    ) -> str:
        if date is None:
            date = (
                datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
            )
        if isinstance(date, datetime.datetime):
            date = date.replace(hour=23, minute=59, second=59).astimezone().isoformat()
        return date
        # deprecated
        """
        offset = date.utcoffset().total_seconds() / 60 if date.utcoffset() else 0
        absoff = abs(offset)

        local_time = date - datetime.timedelta(minutes=offset)

        iso_string = local_time.isoformat(timespec="seconds")

        sign = "-" if offset > 0 else "+"
        hours = int(absoff // 60)
        minutes = int(absoff % 60)

        offset_string = f"{sign}{str(hours).zfill(2)}:{str(minutes).zfill(2)}"

        return iso_string + offset_string
        """

    async def send_income(
        self,
        token: str,
        name: str,
        amount: Union[int, float],
        quantity: int = 1,
        date: datetime.datetime | str = datetime.datetime.now(),
    ):
        amount = Decimal(f"{amount}")
        quantity = Decimal(f"{quantity}")

        headers = {"authorization": f"Bearer {token}", **HEADERS}
        body = {
            "paymentType": "CASH",
            "ignoreMaxTotalIncomeRestriction": False,
            "client": {
                "contactPhone": None,
                "displayName": None,
                "incomeType": "FROM_INDIVIDUAL",
                "inn": None,
            },
            "requestTime": self._date_to_local_iso(),
            "operationTime": self._date_to_local_iso(date),
            "services": [
                {
                    "name": name,
                    "amount": float(
                        amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    ),
                    "quantity": int(quantity),
                }
            ],
            "totalAmount": float(
                (amount * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
        }
        methods.debug(f"{body}")
        response = await self._make_request(
            connection=self.connection, url="income", headers=headers, json=body
        )
        return response

    async def get_information_about_income(self, url: str) -> dict:
        return await self._make_request(self.connection, url=url, type_="get")

    async def execute(
        self,
        inn: str,
        token: str,
        name: str,
        amount: Union[int, float],
        quantity: int = 1,
        date: datetime.datetime | str = datetime.datetime.now(),
    ) -> dict:
        response = await self.send_income(
            token=token, name=name, amount=amount, quantity=quantity, date=date
        )
        if not response or not response.get("approvedReceiptUuid"):
            raise RejectedIncomeError("Check your params.")

        url = f"{BASE_URL}/receipt/{inn}/{response.get("approvedReceiptUuid")}"

        income = Income(
            id=response.get("approvedReceiptUuid"),
            approved_receipt_uuid=response.get("approvedReceiptUuid"),
            json_url=f"{url}/json",
            print_url=f"{url}/print",
        )
        # TODO: Make check information
        # return await self.get_information_about_income(income.json_url)
        return income
