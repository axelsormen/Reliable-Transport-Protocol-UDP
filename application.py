# Importing libraries and functions that are needed for this assignment
import argparse
import socket
import struct 
from datetime import datetime
import time

# Defining the four constants
HEADER_SIZE = 6 # Header size in bytes
MAX_DATA_SIZE = 994 # Max data size in bytes
PACKET_SIZE = HEADER_SIZE + MAX_DATA_SIZE # Total packet size
TIMEOUT_INTERVAL = 0.5 # Timeout interval, 500 milliseconds

# Defining the flag values
SYN_FLAG = 1 << 0 # SYN flag value
ACK_FLAG = 1 << 1 # ACK flag value
FIN_FLAG = 1 << 2 # FIN flag value

'''
Description: The functionn creates a parser, and then adds the different arguments to it. 
Arguments: Server, Client, IP (must be on dotted decimal notation format), Port number (must be int in range [1024, 65535]), File name (must be string), Sliding window size (must be int) and discard packet number (must be int). 
Returns: The parsed command-line arguments in order to execute the server or client
Handling of exceptions: User can get an explanation for each argument from Help. IP, port number, discard packet and window size are validated in seperate functions. If -s or -c not included, they user will be informed via Main. FileNotFoundError is handled in the client function.
'''
def parse_arguments():
    parser = argparse.ArgumentParser(description="File Transfer over UDP using DRTP protocol") # Parses command-line arguments
    parser.add_argument('-s', '--server', action='store_true', help="Enable server mode") # Adds the server argument
    parser.add_argument('-c', '--client', action='store_true', help="Enable client mode") # Adds the client argument
    parser.add_argument('-i', '--ip', type=validate_ip, default='10.0.1.2', required=True, help="IP address. Must be in the dotted decimal notation format. Default = 10.0.1.2") # Adds the IP argument
    parser.add_argument('-p', '--port', type=port_check, default=8088, required=True, help="Port number. Must be an integer and in the range [1024, 65535]. Default = 8088") # Adds the port argument
    parser.add_argument('-f', '--file', type=str, help="JPG file on client side") # Adds the file argument
    parser.add_argument('-w', '--window', type=window_type, default=3, help="Sliding window size. Default = 3") # Adds the sliding window argument
    parser.add_argument('-d', '--discard', type=discard_type, default=float('inf'), help="A custom test case to skip a seq to check for retransmission") # Adds the discard packet argument
    return parser.parse_args() # Returns the parsed command-line arguments

'''
Description: The function creates a packet using struct to pack the header. The header includes a binary string, seq number, ack number and flags. Flags indicate type of packet (SYN, ACK, FIN).
Inputs: seq number, ack number and flags are packed into header. Data is included in the finale packet.
Returns: the created packet (header + data) as a byte string
Handling of exceptions: None
'''
def create_packet(seq, ack_num, flags, data=b''):
    header = struct.pack('!HHH', seq, ack_num, flags) # Packs header with a binary string, seq number, ack number and flags
    return header + data # Returns the created packet (header + data) as a byte string

'''
Description: The function parses a packet using struct to unpack the header. The header includes a binary string, seq number, ack number and flags. Flags indicate type of packet (SYN, ACK, FIN).
Inputs: Packet is divided into header and data. Then parsed. 
Returns: seq number, ack number and flags indicating the type of packet + data included in the packet 
Handling of exceptions: None
'''
def parse_packet(packet):
    header = packet[:HEADER_SIZE] # Header is set to the first 6 bytes
    seq, ack_num, flags = struct.unpack('!HHH', header) # Parses the header
    data = packet[HEADER_SIZE:] # Data is set to the remaining 994 bytes
    return seq, ack_num, flags, data  # Returns seq number, ack number and flags indicating the type of packet + data included in the packet 

'''
Description: The function checks if a specific flag is set in the flags field
Inputs: Flags (flags field) and flag (specific). Checks if the flags field of the packet matches the specific flag
Returns: Boolean indicating if the flag is set
Handling of exceptions: None
'''
def is_flag_set(flags, flag):
    return (flags & flag) != 0 # Returns a boolean indicating if the flag is set

