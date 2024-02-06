from re import S
import unittest
import asyncio
from time import sleep
from threading import enumerate as threads

from asynchronizer.utils import __python_version__
from asynchronizer import Asynchronizer, asynchronize


class TestThreadCount(unittest.TestCase):
    @property
    def threads(self):
        return threads()

    def test_thread_closure(self):
        # asynchronize decorator creates a new thread
        self.assertEqual(len(self.threads), 1)

        a = Asynchronizer()
        self.assertEqual(len(self.threads), 2)
        b = Asynchronizer()
        self.assertEqual(len(self.threads), 3)
        a.close()
        b.close()

        # Only thread left is asynchronize decorator
        self.assertEqual(len(self.threads), 1)

        if __python_version__ > (3, 8):
        # Test context managers are closing properly
            with (Asynchronizer(), Asynchronizer(), Asynchronizer()):
                self.assertEqual(len(self.threads), 4)
            self.assertEqual(len(self.threads), 1)

    def test_thread_closure_with_exception(self):
        self.assertEqual(len(self.threads), 1)
        with self.assertRaises(Exception):
            with Asynchronizer() as asyncr:
                raise Exception("Test exception")
        self.assertEqual(len(self.threads), 1)

        async def long_running_task():
            await asyncio.sleep(5)
            raise Exception("Test exception")

        with Asynchronizer() as asyncr:
            asyncr.create_task(long_running_task)
            sleep(6)
        self.assertEqual(len(self.threads), 1)


    def test_thread_closure_with_shutdown(self):
        async def long_running_task():
            print("Long running task running...")
            await asyncio.sleep(5)

        async def infinite_task():
            while True:
                print("Infinite task running...")
                await asyncio.sleep(1)

        self.assertEqual(len(self.threads), 1)

        with Asynchronizer() as asyncr:
            asyncr.create_task(long_running_task)
            self.assertEqual(len(self.threads), 2)
            sleep(1)

        self.assertEqual(len(self.threads), 1)

        with Asynchronizer() as asyncr:
            asyncr.create_task(infinite_task())
            self.assertEqual(len(self.threads), 2)
            sleep(3)

        self.assertEqual(len(self.threads), 1)


class TestAsynchronizer(unittest.TestCase):
    def test_create_task(self):
        async def async_task():
            await asyncio.sleep(1)
            return "Async task completed"

        def sync_task():
            return "Sync task completed"

        async def non_awaitable_task():
            print("Non-awaitable task")

        with Asynchronizer() as asyncr:
            # Test creating and scheduling an async task
            task1 = asyncr.create_task(async_task)

            # Test creating and scheduling a sync task
            task2 = asyncr.create_task(sync_task)

            # Test creating and scheduling a non-awaitable task
            task3 = asyncr.create_task(non_awaitable_task)

            # Includes the task that is running the background loop to check for stop events
            self.assertEqual(len(asyncr.tasks), 3)
            if __python_version__ > (3, 8):
            # Task 2 gets submitted to a threadpool
            # it will not be included in the list of tasks
                for task in asyncr.tasks:
                    if task.get_name() == "Task-1":
                        self.assertEqual(task, task1)
                    elif task.get_name() == "Task-2":
                        self.assertEqual(task, task3)

    def test_run_async(self):
        async def async_task():
            await asyncio.sleep(1)
            return "Async task completed"

        def sync_task():
            return "Sync task completed"

        with Asynchronizer() as asyncr:
            # Test running an async task asynchronously
            result1 = asyncr.run_async(async_task)

            # Test running a sync task asynchronously
            result2 = asyncr.run_async(sync_task)

            self.assertEqual(result1, "Async task completed")
            self.assertEqual(result2, "Sync task completed")

    def test_run(self):
        async def async_task():
            await asyncio.sleep(1)
            return "Async task completed"

        def sync_task():
            return "Sync task completed"

        with Asynchronizer() as asyncr:
            # Test running an async task
            result1 = asyncr.run(async_task)

            # Test running a sync task
            result2 = asyncr.run(sync_task)

            self.assertEqual(result1, "Async task completed")
            self.assertEqual(result2, "Sync task completed")

    def test_run_with_args(self):
        async def async_task(arg1, arg2):
            await asyncio.sleep(1)
            return arg1 + arg2

        def sync_task(arg1, arg2):
            return arg1 + arg2

        with Asynchronizer() as asyncr:
            # Test running an async task with arguments
            result1 = asyncr.run(async_task, 1, 2)

            # Test running a sync task with arguments
            result2 = asyncr.run(sync_task, 1, 2)

            self.assertEqual(result1, 3)
            self.assertEqual(result2, 3)
            self.assertEqual(len(asyncr.tasks), 1)


class Test_asynchronize(unittest.TestCase):
    def test_asynchronize_no_args(self):
        @asynchronize
        async def async_task():
            await asyncio.sleep(1)
            return "Async task completed"

        @asynchronize
        def sync_task():
            return "Sync task completed"

        self.assertEqual(async_task(), "Async task completed")
        self.assertEqual(sync_task(), "Sync task completed")

    def test_asynchronize_with_args(self):
        @asynchronize
        async def async_task(arg1, arg2):
            await asyncio.sleep(1)
            return arg1 + arg2

        @asynchronize
        def sync_task(arg1, arg2):
            return arg1 + arg2

        self.assertEqual(async_task(1, 2), 3)
        self.assertEqual(sync_task(1, 2), 3)
        self.assertEqual(async_task(2, 3), 5)
        self.assertEqual(sync_task(2, 3), 5)

    def test_asynchronize_with_kwargs(self):
        @asynchronize
        async def async_task(arg1=1, arg2=2):
            await asyncio.sleep(1)
            return arg1 + arg2

        @asynchronize
        def sync_task(arg1=1, arg2=2):
            return arg1 + arg2

        self.assertEqual(async_task(), 3)
        self.assertEqual(sync_task(), 3)
        self.assertEqual(async_task(arg1=2, arg2=3), 5)
        self.assertEqual(sync_task(arg1=2, arg2=3), 5)

if __name__ == "__main__":
    unittest.main()