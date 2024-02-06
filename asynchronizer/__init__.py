from atexit import register
from functools import wraps
from asyncio import (
    new_event_loop,
    set_event_loop,
    run_coroutine_threadsafe,
)
from inspect import (
    iscoroutinefunction,
    iscoroutine,
)

from .thread import AsyncLoopThread as _AsyncLoopThread


# The `Asynchronizer` class provides methods for running functions asynchronously in a separate
# thread.
class Asynchronizer:
    '''
    The Asynchronizer class provides a convenient way to run functions and coroutines asynchronously in a separate thread.

    Attributes
    ----------
    ID : int
        The ID of the Asynchronizer instance.

    Methods
    -------
    __init__()
        Initializes a new instance of the Asynchronizer class.
    __enter__()
        Returns the Asynchronizer instance.
    __exit__(exc_type, exc_value, exc_traceback)
        Closes the Asynchronizer instance.
    _start_background_loop()
        Starts a background loop and runs it forever if it is not already running.
    _create_thread()
        Creates a thread if it doesn't already exist and starts it.
    close()
        Stops the thread and closes the event loop.
    create_task(func, args=tuple(), kwargs=dict())
        Creates a task in a separate thread and schedules it for execution.
    run_async(func, *_args, args=tuple(), kwargs=dict())
        Runs a given function asynchronously, either as a coroutine or a regular function.
    run(func, *_args, args=tuple(), kwargs=dict())
        Runs a given function asynchronously, either as a coroutine or a regular function.

    '''

    ID = 0

    def __init__(self):
        Asynchronizer.ID += 1
        self.id = Asynchronizer.ID
        self._loop = new_event_loop()
        self._create_thread()
        register(self.close)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            from traceback import print_exception
            print_exception(exc_type, exc_value, exc_traceback)
        self.close()

    def _start_background_loop(self):
        '''
        The function starts a background loop and runs it forever if it is not already running.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop that will be used to run asynchronous tasks.

        Returns
        -------
        loop : asyncio.AbstractEventLoop
            The loop object.

        '''
        set_event_loop(self._loop)
        return self._loop

    def _create_thread(self):
        '''
        The function creates a thread if it doesn't already exist and starts it.
        '''
        if not hasattr(self, "_thread"):
            self._thread = _AsyncLoopThread(target=self._start_background_loop, name=f"Asynchronizer-{self.id}", daemon=True)
            self._thread.start()

    def close(self):
        '''
        Stops the thread and closes the event loop.
        '''
        if not self._thread.stopped:
            self._thread.stop()
            self._loop.close()

    def create_task(self, func, args=tuple(), kwargs=dict()):
        '''
        Creates a task in a separate thread and schedules it for execution.

        Parameters
        ----------
        func : callable
            The function that you want to schedule or create a task for.
        args : tuple, optional
            Positional arguments that will be passed to the function when it is called.
        kwargs : dict, optional
            Keyword arguments to be passed to the function when it is called.

        '''
        self._create_thread()

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if iscoroutine(func):
            self.loop.create_task(func)

        if not iscoroutinefunction(func):
            print("Nonawaitable cannot be scheduled.")

        self.loop.create_task(func(*args, **kwargs))

    def run_async(self, func, *_args, args=tuple(), kwargs=dict()):
        '''
        Runs a given function asynchronously, either as a coroutine or a regular function.

        Parameters
        ----------
        func : callable
            The function that you want to run asynchronously.
        args : tuple, optional
            Arguments that will be passed to the function when it is called.
        kwargs : dict, optional
            Keyword arguments to be passed to the function.

        Returns
        -------
        result : object
            The return value depends on the type of `func`.

        '''
        self._create_thread()

        if _args:
            args = (*_args, *args)

        if not isinstance(args, (list, set, tuple)):
            args = (args,)

        if iscoroutine(func):
            return run_coroutine_threadsafe(func, self._thread._loop).result()

        elif not iscoroutinefunction(func):
            return func(*args, **kwargs)

        else:
            return run_coroutine_threadsafe(func(*args, **kwargs), self._loop).result()

    def run(self, func, *_args, args=tuple(), kwargs=dict()):
        '''
        Runs a given function asynchronously, either as a coroutine or a regular function.

        Parameters
        ----------
        func : callable
            The function that you want to run asynchronously.
        args : tuple, optional
            Arguments that will be passed to the function when it is called.
        kwargs : dict, optional
            Keyword arguments to be passed to the function.

        Returns
        -------
        result : object
            The return value depends on the type of `func`.

        '''
        if _args:
            args = (*_args, *args)
        return self.run_async(func=func, args=args, kwargs=kwargs)


# The `asynchronize` class is a decorator that allows a function to be executed asynchronously.
class asynchronize(Asynchronizer):
    """
    Decorator class that allows a function to be executed asynchronously.
    """

    _thread_started = False

    def __init__(self, func):
        self.func = func
        wraps(self.func)(self)

        if not self._thread_started:
            self.__class__._thread = _AsyncLoopThread(target=self._start_background_loop, name="asynchronize-decorator", daemon=True)
            self._loop = new_event_loop()
            self._thread.start()
            asynchronize._thread_started = True
            register(self.close)

    def __call__(self, *args, **kwargs):
        return self.run_async(self.func, *args, kwargs=kwargs)

    @classmethod
    def close(cls):
        cls._thread.stop()
