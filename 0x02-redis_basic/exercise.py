#!/usr/bin/env python3
"""Cache class module"""
import redis
import uuid
import functools
from typing import Union, Optional, Callable, Any, Type


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of times a method is called."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """Returns the given method after incrementing its call counter"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store function call history."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"

        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(inputs_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(outputs_key, str(result))

        return result

    return wrapper


def replay(cache: Type[Cache], method: Callable) -> None:
    """Display the history of calls to a particular function."""
    redis_client = cache._redis
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"

    inputs = redis_client.lrange(inputs_key, 0, -1)
    outputs = redis_client.lrange(outputs_key, 0, -1)

    num_calls = len(inputs)

    print(f"{method_name} was called {num_calls} times:")

    for index, (input_data, output_data) in enumerate(zip(inputs, outputs), 1):
        input_str = input_data.decode('utf-8')
        output_str = output_data.decode('utf-8')

        print(f"{method_name}(*{input_str}) -> {output_str}")


class Cache:
    """Cache class for interacting with Redis"""
    def __init__(self) -> None:
        """
        Initialize the Cache class with a Redis client and flush the database
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable[[bytes], Optional[any]]] = None) -> Optional[any]:
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
