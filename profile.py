# mprof run --multiprocess profile.py
# mprof plot

import subprocess
import threading

def func1():
    subprocess.run(["python3", "main.py", "i"])

def func2():
    subprocess.run(["python3", "main.py", "all"])

thread_1 = threading.Thread(target=func1)
thread_2 = threading.Thread(target=func2)

thread_1.start()
thread_2.start()

