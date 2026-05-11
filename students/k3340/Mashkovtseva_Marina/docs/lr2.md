# Лабораторная работа 2. Потоки. Процессы. Асинхронность.

**Цели:** Понять отличия между потоками и процессами, разобраться с асинхронностью в Python.

**Студент:** Машковцева Марина

**GitHub репозиторий:** `https://github.com/Marinchanka/ITMO_ICT_WebDevelopment_tools_2025-2026`

---

## Задача 1. Подсчёт суммы чисел

Каждая программа считает сумму чисел от 1 до 10 000 000, разбивая задачу на 4 части.

### threading_sum.py

```python
import threading
import time

N = 10000000
NUM_THREADS = 4
results = []
lock = threading.Lock()

def calculate_sum(start, end):
    total = sum(range(start, end + 1))
    with lock:
        results.append(total)

start_time = time.time()

chunk = N // NUM_THREADS
threads = []

for i in range(NUM_THREADS):
    s = i * chunk + 1
    e = (i + 1) * chunk if i < NUM_THREADS - 1 else N
    t = threading.Thread(target=calculate_sum, args=(s, e))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Сумма: {sum(results)}")
print(f"Время: {time.time() - start_time:.4f} сек")
```

### multiprocessing_sum.py

```python
import multiprocessing
import time

N = 10_000_000
NUM_PROCESSES = 4

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end + 1)))

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    chunk = N // NUM_PROCESSES
    processes = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < NUM_PROCESSES - 1 else N
        p = multiprocessing.Process(target=calculate_sum, args=(s, e, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in range(NUM_PROCESSES))
    print(f"Сумма: {total}")
    print(f"Время: {time.time() - start_time:.4f} сек")
```

### async_sum.py

```python
import asyncio
import time

N = 10000000
NUM_TASKS = 4

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    chunk = N // NUM_TASKS
    tasks = []

    for i in range(NUM_TASKS):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < NUM_TASKS - 1 else N
        tasks.append(calculate_sum(s, e))

    results = await asyncio.gather(*tasks)
    print(f"Сумма: {sum(results)}")

start_time = time.time()
asyncio.run(main())
print(f"Время: {time.time() - start_time:.4f} сек")
```

### Результаты

| Подход | Сумма | Время |
|--------|-------|-------|
| threading | 50 000 005 000 000 | 0.0814 сек |
| multiprocessing | 50 000 005 000 000 | 0.3898 сек |
| async | 50 000 005 000 000 | 0.0823 сек |

### Вывод

Все три программы дали одинаковый результат. По времени threading и async оказались быстрее multiprocessing — это объясняется тем, что запуск отдельных процессов сам по себе требует времени (нужно создать процесс, выделить память, скопировать данные). При N = 10 000 000 задача недостаточно тяжёлая, чтобы эти накладные расходы окупились.

Threading не дал реального ускорения по сравнению с однопоточным выполнением из-за GIL — потоки всё равно работают по очереди на CPU-задачах. Async тоже не даёт параллелизма здесь: нет точек `await` внутри вычислений, поэтому задачи выполняются последовательно.

Multiprocessing выиграл бы при действительно большом N, где выгода от параллельного использования нескольких ядер перекрыла бы накладные расходы на запуск процессов.

---

## Задача 2. Параллельный парсинг веб-страниц

Каждая программа парсит заголовки страниц с нескольких сайтов и сохраняет их в базу данных из лабораторной работы №1 (PostgreSQL, таблица `pages`).

### Подготовка БД

```python
# db_setup.py
import sqlite3

conn = sqlite3.connect("parsed_pages.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        approach TEXT
    )
""")
conn.commit()
conn.close()
print("БД готова")
```

### parse_threading.py

```python
import threading
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

URLS = [
    "https://vk.com",
    "https://wikipedia.org",
    "https://github.com",
]

lock = threading.Lock()

def parse_and_save(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, timeout=10, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

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
```

### parse_multiprocessing.py

```python
import multiprocessing
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

URLS = [
    "https://vk.com",
    "https://wikipedia.org",
    "https://github.com",
]

def parse_and_save(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, timeout=10, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

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
```

### parse_async.py

```python
import asyncio
import aiohttp
import aiosqlite
from bs4 import BeautifulSoup
import time

URLS = [
    "https://vk.com",
    "https://wikipedia.org",
    "https://github.com",
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
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with aiosqlite.connect("parsed_pages.db") as db:
            await asyncio.gather(*[parse_and_save(session, url, db) for url in URLS])

start_time = time.time()
asyncio.run(main())
print(f"Время: {time.time() - start_time:.2f} сек")
```

### Результаты

| Подход | Время |
|--------|-------|
| threading | 0.90 сек |
| multiprocessing | 1.71 сек |
| async | 5.35 сек |

### Вывод

Здесь картина другая. Threading оказался быстрее всего — потоки хорошо справляются с сетевыми запросами, потому что GIL отпускается во время ожидания ответа от сервера, и потоки реально работают параллельно.

Multiprocessing снова медленнее threading из-за накладных расходов на создание процессов — для трёх сайтов это явно избыточно.

Async показал худший результат в этом конкретном запуске — скорее всего из-за проблем с SSL на Mac и дополнительных задержек при переподключении. В теории async должен быть сравним с threading или быстрее при большом количестве запросов, но на небольшом числе URL разница несущественна и на результат влияет скорость ответа конкретных сайтов в момент запуска.

---

## Общий вывод

Выбор подхода зависит от типа задачи:

- **Threading** — хорош для небольшого количества сетевых запросов, прост в реализации
- **Multiprocessing** — стоит использовать только для по-настоящему тяжёлых вычислений, где параллельное использование ядер окупает накладные расходы
- **Async** — лучший выбор когда запросов много и важна масштабируемость, но требует асинхронных библиотек (aiohttp, aiosqlite и т.д.)
