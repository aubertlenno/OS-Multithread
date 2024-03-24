import threading
import random
import os
import time

# constants
LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

number_buffer = []
stack_access_lock = threading.Lock()
items_available = threading.Event()
producer_done = threading.Event()

script_dir = os.path.dirname(os.path.realpath(__file__))
all_numbers_file_path = os.path.join(script_dir, "all.txt")
even_numbers_file_path = os.path.join(script_dir, "even.txt")
odd_numbers_file_path = os.path.join(script_dir, "odd.txt")

def produce_numbers():
    for _ in range(MAX_COUNT):
        num = random.randint(LOWER_NUM, UPPER_NUM)
        with stack_access_lock:
            if len(number_buffer) < BUFFER_SIZE:
                number_buffer.append(num)
                items_available.set()
            else:
                while len(number_buffer) >= BUFFER_SIZE:
                    stack_access_lock.release()
                    time.sleep(0.01)
                    stack_access_lock.acquire()
                number_buffer.append(num)
                items_available.set()
        with open(all_numbers_file_path, "a") as all_file:
            all_file.write(f"{num}\n")
    producer_done.set()

def consume_even_numbers():
    while not producer_done.is_set() or number_buffer:
        items_available.wait()
        with stack_access_lock:
            if number_buffer and number_buffer[-1] % 2 == 0:
                num = number_buffer.pop()
                with open(even_numbers_file_path, "a") as even_file:
                    even_file.write(f"{num}\n")
            items_available.clear() if not number_buffer else items_available.set()

def consume_odd_numbers():
    while not producer_done.is_set() or number_buffer:
        items_available.wait()
        with stack_access_lock:
            if number_buffer and number_buffer[-1] % 2 != 0:
                num = number_buffer.pop()
                with open(odd_numbers_file_path, "a") as odd_file:
                    odd_file.write(f"{num}\n")
            items_available.clear() if not number_buffer else items_available.set()

if __name__ == "__main__":
    start_time = time.time()

    # Initialize threads
    producer_thread = threading.Thread(target=produce_numbers)
    even_consumer_thread = threading.Thread(target=consume_even_numbers)
    odd_consumer_thread = threading.Thread(target=consume_odd_numbers)

    # Start threads
    producer_thread.start()
    even_consumer_thread.start()
    odd_consumer_thread.start()

    # Wait for threads to finish
    producer_thread.join()
    even_consumer_thread.join()
    odd_consumer_thread.join()

    end_time = time.time()
    
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")