'''
Description: This function takes in an integer and tries to parse it to an integer.
Inputs: Port number, which is used to validate if it is an integer and in the right interval.
Returns: The port number if it is accepted.  
Handling of exceptions: If the port is not an integer or not between 1024 and 65535, an error message will be thrown.
'''
def port_check(portnumber):
    try:
        port = int(portnumber) # Try to parse the input to an integer
    except ValueError:
        print('Please enter an integer') # Print message if parsing fails

    if port<1024 or port > 65535: # The range of the number must be in the interval of 1024 & 65535
        print('Invalid port. It must be within the range [1024,65535]') # Print message if port number not in interval
    else:
        return port # Returns the port number if it is accepted
    
'''
Description: This function takes in a string, splits the string by every dot and adds it to an array.
Inputs: IP address, which is used to validate if it is on the wanted format.
Returns: The IP address if it is accepted.
Handling of exceptions: If the IP is not on the dotted decimal notation (4 dots) and the blocks are integer between 0 and 255, then an error message will be thrown.
'''
def validate_ip(ip):
    blocks = ip.split('.') # Splits the blocks in the IP string
    if len(blocks) != 4: # The string must contain exactly 4 blocks
        print('Invalid IP. It must in this format: 10.1.2.3') #Print message if IP not on dotted format

    for block in blocks:
        try:
            num = int(block) # Tries to parse the input to an integer
            if num < 0 or num > 255: # Each block must be between 0 and 255
                print('Invalid IP. It must in this format: 10.1.2.3') 
        except ValueError:
            print('Invalid IP. It must in this format: 10.1.2.3') # Print message if parsing fails
    return ip # Returns the IP address if it is accepted

'''
Description: This function validates the passed dicard number. 
Inputs: Discard number, which is used to validate if it is a postive integer.
Returns: The discard number if it is accepted.
Handling of exceptions: If the discard number is not a postive integer, then an error message will be thrown.
'''
def discard_type(number):
    try:
        discard_number = int(number) # Tries to parse the discard number to an integer and returns it if successful
        if discard_number < 0: # Discard number must be greater than zero
            raise ValueError("Discard number must be a positive integer")
        return discard_number # Returns the discard number if it is accepted
    except ValueError:
        raise argparse.ArgumentTypeError("Discard number must be a positive integer")

'''
Description: This function validates the passed window size. 
Inputs: Window size, which is used to validate if it is a positive integer.
Returns: The window size if it is accepted.
Handling of exceptions: If the window size is not a positive integer, then an error message will be thrown.
'''  
def window_type(size):
    try:
        window_size = int(size) # Tries to parse the window size to an integer and returns it if successful
        if window_size < 0: # Window size must be greater than zero
            raise ValueError("Window size must be a positive integer")
        return window_size # Returns the window size if it is accepted
    except ValueError:
        raise argparse.ArgumentTypeError("Window size must be a positive integer")

'''
Description: This function runs the server mode with given IP address, port number and discard packet.
Inputs: IP address and port number are used to bind the socket. Discard packet is used to let the client know which packet to discard and retransmit.
Creates: A file with the received data
Handling of exceptions: KeyboardInterrupt = Possible to quit the program will it is still running. If the timeout interval is reached after the SYN is received, an error message will be thrown.
'''  
def run_server(ip, port, discard_seq):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket is created
    sock.settimeout(TIMEOUT_INTERVAL) # Timeout time 
    sock.bind((ip, port)) # Socket is bound to the specified IP address and port number
    print(f"Server started at {ip}:{port}") # Informs the user that the server has started on the specified IP address and port number

    file_data = b'' # Variable to store received file data
    expected_seq = 1 # Variable to store expected sequence number
    start_time = None # Variable to store start time

    try:
        while True:
            try:
                packet, client_address = sock.recvfrom(PACKET_SIZE) # Packet from client is received
                seq, ack_num, flags, data = parse_packet(packet) # Parsing received packet

                if start_time is None:
                    start_time = time.time() # Starts timer when first packet is received

                if is_flag_set(flags, SYN_FLAG):
                    print("SYN packet is received") # Informs the user that the SYN packet is received
                    syn_ack_packet = create_packet(0, 0, SYN_FLAG | ACK_FLAG) # Creates SYN ACK packet
                    sock.sendto(syn_ack_packet, client_address) # Sends SYN ACK packet to client
                    print("SYN-ACK packet is sent") # Informs the user that the SYN ACK packet is sent
                    continue # Continues if SYN is received

                if is_flag_set(flags, ACK_FLAG): 
                    print("ACK packet is received") # Informs the user that the ACK packet is received
                    print("Connection established") # Informs the user that the connection is established
                    continue # Continues if ACK is received

                if is_flag_set(flags, FIN_FLAG):
                    print("\nFIN packet is received") # Informs the user that the FIN packet is received
                    fin_ack_packet = create_packet(0, 0, FIN_FLAG | ACK_FLAG) # Creates FIN ACK packet
                    sock.sendto(fin_ack_packet, client_address) # Sends FIN ACK packet to client
                    print("FIN ACK packet is sent\n") # Informs the user that the FIN ACK packet is received
                    break # Breaks in order to calculate throughput and close connection

                if seq == discard_seq:
                    # Set discard_seq to positive infinity. This ensures that the next time this comparison is made, it won't be true unless discard_seq is set to another value.
                    discard_seq = float('inf') 
                    continue 

                if seq == expected_seq: #Handles out-of_order packets
                    file_data += data # Received file gets the data from the packet (header is excluded) 
                    print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq} is received") # Informs the user that packet x is received
                    ack_packet = create_packet(0, seq, ACK_FLAG) # Creates ACK packet
                    sock.sendto(ack_packet, client_address) # Sends ACK packet to client
                    print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- sending ack for the received {seq}") # Informs the user that ACK packet for x is sent
                    expected_seq += 1 # Increments expected seq
                else:
                    print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- out-of-order packet {seq} is received") # Informs the user that out-of-order packet for x is sent

            except socket.timeout:
                continue # Times out if socket timeout occurs

    except KeyboardInterrupt:
        pass # Handling keyboard interrupt

    finally:
        duration = time.time() - start_time # Calculates the total duration
        throughput = (len(file_data) * 8) / (duration * 1000000) # Calculates the throughput
        print(f"The throughput is {throughput:.2f} Mbps") # Informs the user of the throughput
        print("Connection Closes") # Informs the user that the connection closes

        with open("received_file", "wb") as f:
            f.write(file_data) # Writes received file data to a file

