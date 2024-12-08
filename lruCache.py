from typing import Dict
from linkList import Node, LinkedList
from performance_statistics import PerformanceStatistics
import json
import os
import time

class LRUCache:
    """
    Implementation of cache storage with LRU eviction policy
    """
    capacity: int
    cache_map: Dict[int, Node]
    history: LinkedList
    disk_path: str
    stats: PerformanceStatistics

    def __init__(self, capacity: int, disk_path: str = "cache_disk"):
        self.capacity = capacity
        self.cache_map = {}
        self.history = LinkedList()
        self.disk_path = disk_path
        self.stats = PerformanceStatistics()
        if not os.path.exists(self.disk_path):
            os.makedirs(self.disk_path)

    def get(self, key: int) -> int:
        """
        Retrieve value by its key or -1 otherwise
        """
        self.stats.record_read_request()
        start_time = time.time()
        if key in self.cache_map:
            value_node: Node = self.cache_map[key]
            if self.history.head != value_node:
                # make item the most recently used
                self.history.unlink(value_node)
                self.history.add_to_head(value_node)
            self.stats.record_hit()
            self.stats.record_cache_read_time(start_time)
            return value_node.value
        else:
            # Try to read from disk
            value = self.read_from_disk(key)
            if value != -1:
                self.stats.record_hit()
            else:
                self.stats.record_miss()
            self.stats.record_disk_read_time(start_time)
            return value

    def put(self, key: int, value: int) -> None:
        """
        Add a new key-value pair to the cache.
        If key exists, replace its value by a new one.
        If capacity is reached, evict the LRU item and insert a new pair
        """
        self.stats.record_write_request()
        value_node: Node = Node(key, value)

        if key in self.cache_map:
            self.remove_item(self.cache_map[key])

        if len(self.cache_map) >= self.capacity:
            # no space left, needs to evict the least recently used item
            self.evict_least_recent_item()

        self.history.add_to_head(value_node)
        self.cache_map[key] = value_node

    def evict_least_recent_item(self) -> None:
        """
        Evict the least recently used item
        """
        lru_item: Node = self.history.tail

        if lru_item is None:
            return

        self.write_to_disk(lru_item.key, lru_item.value)
        self.remove_item(lru_item)

    def remove_item(self, item: Node) -> None:
        """
        Remove item represented by node from the map and the list
        """
        self.history.unlink(item)
        del self.cache_map[item.key]
        del item

    def write_to_disk(self, key: int, value: int) -> None:
        """
        Write the key-value pair to the disk
        """
        file_path = os.path.join(self.disk_path, f"{key}.json")
        with open(file_path, 'w') as f:
            json.dump({key: value}, f)

    def read_from_disk(self, key: int) -> int:
        """
        Read the key-value pair from the disk
        """
        file_path = os.path.join(self.disk_path, f"{key}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data[str(key)]
        return -1