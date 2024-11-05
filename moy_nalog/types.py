from dataclasses import dataclass
from datetime import datetime


@dataclass
class Token:
    value: str
    expire_in: datetime
    refresh_value: str | None = None


@dataclass
class Income:
    id: str
    approved_receipt_uuid: str
    json_url: str
    print_url: str

    data: dict | None = None


@dataclass
class User:
    last_name: str | None
    id: int | None
    display_name: str | None
    middle_name: str | None
    email: str | None
    phone: str | None
    inn: str | None
    snils: str | None
    avatar_exists: bool | None
    initial_registration_date: datetime | None
    registration_date: datetime | None
    first_receipt_register_time: datetime | None
    first_receipt_cancel_time: datetime | None
    hide_cancelled_receipt: bool | None
    register_available: str | None
    status: str | None
    restricted_mode: bool | None
    pfr_url: str | None
    login: str | None
