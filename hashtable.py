from lruCache import LRUCache
class HashTable:
    def __init__(self, capacity=10, disk_path="cache_disk"):
        self.cache = LRUCache(capacity, disk_path)
        
    def set(self, key, value):
        self.cache.put(key, value)
    
    def get(self, key):
        return self.cache.get(key)
