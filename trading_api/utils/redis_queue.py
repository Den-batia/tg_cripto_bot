import redis


class NotificationsQueue:
    __db = redis.Redis(host='redis')
    key = 'queue:notifications'

    @classmethod
    def qsize(cls):
        return cls.__db.llen(cls.key)

    @classmethod
    def empty(cls):
        return cls.qsize() == 0

    @classmethod
    def put(cls, item):
        cls.__db.rpush(cls.key, item)

    @classmethod
    def get(cls, block=True, timeout=None):
        if block:
            item = cls.__db.blpop(cls.key, timeout=timeout)
        else:
            item = cls.__db.lpop(cls.key)

        if item:
            item = item[1]
        return item

    @classmethod
    def get_nowait(cls):
        return cls.get(False)
