import asyncio
import time
from random import Random

from . import asynchronize


class Tasks:
    RNG = Random()

    @classmethod
    async def atask(cls, n):
        print(f"[async] Starting task {n}")
        await asyncio.sleep(cls.RNG.uniform(0, 3))
        print(f"[async] Finished task {n}")
        return n

    @classmethod
    @asynchronize
    async def atasks(cls, n=5):
        print(f"[async]({n}) Starting...")
        async with asyncio.TaskGroup() as tg:
            tasks = tuple(tg.create_task(cls.atask(x)) for x in range(n))
        results = tuple(task.result() for task in tasks)
        print(f"[async]({n}) Finished")
        return results

    @classmethod
    def task(cls, n):
        print(f"[sync] Starting task {n}")
        time.sleep(cls.RNG.uniform(0, 3))
        print(f"[sync] Finished task {n}")
        return n

    @classmethod
    @asynchronize
    def tasks(cls, n=5):
        print(f"[sync]({n}) Starting...")
        results = tuple(cls.task(x) for x in range(n))
        print(f"[sync]({n}) Finished")
        return results