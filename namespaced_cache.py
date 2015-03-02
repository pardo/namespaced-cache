class MockCache():
    def __init__(self):
        self.d = {}

    def set(self, key, value, timeout=0, version=None):
        self.d[key] = value

    def has_key(self, k, version=None):
        return self.d.has_key(k)

    def get_many(self, keys, version=None):
        d = {}
        for k in keys:
            val = self.get(k, version=version)
            if val is not None:
                d[k] = val
        return d

    def clear(self):
        self.d = {}

    def validate_key(self, key):
        return True

    def set_many(self, data, timeout=None, version=None):
        for key, value in data.items():
            self.set(key, value, timeout=timeout, version=version)

    def get(self, key, default=None, version=None):
        return self.d.get(key,default)

    def delete(self, key, version=None):
        try:
            del self.d[key]
        except KeyError:
            pass


class NamespacedCache(object):
    """
        Structure is a
        __root-keys__ -> (
            rootkey1,
            rootkey2
        )

        "__keys-list__" + root-key -> (
            subkey,
            subkey.something,
            subkey.something.a,
            subkey.a
        )

        main.footer.links
        main.footer.articles

        root = main
        base = footer.links

        root = main
        base = footer.articles
    """

    # should not contain the divisor
    namespace_root_key = "__root-keys__" # contains all the root keys
    namespace_base_prefix = "__keys-list__" # contains all the base keys for a root key
    # default to . like namespace.object.specific
    namespace_divisor = "."


    def set_cache(self, cache):
        """
            wraps a valid cache and add a simple namespace support
        """
        self.cache = cache

    def _ns_store(self, key, key_data, version=None):
        # Stores in a set of keys the current key-data
        data = self.cache.get(key, set(), version=version)
        data.add(key_data)
        self.cache.set(key, data, version=version)

    def _ns_delete_(self, key, key_remove, version=None):
        # deletes a key from namespace store
        data = self.cache.get(key, set(), version=version)
        try:
            data.remove(key_remove)
        except KeyError:
            pass
        else:
            self.cache.set(key, data, version=version)

    def _store_base_key(self, root, base, version=None):
        self._ns_store(self.namespace_base_prefix+root, base, version=version)

    def _store_root_key(self, root, version=None):
        self._ns_store(self.namespace_root_key, root, version=version)
        
    def _split(self, key):
        sp = key.split(self.namespace_divisor)
        root = sp[0]
        base = self.namespace_divisor.join(sp[1:])
        return root, base

    def _get_root_keys(self, root):
        base_keys = self.cache.get(self.namespace_base_prefix+root, set())
        keys = []
        for key in base_keys:
            if key == "": #stored value on the root key
                keys.append(root)
            else:
                keys.append(root+self.namespace_divisor+key)
        return keys

    def _get_all_keys(self):
        root_keys = self.cache.get(self.namespace_root_key, set())
        keys = map(lambda k:self._get_root_keys(k), root_keys)
        return reduce(lambda x,y:x.union(y), keys, set())

    def get(self, key, default=None, version=None):
        return self.cache.get(key=key, default=default, version=None)

    def set(self, key, value, timeout=0, version=None):
        """
        """
        self.cache.set(key, value, timeout=timeout, version=version)
        root, base = self._split(key)
        self._store_base_key(root, base, version=version)
        self._store_root_key(root, version=version)

    def delete(self, key, version=None):
        """
        this method can't delete namespaced roots, for that used delete_keys
        """
        self.cache.delete(key=key)
        root, base = self._split(key)
        self._ns_delete_(self.namespace_base_prefix+root, base, version=version)

    def get_many(self, keys, version=None):
        return self.cache.get_many(keys, version)

    def has_key(self, key, version=None):
        return self.cache.has_key(key, version=version)

    def add(self, key, value, timeout=None, version=None):
        return self.cache.add(self, key, value, timeout=timeout, version=version)

    def incr(self, key, delta=1, version=None):
        return self.incr(self, key, delta=delta, version=version)

    def decr(self, key, delta=1, version=None):
        return self.decr(self, key, delta=delta, version=version)

    def set_many(self, data, timeout=None, version=None):
        # we do a lot of key changing before saving
        for key, value in data.items():
            self.set(key, value, timeout=timeout, version=version)

    def delete_many(self, keys, version=None):
        # we do a lot of key changing before deleting
        for key in keys:
            self.delete(key, version=version)

    def clear(self):
        return self.cache.clear()

    def validate_key(self, key):
        return self.cache.validate_key(key)

    def incr_version(self, key, delta=1, version=None):
        raise NotImplementedError

    def decr_version(self, key, delta=1, version=None):
        raise NotImplementedError

    def get_keys(self, pattern=None):
        # pattern
        # "root" all the sub trees under root + "root" key if present
        # "root.subroot" all the sub trees under subroot + subroot if present
        # "root." all the sub tress under root
        # "root.subroot." all the sub trees under subroot

        if pattern is None:
            return list(self._get_all_keys())

        root, base = self._split(pattern)
        keys = self._get_root_keys(root)

        if root.endswith(self.namespace_divisor):
            try:
                keys.remove(root)
            except ValueError:
                pass

        return filter( lambda x:x.startswith(pattern), keys )

    def delete_keys(self, pattern=None):
        keys = self.get_keys(pattern=pattern)

        for key in keys:
            self.delete(key)


try:
    from django.core.cache import BaseCache
except:
    BaseCache = object

class NamespacedCacheDjango(NamespacedCache, BaseCache):
    def __init__(self, cache_name, *args, **kwargs):
        BaseCache.__init__(self, *args, **kwargs)

        if cache_name == "":
            cache_name = "default"

        try:
            #django > 1.7 support
            from django.core.cache import caches
        except ImportError:
            from django.core.cache import get_cache
            self.set_cache(get_cache(cache_name))
        else:
            self.set_cache(caches[cache_name])