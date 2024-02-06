import asyncio
import threading
from time import sleep

from .utils import create_task

# The `EventLoopThread` class is a subclass of `threading.Thread` that runs an asynchronous event loop until it
# is stopped.
class EventLoopThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()


    def run(self):
        self._loop = self._target()
        asyncio.set_event_loop(self._loop)
        self._stop_task = create_task(self._loop, self.check_stop(), name="Check Stop")
        self._loop.run_forever()
        return


    async def check_stop(self):
        while not self.stopped:
            await asyncio.sleep(0)
        self.shutdown()

    def shutdown(self):
        tasks = asyncio.all_tasks(loop=self._loop)
        for task in tasks:
            task.cancel()
        self._loop.stop()

    def stop(self):
        self._stop_event.set()
        while self._loop.is_running():
            sleep(0.1)


    @property
    def stopped(self):
        return self._stop_event.is_set()