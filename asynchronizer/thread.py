from asyncio import (
    get_event_loop as _get_event_loop,
    new_event_loop as _new_event_loop,
    set_event_loop as _set_event_loop,
    sleep as _asleep,
)


from threading import (
    Thread as _Thread,
    Event as _Event,
)



class AsyncLoopThread(_Thread):
    def __init__(self, *args, **kwargs):
        super(AsyncLoopThread, self).__init__(*args, **kwargs)
        self._stop_event = _Event()
        self._loop = self._target()


    def run(self):
        _set_event_loop(self._loop)
        self._stop_task = self._loop.create_task(self.check_stop())
        self._loop.run_forever()


    async def check_stop(self):
        while True:
            try:
                if self.stopped:
                    self._loop.stop()
                    self._loop.close()
                    return
                await _asleep(0.1)
            except:
                return
    

    def stop(self):
        self._stop_event.set()


    @property
    def stopped(self):
        return self._stop_event.is_set()