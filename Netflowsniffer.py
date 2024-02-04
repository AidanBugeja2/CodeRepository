from scapy.all import sniff, IP, UDP  # Imports necessary modules from Scapy
import socket  # Imports the socket module
from datetime import datetime  # Imports the datetime module
import sqlite3  # Imports the sqlite3 module

NetflowHost = socket.gethostname()  # Gets the hostname of the machine
NetflowPort = 2055  # Defines the port number
NetflowSocket = socket.socket()  # Creates a socket object
NetflowSocket.bind((NetflowHost, NetflowPort))  # Binds the socket to the hostname and port
NetflowSocket.listen()  # Begins listening for incoming connections
packet_count = 0  # Initializes packet count to 0

dbsConnection = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')  # Connects to SQLite database
conCursor = dbsConnection.cursor()  # Creates a cursor object to interact with the database

def packet_callback(packet):  # Defines packet callback function
    global packet_count  # Access global variable
    
    if IP in packet:  # Checks if packet has an IP layer
        if UDP in packet:  # Checks if packet has a UDP layer
            
            # Extracts current date and time
            current_time = datetime.now().strftime("&Y-%m-%d %H:%M:%S")
            src_ip = packet[IP].src  # Extracts source IP address
            dst_ip = packet[IP].dst  # Extracts destination IP address
            src_port = packet[UDP].sport  # Extracts source port number
            dst_port = packet[UDP].dport  # Extracts destination port number
            
            protocol = "UDP"  # Defines protocol
            
            # Prints packet details
            print(f"Date/Time: {current_time}")
            print(f"Router IP: {src_ip}")
            print(f"Source IP: {src_ip}")
            print(f"Destination IP: {dst_ip}")
            print(f"Source Port: {src_port}")
            print(f"Destination Port: {dst_port}")
            print(f"Protocol: {protocol}")
            
            packet_count += 1  # Incrementing packet count
            print(f"Number of Packets: {packet_count}")
            print("-" * 30)
            
            # Inserts data into the SQLite database
            conCursor.execute('''
                INSERT INTO netflow_data(date_time, router_ip, num_packets, src_ip, dst_ip, protocol, src_port, dst_port)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ''', (current_time, src_ip, packet_count, src_ip, dst_ip, protocol, src_port, dst_port))
            dbsConnection.commit()  # Commit changes to the database

# Starts sniffing packets
sniff(filter='udp', prn=packet_callback, iface='virbr0')
