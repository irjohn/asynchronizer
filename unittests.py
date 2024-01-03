import asyncio
import unittest
import threading
from asynchronizer import (
    Asynchronizer,
    get_event_loop,
)

from asynchronizer.utils import Tasks

async def _atask(n):
    print(f"[async] Starting task {n}")
    await asyncio.sleep(2)
    print(f"[async] Finished task {n}")

    
async def _atasks(n=5):
    print(f"[async]({n}) Starting...")
    async with asyncio.TaskGroup() as tg:
        tasks = tuple(tg.create_task(_atask(x)) for x in range(n))
    results = tuple(task.result() for task in tasks)
    print(f"[async]({n}) Finished")
    return results

'''
print(Tasks.atasks(5))
print(Tasks.tasks(2))
print(threading.enumerate())


async def main():
    with Asynchronizer() as executor:
        executor.run(_atasks, args=2)
        executor.run(_atasks(2))

loop = get_event_loop()
loop.run_until_complete(main())
print(threading.enumerate())

with Asynchronizer() as exc:
    exc.run_async(_atasks(2))


print(threading.enumerate())

a1 = Asynchronizer()
a2 = Asynchronizer()

a1.run_async(Tasks.atasks)
a2.run(_atasks, 5)
print(threading.enumerate())
'''
import time

class TestThreadCount(unittest.TestCase):
    @property
    def threads(self):
        return threading.enumerate()
    

    def test_thread_closure(self):
        self.assertEqual(len(self.threads), 2)
        a = Asynchronizer()
        self.assertEqual(len(self.threads), 3)
        b = Asynchronizer()
        self.assertEqual(len(self.threads), 4)
        a.close()
        b.close()
        time.sleep(0.25)
        self.assertEqual(len(self.threads), 2)
        with Asynchronizer():
            self.assertEqual(len(self.threads), 3)
        time.sleep(0.25)
        self.assertEqual(len(self.threads), 2)


if __name__ == "__main__":
    pass