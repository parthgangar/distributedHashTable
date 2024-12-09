import sys, socket, threading, re, hashlib, bisect, json
from queue import Queue
from logger import Logger

logger = Logger(name='CoordinatorLogger')

class ConsistentHashing:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self.hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self.hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self.hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

class CoordinatorNode:
    def __init__(self, ip, port, server_addresses):
        self.ip = ip
        self.port = port
        self.server_addresses = server_addresses
        self.server_sockets = {addr: self.connect_to_server(addr) for addr in server_addresses}
        self.request_queue = Queue()
        self.consistent_hashing = ConsistentHashing(nodes=server_addresses)

    def connect_to_server(self, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        return sock

    def forward_request_to_server(self, command):
        set_ht = re.match('^set ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)$', command)
        get_ht = re.match('^get ([a-zA-Z0-9]+)$', command)
        stats_ht = re.match('^stats$', command)

        if set_ht:
            key = set_ht.groups()[0]
            server_address = self.consistent_hashing.get_node(key)
            server_socket = self.server_sockets[server_address]
            server_socket.send(json.dumps([command]).encode())
            response = server_socket.recv(2048).decode()
            return response
        elif get_ht:
            key = get_ht.groups()[0]
            server_address = self.consistent_hashing.get_node(key)
            server_socket = self.server_sockets[server_address]
            server_socket.send(json.dumps([command]).encode())
            response = server_socket.recv(2048).decode()
            return response
        elif stats_ht:
            results = []
            for server_address, server_socket in self.server_sockets.items():
                server_socket.send(json.dumps([command]).encode())
                response = server_socket.recv(2048).decode()
                results.append(json.loads(response)[0])
            aggregated_stats = self.aggregate_stats(results)
            return json.dumps(aggregated_stats, indent=4)
        else:
            return "Error: Invalid command"

    def aggregate_stats(self, stats_list):
        aggregated_stats = {
            "hit_rate": 0,
            "read_requests": 0,
            "write_requests": 0,
            "cache_read_time": 0,
            "disk_read_time": 0
        }
        for stats in stats_list:
            aggregated_stats["hit_rate"] += stats["hit_rate"]
            aggregated_stats["read_requests"] += stats["read_requests"]
            aggregated_stats["write_requests"] += stats["write_requests"]
            aggregated_stats["cache_read_time"] += stats["cache_read_time"]
            aggregated_stats["disk_read_time"] += stats["disk_read_time"]
        num_servers = len(stats_list)
        aggregated_stats["hit_rate"] /= num_servers
        return aggregated_stats

    def process_requests(self):
        while True:
            conn, msg = self.request_queue.get()
            try:
                logger.info(f"Processing request: {msg}")
                commands = json.loads(msg)
                results = [self.forward_request_to_server(command) for command in commands]
                response = json.dumps(results)
                conn.send(response.encode())
            except Exception as e:
                logger.error(f"Error processing request: {e}")
            finally:
                self.request_queue.task_done()

    def process_request(self, conn):
        while True:
            try:
                msg = conn.recv(2048).decode()
                if not msg:
                    break
                self.request_queue.put((conn, msg))
            except Exception as e:
                logger.error(f"Error receiving message from client: {e}")
                break

    def listen_to_clients(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        sock.listen(5)
        logger.info(f"Coordinator listening on {self.ip}:{self.port}")

        request_thread = threading.Thread(target=self.process_requests)
        request_thread.daemon = True
        request_thread.start()

        while True:
            try:
                client_socket, client_address = sock.accept()
                logger.info(f"Connected to new client at address {client_address}")
                my_thread = threading.Thread(target=self.process_request, args=(client_socket,))
                my_thread.daemon = True
                my_thread.start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                break

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python coordinator_node.py <IP> <PORT> <SERVER_IP:SERVER_PORT> ...")
        sys.exit(1)

    ip_address = str(sys.argv[1])
    port = int(sys.argv[2])
    server_addresses = [tuple(addr.split(':')) for addr in sys.argv[3:]]
    server_addresses = [(ip, int(port)) for ip, port in server_addresses]

    coordinator = CoordinatorNode(ip=ip_address, port=port, server_addresses=server_addresses)
    coordinator.listen_to_clients()

    