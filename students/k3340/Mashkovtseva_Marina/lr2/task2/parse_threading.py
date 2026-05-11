import threading
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

URLS = [
    "https://stackoverflow.com",
    "https://github.com",
    "https://vk.com",
]

lock = threading.Lock()

def parse_and_save(url):
    try:
        html = requests.get(url, timeout=10).text
        title = BeautifulSoup(html, "html.parser").title.string.strip()

        with lock:
            conn = sqlite3.connect("parsed_pages.db")
            conn.execute("INSERT INTO pages VALUES (NULL, ?, ?, ?)", (url, title, "threading"))
            conn.commit()
            conn.close()

        print(f"{url} -> {title}")
    except Exception as e:
        print(f"ошибка {url}: {e}")

start_time = time.time()

threads = [threading.Thread(target=parse_and_save, args=(url,)) for url in URLS]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Время: {time.time() - start_time:.2f} сек")
