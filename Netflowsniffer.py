from scapy.all import sniff, IP, UDP  # Import necessary modules from Scapy
import socket  # Import the socket module
from datetime import datetime  # Import the datetime module
import sqlite3  # Import the sqlite3 module

NetflowHost = socket.gethostname()  # Get the hostname of the machine
NetflowPort = 2055  # Define the port number
NetflowSocket = socket.socket()  # Create a socket object
NetflowSocket.bind((NetflowHost, NetflowPort))  # Bind the socket to the hostname and port
NetflowSocket.listen()  # Begin listening for incoming connections
packet_count = 0  # Initialize packet count to 0

dbsConnection = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')  # Connect to SQLite database
conCursor = dbsConnection.cursor()  # Create a cursor object to interact with the database

def packet_callback(packet):  # Define packet callback function
    global packet_count  # Access global variable
    
    if IP in packet:  # Check if packet has an IP layer
        if UDP in packet:  # Check if packet has a UDP layer
            
            # Extract current date and time
            current_time = datetime.now().strftime("&Y-%m-%d %H:%M:%S")
            src_ip = packet[IP].src  # Extract source IP address
            dst_ip = packet[IP].dst  # Extract destination IP address
            src_port = packet[UDP].sport  # Extract source port number
            dst_port = packet[UDP].dport  # Extract destination port number
            
            protocol = "UDP"  # Define protocol
            
            # Print packet details
            print(f"Date/Time: {current_time}")
            print(f"Router IP: {src_ip}")
            print(f"Source IP: {src_ip}")
            print(f"Destination IP: {dst_ip}")
            print(f"Source Port: {src_port}")
            print(f"Destination Port: {dst_port}")
            print(f"Protocol: {protocol}")
            
            packet_count += 1  # Increment packet count
            print(f"Number of Packets: {packet_count}")
            print("-" * 30)
            
            # Insert data into the SQLite database
            conCursor.execute('''
                INSERT INTO netflow_data(date_time, router_ip, num_packets, src_ip, dst_ip, protocol, src_port, dst_port)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ''', (current_time, src_ip, packet_count, src_ip, dst_ip, protocol, src_port, dst_port))
            dbsConnection.commit()  # Commit changes to the database

# Start sniffing packets
sniff(filter='udp', prn=packet_callback, iface='virbr0')
