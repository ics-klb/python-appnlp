# -*- coding: utf-8 -*-
from botnlp.storage.adapter import StorageAdapter

class DataStoreAdapter(StorageAdapter):
    """
    This is an class that represents the interface
    that all storage adapters should implement.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)