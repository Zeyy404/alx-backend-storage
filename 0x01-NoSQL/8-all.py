#!/usr/bin/env python3
"""
a Python function that lists all documents in a collection
"""


def list_all(mongo_collection):
    """
    Lists all documents in a collection
    Returns an empty list if no document in the collection
    """
    documents = list(mongo_collection.find())
    return documents
