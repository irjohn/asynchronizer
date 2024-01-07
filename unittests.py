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
    with Asynchronizer() as exc:
        exc.run(Tasks.atasks)
    pass