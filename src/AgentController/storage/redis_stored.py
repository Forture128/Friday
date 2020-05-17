import redis

HOST_PATH = 'localhost'
PORT = 6379
PASS = '1100'


class RedisStored:

    def __init__(self):
        self._client_redis = redis.Redis(host=HOST_PATH, port=PORT, password=PASS)
        self._key_value = ''
        self._value = ''

    # Set value by key.
    def set_value(self, key, value):
        return self._client_redis.set(key, value)

    # Get value by key.
    def get_value(self, key):
        return self._client_redis.get(key)


if __name__ == '__main__':
    pass
