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
