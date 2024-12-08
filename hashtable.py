from lruCache import LRUCache
class HashTable:
    def __init__(self, capacity=10):
        self.cache = LRUCache(capacity)
    
    def set(self, key, value):
        self.cache.put(key, value)
    
    def get(self, key):
        return self.cache.get(key)
