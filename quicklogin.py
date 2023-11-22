import asyncio

from tiktokpy import TikTokPy  # type: ignore


async def main():
    async with TikTokPy() as bot:
        # Login to TikTok
        await bot.login_session()


asyncio.run(main())
