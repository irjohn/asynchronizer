from utils import Tasks
import asyncio
import threading

print(Tasks.atasks(5))
print(Tasks.tasks(5))

print(threading.enumerate())
