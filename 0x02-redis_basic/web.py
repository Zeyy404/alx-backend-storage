#!/usr/bin/env python3
"""A module to fetch and cache web pages"""
import redis
import requests
from typing import Callable


redis_client = redis.Redis()


def cache_page(method: Callable) -> Callable:
    """Decorator to cache page content with expiration."""
    def wrapper(url: str) -> str:
        redis_client.incr(f"count:{url}")
        cached_content = redis_client.get(f"cache_page:{url}")
        if cached_content:
            return cached_content.decode('utf-8')

        content = method(url)
        redis_client.set(f"count:{url}", 0)
        redis_client.setex(f"content:{url}", 10, content)

        return content

    return wrapper


@cache_page
def get_page(url: str) -> str:
    """Fetch and return the HTML content of a given URL."""
    response = requests.get(url)
    response.raise_for_status()

    return response.text
