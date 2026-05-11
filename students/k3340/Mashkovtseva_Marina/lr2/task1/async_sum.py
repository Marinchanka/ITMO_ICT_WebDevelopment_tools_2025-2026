import asyncio
import time

N = 10_000_000
TASKS = 4

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    chunk = N // TASKS
    tasks = []

    for i in range(TASKS):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < TASKS - 1 else N
        tasks.append(calculate_sum(s, e))

    results = await asyncio.gather(*tasks)
    print(f"Сумма: {sum(results)}")

start_time = time.time()
asyncio.run(main())
print(f"Время: {time.time() - start_time:.4f} сек")
