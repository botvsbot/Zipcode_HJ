import json
import logging
import redis


class LocalCache(object):
    """Cache in local memory.

    Fall back when redis is not available. Only set, get, exists
        are supported in this mode.
    """
    _CACHE_DICT = {}

    def __init__(self):
        logging.warn('*** Redis not found. Using local memory. ***')

    def get(self, name):
        return self._CACHE_DICT.get(name)

    def set(self, name, value):
        self._CACHE_DICT[name] = value
        return True

    def exists(self, name):
        return name in self._CACHE_DICT


class JSONRedis(redis.StrictRedis):
    """Adds a pair of set/get functions to cache python objects.

    JSON serialization is used, for human readability() and because speed is
        comparable or faster than cpython.

    Only supports python built-in python types.
    """
    def get(self, name):
        json_value = super(JSONRedis, self).get(name)
        return json.loads(json_value) if json_value else None

    def set(self, name, value, *args, **kwargs):
        return super(JSONRedis, self).set(name, json.dumps(value), *args, **kwargs)
