import sys, os, re, socket
from hashtable import HashTable
from threading import Thread

class HashTableService:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ht = HashTable()
    
    def handle_commands(self, msg):
        set_ht = re.match('^set ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)$', msg)
        get_ht = re.match('^get ([a-zA-Z0-9]+)$', msg)

        if set_ht:
            key, value = set_ht.groups()
            res = self.ht.set(key=key, value=value)
            output = "Inserted"

        elif get_ht:
            key = get_ht.groups()[0]
            output = self.ht.get(key=key)
            if output is None:
                output = "Error: Non existent key"

        else:
            output = "Error: Invalid command"

        return output
    
    def process_request(self, conn):
        while True:
            try:
                msg = conn.recv(2048).decode()
                print(f"Received: {msg}")
                output = self.handle_commands(msg)

                conn.send(output.encode())

            except Exception as e:
                print("Error processing message from client")
                print(e)
    
    def listen_to_clients(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', int(self.port)))
        sock.listen(5)

        while True:
            try:
                client_socket, client_address = sock.accept()
                print(f"Connected to new client at address {client_address}")
                my_thread = Thread(target=self.process_request, args=(client_socket,))
                my_thread.daemon = True
                my_thread.start()

            except:
                print("Error accepting connection...")
    
if __name__ == "__main__":
    ip_address = str(sys.argv[1])
    port = int(sys.argv[2])
    dht = HashTableService(ip=ip_address, port=port)
    dht.listen_to_clients()