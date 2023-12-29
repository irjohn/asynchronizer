from functools import wraps as _wraps
from asyncio import (
    get_event_loop as _get_event_loop,
    new_event_loop as _new_event_loop,
    set_event_loop as _set_event_loop,
    run_coroutine_threadsafe as _run_coroutine_threadsafe,
)

from inspect import (
    iscoroutinefunction as _iscoroutinefunction,
    iscoroutine as _iscoroutine,
)

from threading import (
    Thread as _Thread,
)

from atexit import (
    register as _register,
)


#def asynchronize(func):
#    @wraps(func)
#    def wrapper(*args, kill_context=False, **kwargs):
#        with Asynchronizer(kill_context=kill_context) as executor:
#            results = executor.run_async(func, args=args, kwargs=kwargs)
#        return results
#    return wrapper


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
    def __init__(self, loop=None, kill_context=False):
        self._kill_context = kill_context
        self._loop = loop or get_event_loop()
        self._register_handler()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            from traceback import print_exception
            print_exception(exc_type, exc_value, exc_traceback)
        if self._kill_context:
            self.close()


    def _register_handler(self):
        _register(self.close)


    @staticmethod
    def _start_background_loop(loop):
        _set_event_loop(loop)
        if not loop.is_running():
            loop.run_forever()


    def _create_thread(self):
        if not hasattr(self, "_loop"):
            self._loop = get_event_loop()
        if not hasattr(self, "_thread"):
            self._thread = _Thread(target=self._start_background_loop, args=(self._loop,), daemon=True)
            self._thread.start()


    def close(self):
        if hasattr(self, "_loop"):
            self._loop.stop()
            del self._loop


    def run_async(self, func, args=tuple(), kwargs=dict()):
        self._create_thread()

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if _iscoroutine(func):
            return _run_coroutine_threadsafe(func, self._loop).result()

        if not _iscoroutinefunction(func):
            return func(*args, **kwargs)
        return _run_coroutine_threadsafe(func(*args, **kwargs), self._loop).result()


    def run(self, func, args=tuple(), kwargs=dict()):
        if not isinstance(args, (list, set, tuple)):
            args = (args,)
        return self.run_async(func=func, args=args, kwargs=kwargs)


class asynchronize(Asynchronizer):
    _loop = get_event_loop()
    _thread = _Thread(target=Asynchronizer._start_background_loop, args=(get_event_loop(),), daemon=True)
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
        if hasattr(cls, "_loop"):
            cls._loop.stop()
            del cls._loop
