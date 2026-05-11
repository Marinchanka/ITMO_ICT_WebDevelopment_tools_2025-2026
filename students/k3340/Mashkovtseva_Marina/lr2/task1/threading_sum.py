import threading
import time

N = 10_000_000
THREADS = 4
results = []
lock = threading.Lock()

def calculate_sum(start, end):
    total = sum(range(start, end + 1))
    with lock:
        results.append(total)

start_time = time.time()

chunk = N // THREADS
threads = []

for i in range(THREADS):
    s = i * chunk + 1
    e = (i + 1) * chunk if i < THREADS - 1 else N
    t = threading.Thread(target=calculate_sum, args=(s, e))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Сумма: {sum(results)}")
print(f"Время: {time.time() - start_time:.4f} сек")
