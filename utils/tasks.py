import asyncio
import time
import random

from asynchronizer import asynchronize

class Tasks:
    RNG = random.Random()

    @classmethod
    async def atask(cls, n):
        print(f"Starting task {n}")
        await asyncio.sleep(cls.RNG.uniform(0,3))
        print(f"Finished task {n}")

    
    @classmethod
    @asynchronize
    async def atasks(cls, n):
        async with asyncio.TaskGroup() as tg:
            tasks = tuple(tg.create_task(cls.atask(x)) for x in range(n))
        return tuple(task.result() for task in tasks)
        

    @classmethod
    def task(cls, n):
        print(f"Starting task {n}")
        time.sleep(cls.RNG.uniform(0,3))
        print(f"Finished task {n}")        


    @classmethod
    @asynchronize
    def tasks(cls, n):
        return tuple(cls.task(x) for x in range(n))