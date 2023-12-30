import asyncio
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