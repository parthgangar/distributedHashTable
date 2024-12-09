import hashlib
import socket
import threading
import sys
import json

class KademliaNode:
    def __init__(self, ip, port, k=20, alpha=3):
        self.ip = ip
        self.port = port
        self.id = self.hash(f"{ip}:{port}")
        self.k = k
        self.alpha = alpha
        self.routing_table = [[] for _ in range(160)]
        self.data = {}

    def hash(self, key):
        return int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16)

    def xor_distance(self, id1, id2):
        return id1 ^ id2

    def find_bucket(self, node_id):
        distance = self.xor_distance(self.id, node_id)
        return distance.bit_length() - 1

    def update_routing_table(self, node_id, ip, port):
        bucket_index = self.find_bucket(node_id)
        bucket = self.routing_table[bucket_index]
        if node_id not in [n['id'] for n in bucket]:
            if len(bucket) < self.k:
                bucket.append({'id': node_id, 'ip': ip, 'port': port})
            else:
                bucket.pop(0)
                bucket.append({'id': node_id, 'ip': ip, 'port': port})

    def find_node(self, target_id):
        bucket_index = self.find_bucket(target_id)
        bucket = self.routing_table[bucket_index]
        return sorted(bucket, key=lambda n: self.xor_distance(n['id'], target_id))[:self.alpha]

    def store(self, key, value):
        key_id = self.hash(key)
        self.data[key_id] = value
        closest_nodes = self.find_node(key_id)
        for node in closest_nodes:
            self.send_message(node['ip'], node['port'], 'STORE', key, value)

    def lookup(self, key):
        key_id = self.hash(key)
        if key_id in self.data:
            return self.data[key_id]
        closest_nodes = self.find_node(key_id)
        for node in closest_nodes:
            response = self.send_message(node['ip'], node['port'], 'FIND_VALUE', key)
            if response:
                return response
        return None

    def send_message(self, ip, port, command, key, value=None):
        message = json.dumps({'command': command, 'key': key, 'value': value})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(message.encode())
            response = s.recv(1024).decode()
            return json.loads(response).get('value')

    def handle_message(self, client_socket):
        message = json.loads(client_socket.recv(1024).decode())
        command = message['command']
        key = message['key']
        value = message.get('value')
        if command == 'STORE':
            self.data[self.hash(key)] = value
            response = {'status': 'OK'}
        elif command == 'FIND_VALUE':
            key_id = self.hash(key)
            if key_id in self.data:
                response = {'value': self.data[key_id]}
            else:
                response = {'value': None}
        client_socket.sendall(json.dumps(response).encode())
        client_socket.close()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        print(f"Node {self.id} listening on {self.ip}:{self.port}")

        while True:
            client_socket, client_address = server.accept()
            threading.Thread(target=self.handle_message, args=(client_socket,)).start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python kademlia_node.py <IP> <PORT>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    node = KademliaNode(ip, port)
    node.run()