import redis
from rejson import Client, Path

HOST_PATH = 'localhost'
PORT = 6379
PASS = '1100'


class RedisStored:

    def __init__(self):
        self._client_redis = Client(host=HOST_PATH, port=PORT, decode_responses=True)
        self._key_value = ''
        self._value = ''

    # Set value by key.
    def set_value(self, key, value):
        return self._client_redis.set(key, value)

    # Get value by key.
    def get_value(self, key):
        return self._client_redis.get(key)

    # Set value json format by key.
    def set_json_value(self, key, json_value):
        return self._client_redis.jsonset(key, Path.rootPath(), json_value)

    # Get value json format by key.
    def get_json_value(self, key):
        return self._client_redis.jsonget(key, Path('.truth.coord'))

    # Update value json.
    def update_json_value(self, key, new_json_value):
        return self._client_redis.jsonset(key, Path('.answer'), new_json_value)


if __name__ == '__main__':
    pass
