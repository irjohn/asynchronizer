import unittest
import threading
from asynchronizer import (
    Asynchronizer,
    get_event_loop,
)

from asynchronizer.utils import Tasks

import time

class TestThreadCount(unittest.TestCase):
    @property
    def threads(self):
        return threading.enumerate()


    def test_thread_closure(self):
        self.assertEqual(len(self.threads), 2)
        a = Asynchronizer()
        self.assertEqual(len(self.threads), 3)
        b = Asynchronizer()
        self.assertEqual(len(self.threads), 4)
        a.close()
        b.close()
        time.sleep(0.25)
        self.assertEqual(len(self.threads), 2)
        with Asynchronizer():
            self.assertEqual(len(self.threads), 3)
        time.sleep(0.25)
        self.assertEqual(len(self.threads), 2)


if __name__ == "__main__":
    unittest.main()