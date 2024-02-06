import warnings
from sys import version_info as __version_info__

__python_version__ = (__version_info__.major, __version_info__.minor)

def create_task(loop, coro, name=None, context=None):
    '''
    Creates a task in the given event loop.

    Parameters
    ----------
    loop : asyncio.AbstractEventLoop
        The event loop in which the task will be created.
    func : callable
        The function that you want to run asynchronously.
    args : tuple, optional
        Arguments that will be passed to the function when it is called.
    kwargs : dict, optional
        Keyword arguments to be passed to the function.

    Returns
    -------
    task : asyncio.Task
        The task that was created in the event loop.

    '''

    if __python_version__ == (3,7):
        if name is not None:
            warnings.warn("Warning: The 'name' parameter is not supported in Python 3.7")
        return loop.create_task(coro)

    elif (3,8) <= __python_version__ < (3,11):
        if context is not None:
            warnings.warn("Warning: The 'context' parameter is not supported in Python 3.10 or earlier")
        return loop.create_task(coro, name=name)

    else:
        return loop.create_task(coro, name=name, context=context)