import sys, os, re, socket
import logging
from hashtable import HashTable
from threading import Thread
from queue import Queue
from logger import Logger

logger = Logger(name='HashTableServiceLogger')

class HashTableService:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ht = HashTable()
        self.request_queue = Queue() #Add a queue to store requests
    
    def handle_commands(self, msg):
        set_ht = re.match('^set ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)$', msg)
        get_ht = re.match('^get ([a-zA-Z0-9]+)$', msg)

        if set_ht:
            key, value = set_ht.groups()
            res = self.ht.set(key=key, value=value)
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

        else:
            output = "Error: Invalid command"
            logger.error(f"Invalid command: {msg}")

        return output
    
    def process_requests(self):
        while True:
            conn, msg = self.request_queue.get() #Get the request from the queue
            try:
                logger.info(f"Processing request: {msg}")
                output = self.handle_commands(msg)
                conn.send(output.encode())
            except Exception as e:
                logger.error(f"Error processing request: {e}")
            finally:
                self.request_queue.task_done() #Mark the request as done
    
    def process_request(self, conn):
        while True:
            try:
                msg = conn.recv(2048).decode()
                if not msg:
                    break
                self.request_queue.put((conn, msg)) #Add the request to the queue
            except Exception as e:
                logger.error(f"Error processing message from client: {e}")
                break
    
    def listen_to_clients(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, int(self.port)))
        sock.listen(5)
        logger.info(f"Listening on  {self.ip}:{self.port}")

        # Start the thread to process requests
        process_requestThread = Thread(target=self.process_requests)
        process_requestThread.daemon = True
        process_requestThread.start()

        while True:
            try:
                client_socket, client_address = sock.accept()
                logger.info(f"Connected to new client at address {client_address}")
                client_handler = Thread(target=self.process_request, args=(client_socket,))
                client_handler.daemon = True
                client_handler.start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                break
    
if __name__ == "__main__":
    ip_address = str(sys.argv[1])
    port = int(sys.argv[2])
    dht = HashTableService(ip=ip_address, port=port)
    dht.listen_to_clients()