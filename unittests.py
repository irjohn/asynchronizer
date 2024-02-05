import unittest
from threading import enumerate as threads

from asynchronizer import Asynchronizer, asynchronize
from asynchronizer.utils import Tasks


class TestThreadCount(unittest.TestCase):
    @property
    def threads(self):
        return threads()


    def test_thread_closure(self):
        self.assertEqual(len(self.threads), 2)
        a = Asynchronizer()
        self.assertEqual(len(self.threads), 3)
        b = Asynchronizer()
        self.assertEqual(len(self.threads), 4)
        a.close()
        b.close()

        self.assertEqual(len(self.threads), 2)
        with (Asynchronizer(), Asynchronizer(), Asynchronizer()):
            self.assertEqual(len(self.threads), 5)
        self.assertEqual(len(self.threads), 2)


if __name__ == "__main__":
    unittest.main()