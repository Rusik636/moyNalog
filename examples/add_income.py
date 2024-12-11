import asyncio

from moy_nalog import MoyNalog

nalog = MoyNalog("1234567890", "MyStrongPassword")


async def main():
    await nalog.add_income(
        "Предоставление информационных услуг #970/2495", amount=1000, quantity=1
    )


asyncio.run(main())
