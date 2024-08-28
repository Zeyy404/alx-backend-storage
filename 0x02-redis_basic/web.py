#!/usr/bin/env python3
"""A module to fetch and cache web pages"""
import redis
import requests
import functools
from typing import Callable


redis_client = redis.Redis()


def cache_page(method: Callable) -> Callable:
    """Decorator to cache page content with expiration."""
    @functools.wraps(method)
    def wrapper(url: str) -> str:
        cache_key = f"content:{url}"

        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode('utf-8')

        content = method(url)
        redis_client.setex(cache_key, 10, content)

        return content

    return wrapper


@cache_page
def get_page(url: str) -> str:
    """Fetch and return the HTML content of a given URL."""
    count_key = f"count:{url}"
    redis_client.incr(count_key)

    response = requests.get(url)
    response.raise_for_status()

    return response.text
