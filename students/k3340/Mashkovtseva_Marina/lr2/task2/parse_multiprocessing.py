import multiprocessing
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

URLS = [
    "https://stackoverflow.com",
    "https://github.com",
    "https://vk.com",
]

def parse_and_save(url):
    try:
        html = requests.get(url, timeout=10).text
        title = BeautifulSoup(html, "html.parser").title.string.strip()

        conn = sqlite3.connect("parsed_pages.db")
        conn.execute("INSERT INTO pages VALUES (NULL, ?, ?, ?)", (url, title, "multiprocessing"))
        conn.commit()
        conn.close()

        print(f"{url} -> {title}")
    except Exception as e:
        print(f"ошибка {url}: {e}")

if __name__ == "__main__":
    start_time = time.time()
    with multiprocessing.Pool(4) as pool:
        pool.map(parse_and_save, URLS)
    print(f"Время: {time.time() - start_time:.2f} сек")
