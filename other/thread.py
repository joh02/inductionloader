import threading
import time
from queue import Queue
'''
# Globale Variable
global_shared_variable = 0

# Lock für die gemeinsame Variable
shared_variable_lock = threading.Lock()

# Datei für den gemeinsamen Zugriff
file_lock = threading.Lock()
file_path = "shared_file.txt"

def thread_function_1():
    global global_shared_variable

    for _ in range(5):
        with shared_variable_lock:
            global_shared_variable += 1
            print(f"Thread 1: Incremented shared_variable to {global_shared_variable}")
            time.sleep(1)

        with file_lock:
            with open(file_path, "a") as file:
                file.write("Thread 1 wrote to file\n")
            print("Thread 1: Wrote to file")
            time.sleep(1)

def thread_function_2():
    global global_shared_variable

    for _ in range(3):
        with shared_variable_lock:
            global_shared_variable -= 1
            print(f"Thread 2: Decremented shared_variable to {global_shared_variable}")
            time.sleep(1)

        with file_lock:
            with open(file_path, "a") as file:
                file.write("Thread 2 wrote to file\n")
            print("Thread 2: Wrote to file")
            time.sleep(1)

# Erstellung der Threads
thread3 = threading.Thread(target=thread_function_1)
thread4 = threading.Thread(target=thread_function_2)

# Start der Threads
thread3.start()
thread4.start()

# Warten, bis beide Threads beendet sind
thread3.join()
thread4.join()

'''
# ----------------------------------------------------------------------------


# example of using the queue
from time import sleep
from random import randint
from threading import Thread
from queue import Queue


# generate work
def producer(queue):
    print('Producer: Start')
    # generate work
    for i in range(10):
        # generate a value
        value = randint(1, 100)
        # block
        sleep(value/10)
        # add to the queue
        queue.put(value)
    # all done
    queue.put(None)
    print('Producer: Done')


# consumer work
def consumer(queue):
    print('Consumer: Start')
    # consume work
    while True:
        # get a unit of work
        item = queue.get()
        # check for stop
        if not item:
            break
        # report
        print(f'>got {item}')
    # all done
    print('Consumer: Done')


# create the shared queue
queue = Queue()
# start the consumer
consumer = Thread(target=consumer, args=(queue,))
consumer.start()
# start the producer
producer = Thread(target=producer, args=(queue,))
producer.start()
# wait for all threads to finish
producer.join()
consumer.join()