import threading
import time
from threading import Thread

def countdown(name, delay, count):
    while count:
        time.sleep(delay)
        print (f'{name, time.ctime(time.time()), count}')
        count -= 1

class newThread(Thread):
    def __init__(self, name, count):
        threading.Thread.__init__(self)
        self.name = name
        self.count = count
    def run(self):
        print("Starting: " + self.name + "\n")
        countdown(self.name, 1,self.count)
        print("Exiting: " + self.name + "\n")

t = newThread("Thread 1", 5)
t.start()
t.join()
print("Exiting Main Thread")
