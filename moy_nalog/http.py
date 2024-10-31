from httpx import AsyncClient

BASE_URL = "https://lknpd.nalog.ru/api/v1"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
}


class HttpConnection:
    def __init__(self) -> None:
        self._async_client: AsyncClient | None = None

    async def __aenter__(self) -> AsyncClient:
        if not self._async_client:
            self._async_client = AsyncClient(base_url=BASE_URL, headers=HEADERS)
        return self._async_client

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._async_client.aclose()
        self._async_client = None
