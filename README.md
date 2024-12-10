# Implementing DHT using LRU Cache

This project implements a Distributed Hash Table (DHT) with an LRU (Least Recently Used) cache. The system is designed to handle multiple clients communicating with a coordinator node, which then distributes keys to multiple servers. The servers use an LRU cache to store key-value pairs and maintain performance statistics.

> This module provides a prototype implementation of the DHT functionality.
>
> **Note:**
> - This prototype has been tested on a single local machine with basic-level testing. It is not intended for production use or industry-level testing.

## Prerequisites

- Python 3.x
- Required Python packages (install using `pip`):
    - `socket`
    - `threading`
    - `hashlib`
    - `json`
    - `sys`

## Project Structure

- `client.py`: Client implementation to send commands to the coordinator node.
- `coordinator_node.py`: Coordinator node implementation to distribute keys to servers.
- `dht.py`: Server implementation to handle key-value storage with LRU cache.
- `kademlia.py`: Kademlia DHT implementation (yet to integrate it thoroughly).
- `logger.py`: Logger utility for logging messages.
- `performance_statistics.py`: Performance statistics collection and reporting.
- `lruCache.py`: LRU cache implementation.
- `hashtable.py`: Hash table implementation using LRU cache.

## Running the Project

### Step 1: Start the Server Nodes

1. Open multiple terminals (one for each server) and navigate to the project directory.
2. Run the following command to start the server node:
     ```bash
     python dht.py <SERVER_IP> <SERVER_PORT>
     ```
     Replace `<SERVER_IP>` and `<SERVER_PORT>` with the desired IP address and port number.

### Step 2: Start the Coordinator Node

1. Open a terminal and navigate to the project directory.
2. Run the following command to start the coordinator node:
     ```bash
     python coordinator_node.py <COORDINATOR_IP> <COORDINATOR_PORT> <LIST OF SERVER_IP & SERVER_PORT>
     ```
     Replace `<COORDINATOR_IP>` and `<COORDINATOR_PORT>` with the desired IP address and port number.
     Replace `<LIST OF SERVER_IP & SERVER_PORT>` with a space-separated list of server IP addresses and port numbers.

### Step 3: Start the Clients

1. Open multiple terminals (one for each client) and navigate to the project directory.
2. Run the following command to start a client:
     ```bash
     python client.py <COORDINATOR_IP> <COORDINATOR_PORT>
     ```
     Replace `<COORDINATOR_IP>` and `<COORDINATOR_PORT>` with the desired IP address and port number.

### Step 4: Interact with the System

In the client terminal, enter commands to interact with the system. For example:

- Set a key-value pair:
    ```bash
    set <KEY> <VALUE>
    ```
    Replace `<KEY>` and `<VALUE>` with the desired key and value.

- Get the value for a key:
    ```bash
    get <KEY>
    ```
    Replace `<KEY>` with the desired key.

- Retrieve performance statistics:
    ```bash
    stats
    ```

> **Note:**
> - The `stats` command is currently not working. This issue is yet to be fixed.


### Example Usage

1. Start a server node:
    ```bash
    python dht.py 127.0.0.1 5000
    python dht.py 127.0.0.1 5001
    ```

2. Start the coordinator node:
    ```bash
    python coordinator_node.py 127.0.0.1 4000
    ``` 

3. Start multiple clients:
    ```bash
    python client.py 127.0.0.1 4000
    python client.py 127.0.0.1 4000
    ```

