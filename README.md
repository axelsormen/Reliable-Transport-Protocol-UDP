# DRTP File Transfer Application

## Overview
The DRTP File Transfer Application is a reliable file transfer system over UDP between a server and a client. The application implements a reliable transport protocol (DRTP) with a custom header format. It utilizes a sliding window mechanism to ensure reliable data transfer using Go-Back-N (GBN) protocol.

## Features
- Implements reliable file transfer over UDP using DRTP.
- Supports three-way handshake for connection establishment.
- Utilizes sliding window mechanism for reliable data transfer.
- Handles out-of-order packets and retransmissions.
- Supports graceful connection teardown using FIN-FIN-ACK handshake.

## Usage
### Server
To run the server, use the following command: "python3 application.py -s -i <ip_address_of_the_server> -p <port> -d <discard>"

- `-s`: Specifies that the script should run as a server.
- `-i <ip_address_of_the_server>`: Specifies the IP address of the server.
- `-p <port>`: Specifies the port on which the server will listen for incoming connections.
- `-d <discard>` (Optional): Specifies the sequence number of the packet to discard for testing purposes.

### Client
To run the client, use the following command: "python3 application.py -c -f <file_name> -i <ip_address_of_the_server> -p <server_port> -w <window>"

- `-c`: Specifies that the script should run as a client.
- `-f <file_name>`: Specifies the name of the file to be transferred.
- `-i <ip_address_of_the_server>`: Specifies the IP address of the server.
- `-p <server_port>`: Specifies the port on which the server is listening.
- `-w <window>` (Optional): Specifies the window size for sliding window protocol.

### Example Usage
Server: python3 application.py -s -i 127.0.0.1 -p 8000 -d 8
Client: python3 application.py -c -f Photo.jpg -i 127.0.0.1 -p 8000 -w 5

## Requirements
- A terminal with Python 3 installed
