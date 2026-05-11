import multiprocessing
import time

N = 10_000_000
PROCESSES = 4

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end + 1)))

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    chunk = N // PROCESSES
    processes = []

    start_time = time.time()

    for i in range(PROCESSES):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < PROCESSES - 1 else N
        p = multiprocessing.Process(target=calculate_sum, args=(s, e, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in range(PROCESSES))
    print(f"Сумма: {total}")
    print(f"Время: {time.time() - start_time:.4f} сек")
