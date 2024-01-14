from functools import wraps as _wraps
from asyncio import (
    set_event_loop_policy as _set_event_loop_policy,
    get_event_loop as _get_event_loop,
    new_event_loop as _new_event_loop,
    set_event_loop as _set_event_loop,
    run_coroutine_threadsafe as _run_coroutine_threadsafe,
)

from inspect import (
    iscoroutinefunction as _iscoroutinefunction,
    iscoroutine as _iscoroutine,
)


from atexit import (
    register as _register,
)

import uvloop as _uvloop

from .thread import AsyncLoopThread as _AsyncLoopThread


_set_event_loop_policy(_uvloop.EventLoopPolicy())
def get_event_loop():
    try:
        loop = _get_event_loop()
    except RuntimeError:
        loop = _new_event_loop()
        _set_event_loop(loop)
    if loop.is_running():
        loop = _new_event_loop()
        _set_event_loop(loop)
    return loop



class Asynchronizer:
    def __init__(self):
        self._create_thread()
        self._register_handler()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            from traceback import print_exception
            print_exception(exc_type, exc_value, exc_traceback)
        self.close()


    def _register_handler(self):
        _register(self.close)


    def _start_background_loop(loop):
        _set_event_loop(loop)
        if not loop.is_running():
            loop.run_forever()
        return loop


    def _create_thread(self):
        if not hasattr(self, "_thread"):
            self._thread = _AsyncLoopThread(target=get_event_loop, daemon=True)
            self._thread.start()


    @property
    def loop(self):
        if not hasattr(self, "_thread"):
            self._create_thread()
        return self._thread._loop


    def close(self):
        if not self._thread.stopped:
            self._thread.stop()


    def create_task(self, func, args=tuple(), kwargs=dict()):
        self._create_thread()

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if _iscoroutine(func):
            self.loop.create_task(func)

        if not _iscoroutinefunction(func):
            print("Nonawaitable cannot be scheduled.")

        self.loop.create_task(func(*args, **kwargs))


    def run_async(self, func, args=tuple(), kwargs=dict()):
        self._create_thread()

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if _iscoroutine(func):
            return _run_coroutine_threadsafe(func, self._thread._loop).result()

        if not _iscoroutinefunction(func):
            return func(*args, **kwargs)
        return _run_coroutine_threadsafe(func(*args, **kwargs), self._thread._loop).result()


    def run(self, func, *_args, args=tuple(), kwargs=dict()):
        if _args:
            args = (*_args, *args)
        return self.run_async(func=func, args=args, kwargs=kwargs)


class asynchronize(Asynchronizer):
    _thread = _AsyncLoopThread(target=get_event_loop, daemon=True)
    _thread_started = False

    def __init__(self, func):
        _wraps(func)(self)
        self.func = func
        if not self._thread_started:
            self._thread.start()

            asynchronize._thread_started = True
            self._register_handler()


    def __call__(self, *args, **kwargs):
        results = self.run_async(self.func, args=args, kwargs=kwargs)
        return results


    @classmethod
    def close(cls):
        cls._thread.stop()
