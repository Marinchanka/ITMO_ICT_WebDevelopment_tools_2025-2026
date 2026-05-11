import asyncio
import aiohttp
import aiosqlite
from bs4 import BeautifulSoup
import time

URLS = [
    "https://stackoverflow.com",
    "https://github.com",
    "https://vk.com",
]

async def parse_and_save(session, url, db):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            html = await r.text()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

        await db.execute("INSERT INTO pages VALUES (NULL, ?, ?, ?)", (url, title, "async"))
        await db.commit()

        print(f"{url} -> {title}")
    except Exception as e:
        print(f"ошибка {url}: {e}")

async def main():
    connector = aiohttp.TCPConnector(ssl=False)  # отключаем проверку SSL
    async with aiohttp.ClientSession(connector=connector) as session:
        async with aiosqlite.connect("parsed_pages.db") as db:
            await asyncio.gather(*[parse_and_save(session, url, db) for url in URLS])

start_time = time.time()
asyncio.run(main())
print(f"Время: {time.time() - start_time:.2f} сек")
