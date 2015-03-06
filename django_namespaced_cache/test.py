import random
import unittest

from namespaced_cache import NamespacedCache, MockCache

class TestNamespacedCache(unittest.TestCase):

    def setUp(self):
        cache = MockCache()
        self.cache = NamespacedCache()
        self.cache.set_cache(cache)

    def test_get_set(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        self.assertEqual(self.cache.get("a"), 1)
        self.assertEqual(self.cache.get("a.b"), 2)
        self.assertEqual(self.cache.get("a.b.c"), 3)

    def test_delete(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        self.assertTrue(self.cache.has_key("a"))
        self.assertTrue(self.cache.has_key("a.b"))
        self.assertTrue(self.cache.has_key("a.b.c"))

        self.cache.delete("a")
        self.assertFalse(self.cache.has_key("a"))
        self.assertTrue(self.cache.has_key("a.b"))
        self.assertTrue(self.cache.has_key("a.b.c"))

        self.cache.delete("a.b.c")
        self.assertFalse(self.cache.has_key("a"))
        self.assertTrue(self.cache.has_key("a.b"))
        self.assertFalse(self.cache.has_key("a.b.c"))


    def test_clear(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)
        self.cache.clear()

        self.assertFalse(self.cache.has_key("a"))
        self.assertFalse(self.cache.has_key("a.b"))
        self.assertFalse(self.cache.has_key("a.b.c"))

    def test_has_key(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        self.assertTrue(self.cache.has_key("a"))
        self.assertTrue(self.cache.has_key("a.b"))
        self.assertTrue(self.cache.has_key("a.b.c"))

        self.assertFalse(self.cache.has_key("a.b.c.d"))
        self.assertFalse(self.cache.has_key("a.c.d"))
        self.assertFalse(self.cache.has_key("a.d"))
        self.assertFalse(self.cache.has_key("d"))

    def test_set_many(self):
        data = {
            "a": 1,
            "a.b": 2,
            "a.b.c": 3
        }
        self.cache.set_many(data)

        self.assertEqual(self.cache.get("a"), 1)
        self.assertEqual(self.cache.get("a.b"), 2)
        self.assertEqual(self.cache.get("a.b.c"), 3)

    def test_get_many(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        data = self.cache.get_many(["a", "a.b", "a.b.c"])
        self.assertEqual(data, {
            "a": 1,
            "a.b": 2,
            "a.b.c": 3
        })

    def test_delete_many(self):
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        self.cache.delete_many([
            "a",
            "a.b.c"
        ])

        self.assertTrue(self.cache.has_key("a.b"))
        self.assertFalse(self.cache.has_key("a.b.c"))
        self.assertFalse(self.cache.has_key("a"))

    def test_get_keys(self):
        #namespaced feature
        self.cache.set("a", 1)
        self.cache.set("a.b", 2)
        self.cache.set("a.b.c", 3)

        self.cache.set("b", 1)
        self.cache.set("b.b", 2)
        self.cache.set("b.b.c", 3)

        self.cache.set("c.a", 1)
        self.cache.set("c.b", 2)
        self.cache.set("c.c", 3)
        self.cache.set("c.d", 4)

        self.cache.set("d", 1)
        self.cache.set("d.a", 2)
        self.cache.set("d.a.a", 3)
        self.cache.set("d.a.b", 4)
        self.cache.set("d.a.c", 5)
        self.cache.set("d.a.c.a.b", 5)

        all_keys = [
            "a",
            "a.b",
            "a.b.c",

            "b",
            "b.b",
            "b.b.c",

            "c.a",
            "c.b",
            "c.c",
            "c.d",

            "d",
            "d.a",
            "d.a.a",
            "d.a.b",
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys():
            self.assertTrue(key in all_keys, "Key not found '%s' " % key)


        expected_keys = [
            "c.a",
            "c.b",
            "c.c",
            "c.d",
        ]

        for key in self.cache.get_keys("c"):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)


        expected_keys = [
            "c.a",
        ]

        for key in self.cache.get_keys("c.a"):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)


        expected_keys = [
            "d",
            "d.a",
            "d.a.a",
            "d.a.b",
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys("d"):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)

        expected_keys = [
            "d.a",
            "d.a.a",
            "d.a.b",
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys("d."):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)


        expected_keys = [
            "d.a",
            "d.a.a",
            "d.a.b",
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys("d.a"):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)

        expected_keys = [
            "d.a.a",
            "d.a.b",
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys("d.a."):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)

        expected_keys = [
            "d.a.c",
            "d.a.c.a.b"
        ]

        for key in self.cache.get_keys("d.a.c"):
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)

        expected_keys = [
            "a",
            "a.b",
            "a.b.c",

            # "b", deleted
            # "b.b", deleted
            "b.b.c",

            "c.a",
            # "c.b", deleted
            "c.c",
            "c.d",

            "d",
            "d.a",
            "d.a.a",
            "d.a.b",
            # "d.a.c", deleted
            "d.a.c.a.b"
        ]

        self.cache.delete("b")
        self.cache.delete("b.b")
        self.cache.delete("c.b")
        self.cache.delete("d.a.c")

        for key in self.cache.get_keys():
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)

        expected_keys = [
            "a",
            "a.b",
            "a.b.c",

            # "b.b", deleted
            "b.b.c",

            "d"
        ]

        self.cache.delete_keys("c")
        self.cache.delete_keys("d.a")

        for key in self.cache.get_keys():
            self.assertTrue(key in expected_keys, "Key not found '%s' " % key)


if __name__ == '__main__':
    unittest.main()
