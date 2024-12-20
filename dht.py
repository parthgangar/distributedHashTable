import sys, re, socket, time
from hashtable import HashTable
from threading import Thread
from queue import Queue
from logger import Logger
import json

logger = Logger(name='DHTLogger')

class DHT:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.ht = HashTable(capacity=10, disk_path="cache_disk")
        self.request_queue = Queue()

    def handle_command(self, command: str) -> str:
        set_ht = re.match('^set ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)$', command)
        get_ht = re.match('^get ([a-zA-Z0-9]+)$', command)
        stats_ht = re.match('^stats$', command)

        start_time = time.time()
        if set_ht:
            key, value = set_ht.groups()
            self.ht.set(key=key, value=value)
            output = "Inserted"
            logger.info(f"Inserted key: {key} value: {value}")

        elif get_ht:
            key = get_ht.groups()[0]
            output = self.ht.get(key=key)
            if output is None:
                output = "Error: Non existent key"
                logger.warning(f"Key {key} does not exist")
            else:
                logger.info(f"Retrieved value: {output}")
        elif stats_ht:
            output = self.get_performance_statistics()
            logger.info("Performance statistics requested")

        else:
            output = "Error: Invalid command"
            logger.error(f"Invalid command: {command}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for command '{command}': {elapsed_time:.6f} seconds")
        return output
    
    def get_performance_statistics(self) -> str:
        stats = self.ht.cache.stats.get_statistics()
        return json.dumps(stats, indent=4)

    def handle_commands(self, commands: list) -> list:
        results = []
        for command in commands:
            result = self.handle_command(command)
            results.append(result)
        return results
    
    def process_requests_from_queue(self) -> None:
        while True:
            conn, msg = self.request_queue.get() #Get the request from the queue
            try:
                logger.info(f"Processing request: {msg}")
                commands = json.loads(msg)
                results = self.handle_commands(commands)
                response = json.dumps(results)
                conn.send(response.encode())
            except Exception as e:
                logger.error(f"Error processing request: {e}")
            finally:
                self.request_queue.task_done() #Mark the request as done
    
    def client_handler(self, conn: socket.socket) -> None:
        while True:
            try:
                msg = conn.recv(2048).decode()
                if not msg:
                    break
                self.request_queue.put((conn, msg)) #Add the request to the queue
            except Exception as e:
                logger.error(f"Error processing message from client: {e}")
                break
    
    def listen_to_clients(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, int(self.port)))
        sock.listen(5)
        logger.info(f"Listening on  {self.ip}:{self.port}")

        # Start the thread to process requests
        process_requestThread = Thread(target=self.process_requests_from_queue)
        process_requestThread.daemon = True
        process_requestThread.start()

        while True:
            try:
                client_socket, client_address = sock.accept()
                logger.info(f"Connected to new client at address {client_address}")
                client_handlerThread = Thread(target=self.client_handler, args=(client_socket,))
                client_handlerThread.daemon = True
                client_handlerThread.start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                break
    
if __name__ == "__main__":
    ip_address = str(sys.argv[1])
    port = int(sys.argv[2])
    dht = DHT(ip=ip_address, port=port)
    dht.listen_to_clients()