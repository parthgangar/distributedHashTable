import time

class PerformanceStatistics:
    def __init__(self):
        self.hit_count = 0
        self.miss_count = 0
        self.read_requests = 0
        self.write_requests = 0
        self.cache_read_time = 0
        self.disk_read_time = 0

    def record_hit(self):
        self.hit_count += 1

    def record_miss(self):
        self.miss_count += 1

    def record_read_request(self):
        self.read_requests += 1

    def record_write_request(self):
        self.write_requests += 1

    def record_cache_read_time(self, start_time):
        self.cache_read_time += time.time() - start_time

    def record_disk_read_time(self, start_time):
        self.disk_read_time += time.time() - start_time

    def get_hit_rate(self):
        total_requests = self.hit_count + self.miss_count
        return self.hit_count / total_requests if total_requests > 0 else 0

    def get_statistics(self):
        return {
            "hit_rate": self.get_hit_rate(),
            "read_requests": self.read_requests,
            "write_requests": self.write_requests,
            "cache_read_time": self.cache_read_time,
            "disk_read_time": self.disk_read_time
        }