import sys, socket
from threading import Thread
from logger import Logger
import json

logger = Logger(name='ClientLogger')

def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

if len(sys.argv) != 3:
    logger.error("Correct usage: script, IP address, port number")
    exit()

coordinator_ip_address = str(sys.argv[1])
coordinator_port = int(sys.argv[2])
coordinator = get_socket()
coordinator.connect((coordinator_ip_address, coordinator_port))

def listen_for_messages():
    while True:
        output = coordinator.recv(2048).decode()
        if output:
            logger.info(output)

t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

while True:
    commands = []
    print("Enter commands (type 'done' to finish):")
    while True:
        command = input()
        if command.lower() == 'done':
            break
        commands.append(command)
    
    json_data = json.dumps(commands)
    coordinator.send(json_data.encode())