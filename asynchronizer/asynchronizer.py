import time as _time
from random import Random as _Random
import asyncio as _asyncio
from functools import wraps
from inspect import iscoroutinefunction as _iscoroutinefunction
from threading import (
    Thread as _Thread, 
    Event as _Event
)


def asynchronize(func):
    @wraps(func)
    def wrapper(*args, kill_context=False, set_loop=False, **kwargs):
        with Asynchronizer(kill_context=kill_context) as executor:
            results = executor.run_async(func, args=args, kwargs=kwargs)
            if set_loop:
                print(args[0])
                args[0]._loop = executor._loop
        return results
    return wrapper



def _create_thread_(func):
    @wraps(func)
    def run_task(self, *args, **kwargs):
        if not hasattr(self, "_thread"):
            if not hasattr(self, "_loop"):
                self._loop = _asyncio.get_event_loop()
            self._create_thread()
        return func(self, *args, **kwargs)
    return run_task


def get_event_loop():
    try:
        loop = _asyncio.get_event_loop()
    except RuntimeError:
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
    if loop.is_running():
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
    return loop


class _AsyncThread(_Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(_AsyncThread, self).__init__(*args, **kwargs)
        self._stop_event = _Event()


    def stop(self):
        self._stop_event.set()


    def stopped(self):
        return self._stop_event.is_set()


class Asynchronizer:
    #@_create_thread_
    def __init__(self, loop=None, kill_context=False):
        self._kill_context = kill_context
        self._loop = loop or get_event_loop()


    #@_create_thread_
    def __enter__(self):
        return self
    
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            from traceback import print_exception
            print_exception(exc_type, exc_value, exc_traceback)
        if self._kill_context:
            self.close()


    @staticmethod
    def _start_background_loop(loop):
        _asyncio.set_event_loop(loop)
        if not loop.is_running():
            loop.run_forever()


    def _create_thread(self):
        if not hasattr(self, "_loop"):
            self._loop = get_event_loop()
        if not hasattr(self, "_thread"):
            self._thread = _AsyncThread(target=self._start_background_loop, args=(self._loop,), daemon=True)
            self._thread.start()


    def close(self):
        self._thread.stop()
        del self._thread
        self._loop.stop()
        del self._loop
    

    #@_create_thread_
    def run_async(self, func, args=tuple(), kwargs=dict()):
        if not isinstance(args, (list, set, tuple)):
            args = (args,)
        self._create_thread()
        if not _iscoroutinefunction(func):
            return func(*args, **kwargs)  
        return _asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop).result()


    def run(self, func, args=tuple(), kwargs=dict()):
        if not isinstance(args, (list, set, tuple)):
            args = (args,)
        return self.run_async(func=func, args=args, kwargs=kwargs)



async def _atask(x, sleep):
    print(f"Starting {x}")
    await _asyncio.sleep(sleep)
    print(f"Finished {x}")


async def _atasks(n=5):
    rng = _Random()
    return await _asyncio.gather(*[_atask(y, rng.uniform(0, 5)) for y in range(n)])


def _stask(x, sleep):
    print(f"Starting {x}")
    _time.sleep(sleep)
    print(f"Finished {x}")
    return x


def _stasks(n=5):
    
    from random import Random
    rng = Random()
    return tuple(_stask(y, rng.uniform(0, 5)) for y in range(n))


print("Testing kali")