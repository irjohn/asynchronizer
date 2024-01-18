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

from uvloop import EventLoopPolicy as _EventLoopPolicy

from .thread import AsyncLoopThread as _AsyncLoopThread


_set_event_loop_policy(_EventLoopPolicy())
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



# The `Asynchronizer` class provides methods for running functions asynchronously in a separate
# thread.
class Asynchronizer:
    def __init__(self):
        self._create_thread()
        _register(self.close)
        #self._register_handler()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            from traceback import print_exception
            print_exception(exc_type, exc_value, exc_traceback)
        self.close()


    def _start_background_loop(loop):
        '''The function starts a background loop and runs it forever if it is not already running.

        Parameters
        ----------
        loop
            The `loop` parameter is an instance of the `asyncio.AbstractEventLoop` class. It represents the
        event loop that will be used to run asynchronous tasks.

        Returns
        -------
            The loop object is being returned.

        '''
        _set_event_loop(loop)
        if not loop.is_running():
            loop.run_forever()
        return loop


    def _create_thread(self):
        '''The function creates a thread if it doesn't already exist and starts it.
        '''
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
        '''The function creates a task in a separate thread and schedules it for execution.

        Parameters
        ----------
        func
            The `func` parameter is the function that you want to schedule or create a task for. It should be a
        callable object, such as a function or a coroutine function.
        args
            args is a tuple of positional arguments that will be passed to the function when it is called.
        kwargs
            The `kwargs` parameter is a dictionary that contains keyword arguments to be passed to the `func`
        function when it is called. It allows you to specify additional arguments by their names.

        '''
        self._create_thread()

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if _iscoroutine(func):
            self.loop.create_task(func)

        if not _iscoroutinefunction(func):
            print("Nonawaitable cannot be scheduled.")

        self.loop.create_task(func(*args, **kwargs))


    def run_async(self, func, args=tuple(), kwargs=dict()):
        '''The `run_async` function creates a new thread and runs a given function asynchronously, either as a
        coroutine or a regular function.

        Parameters
        ----------
        func
            The `func` parameter is the function that you want to run asynchronously. It can be any callable
        object, such as a function, method, or coroutine function.
        args
            args is a tuple of arguments that will be passed to the function when it is called.
        kwargs
            The `kwargs` parameter is a dictionary that contains keyword arguments to be passed to the `func`
        function. These keyword arguments are used when calling the `func` function along with the `args`
        arguments.

        Returns
        -------
            The return value depends on the type of `func`.

        '''
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


# The `asynchronize` class is a decorator that allows a function to be executed asynchronously.
class asynchronize(Asynchronizer):
    _thread = _AsyncLoopThread(target=get_event_loop, daemon=True)
    _thread_started = False

    def __init__(self, func):
        _wraps(func)(self)
        self.func = func
        if not self._thread_started:
            self._thread.start()

            asynchronize._thread_started = True
            _register(self.close)


    def __call__(self, *args, **kwargs):
        results = self.run_async(self.func, args=args, kwargs=kwargs)
        return results


    @classmethod
    def close(cls):
        cls._thread.stop()
