#!/usr/bin/env python3
"""Cache class module"""
import redis
import uuid
import functools
from typing import Union, Optional, Callable, Any


def count_calls(method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to count the number of times a method is called."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = f"count:{method.__qualname__}"
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    
    return wrapper

class Cache:
    """Cache class for interacting with Redis"""
    def __init__(self) -> None:
        """
        Initialize the Cache class with a Redis client and flush the database
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable[[bytes], Optional[any]]] = None) -> Optional[any]:
        """
        Retrieves data from Redis and apply a conversion function if provided
        """
        data = self._redis.get(key)
        if data is None:
            return None

        if fn:
            return fn(data)

        return data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve the data as a UTF-8 string"""
        return self.get(key, fn=lambda x: x.decode('utf-8')
                        if x is not None else None)

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve the data as an integer"""
        return self.get(key, fn=lambda x: int(x) if x is not None else None)