'''
Description: This function runs the client mode with given IP address, port number, file name, and window size
Inputs: IP address and port number are used in the server address. File name is the name of the file that should be sent to the server. Window size is the maximum length of the sliding window.
Returns: Nothing
Handling of exceptions: If the passed file name is not found, an error message will also be thrown. If the timeout interval is reached after the first SYN is sent, an error message will be thrown.
'''  
def run_client(ip, port, file_name, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket
    sock.settimeout(TIMEOUT_INTERVAL) # Timeout time 
    server_address = (ip, port) # Defines the server address

    '''
    Description: This function sends the packet to the server address
    Inputs: Packet, which is sent to the server address
    Returns: Nothing
    Handling of exceptions: None.
    '''  
    def send_packet(packet):
        sock.sendto(packet, server_address) # Sendes packet to server

    try:
        with open(file_name, "rb") as f: # Opens the file
            file_data = f.read() # Reads the file data

        total_packets = (len(file_data) + MAX_DATA_SIZE - 1) // MAX_DATA_SIZE # Calculates total packets
        base = 1 # Defines the base 
        next_seq = 1 # Defines the next sequence number
        window = set() # Defines the sliding window

        '''
        Description: This function retransmitts packets that have not received an ACK. See comments for more details.
        Inputs: None
        Returns: Nothing
        Handling of exceptions: None.
        '''  
        def retransmit_packets():
            for seq in range(base, next_seq-1): # Loops through the packets in the window range
                data = file_data[(seq-1)*MAX_DATA_SIZE:seq*MAX_DATA_SIZE] # Extracts the next data from the file data
                packet = create_packet(seq, 0, 0, data) # Creates retransmit packet with seq number, no ack number, no flags and the file data
                send_packet(packet) # Sends the retransmit packet to the server
                print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- retransmitting packet with seq = {seq}") # Informs the user that the retransmit packet for x is sent

        '''
        Description: This function sends the seq packets to the server. See comments for more details.
        Inputs: None
        Returns: Nothing
        Handling of exceptions: None.
        '''  
        def send_window():
            nonlocal next_seq # Retrieves the nonlocal variable next_seq
            while next_seq <= base + window_size and next_seq <= total_packets: 
                # Loops until all packets in the window are sent or all packets are sent
                    if next_seq-1 < 1: # Skip seq = 0
                        window.add(next_seq)
                        next_seq += 1
                    data = file_data[(next_seq-1)*MAX_DATA_SIZE:next_seq*MAX_DATA_SIZE] # Extracts the next data from the file data
                    packet = create_packet(next_seq-1, 0, 0, data) # Creates packet with the next seq number, no ack number, no flags and the file data
                    send_packet(packet) # Sends packet to the server
                    print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- packet with seq = {next_seq-1} is sent, sliding window = {list(window)}") # Informs the user that seq x is sent
                    window.add(next_seq) # Add the next seq num to the sliding window
                    next_seq += 1 # Increment the next seq num

        print("\nConnection Establishment Phase:") # Informs the user that the Connection Establishment Phase has started
        syn_packet = create_packet(0, 0, SYN_FLAG) # Creates SYN PACKET
        send_packet(syn_packet) # Sends SYN packet to server
        print("\nSYN packet is sent") # Informs the user that the SYN packet is sent

        try:
            packet, _ = sock.recvfrom(PACKET_SIZE) # Sets packet to the received data from the server
            _, _, flags, _ = parse_packet(packet) # Parses the flags of received data

            if is_flag_set(flags, SYN_FLAG | ACK_FLAG): # If SYN-ACK packet is received
                print("SYN-ACK packet is received") # Informs the user that SYN-ACK packet is received
                ack_packet = create_packet(0, 0, ACK_FLAG) # Creates ACK packet
                send_packet(ack_packet) # Sends ACK packet to server
                print("ACK packet is sent") # Informs the user that the ACK packet is sent
                print("Connection established") # Informs the user that the connection is established

        except socket.timeout: # Times out if to the server does not respond
            print("Connection failed") # Informs the user that the connection failed
            sock.close() # Closes socket
            exit() # Exits program

        print("\nData Transfer:\n") # Informs the user that the data transfer has begun
        while base < total_packets: # Continues until all packets have been sent
            start_time = time.time() # Starts the timer
            send_window() # Calls the send_windows function

            while time.time() - start_time < TIMEOUT_INTERVAL: # RTO implementation
                try:
                    packet, _ = sock.recvfrom(PACKET_SIZE) # Sets packet to the received data from the server
                    _, ack_num, flags, _ = parse_packet(packet) # Parses ack numbers and flags of received data

                    if is_flag_set(flags, ACK_FLAG) and ack_num >= base: # ACK is received and is within the base
                        print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- ACK for packet = {ack_num} is received") # Informs the user that ACK packet is received
                        while base <= ack_num: # As long as base is less than or equal to ack_num
                            window.remove(base) # Removes the current base number from the sliding window
                            base += 1 # Increments the base number
                        send_window() # Calls the send_window function

                except socket.timeout:
                    break # If timer exceeds TIMEOUT_INTERVAL then break

            if base < total_packets: # If base is less than total_packets, it means that RTO has occurred
                print(f"{datetime.now().strftime('%H:%M:%S.%f')} -- RTO occured") # Informs the user that RTO occurred
            retransmit_packets() # Call retransmit_packets function

        print("DATA Finished\n\n\n") # Informs the user that data transfer has finished
        print("Connection Teardown:\n") # Informs the user that the connection teardown has begun
        fin_packet = create_packet(0, 0, FIN_FLAG) # Creates FIN packet
        send_packet(fin_packet) # Sends FIN packet to server
        print("FIN packet is sent") # Informs the user that FIN packet is sent

        while True:
            try:
                packet, _ = sock.recvfrom(PACKET_SIZE) # Sets packet to the received data from the server
                _, _, flags, _ = parse_packet(packet) # Parses the flags of received data

                if is_flag_set(flags, FIN_FLAG | ACK_FLAG): # If FIN ACK is received then break
                    print("FIN ACK packet is received") # Informs the user that FIN ACK packet is received
                    print("Connection Closes") # Informs the user that the connection closes
                    break

            except socket.timeout:
                send_packet(fin_packet) # Resends FIN packet if timeout
                print("Resending FIN packet") # Informs the user that the FIN packet was resent

    except FileNotFoundError:
        print(f"File {file_name} not found") # Informs the user that the file was not found
    finally:
        sock.close() # Closes the socket when finished

if __name__ == "__main__":
    args = parse_arguments() # Parses arguments

    if args.server: # Calls the server with IP, port number and discard packet when -s is passed
        run_server(args.ip, args.port, args.discard) 
    elif args.client: # Calls the client with IP, port number and file when -c is passed
        if args.file is None: # If file is not specified, then exit program
            print("Please specify the file to send using -f or --file") # Informs the users that file must be specified
        else:
            run_client(args.ip, args.port, args.file, args.window) 
    else:
        print("Please specify either server mode (-s) or client mode (-c)") # Informs the user that -s or -c must be used
