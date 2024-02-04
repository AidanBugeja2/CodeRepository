from scapy.all import IP, SNMP, UDP, sniff
import sqlite3
import time
import os

# Function to save SYSLOG trap data to the database
def save_syslog_data(date, time, router_ip, message):
    """
    Save SYSLOG trap data to the database.

    Args:
        date (str): Date of the trap.
        time (str): Time of the trap.
        router_ip (str): IP address of the router.
        message (str): Message of the trap.
    """
    conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS SyslogTraps
                      (Date TEXT, Time TEXT, Router_IP TEXT, Message TEXT)''')
    cursor.execute("INSERT INTO SyslogTraps (Date, Time, Router_IP, Message) VALUES (?, ?, ?, ?)",
                   (date, time, router_ip, message))
    conn.commit()
    conn.close()

# Function to save LINK UP/DOWN trap data to the database
def save_link_data(date, time, router_ip, interface_name, state):
    """
    Save LINK UP/DOWN trap data to the database.

    Args:
        date (str): Date of the trap.
        time (str): Time of the trap.
        router_ip (str): IP address of the router.
        interface_name (str): Name of the interface.
        state (str): State of the interface (UP/DOWN).
    """
    conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS LinkTraps
                      (Date TEXT, Time TEXT, Router_IP TEXT, Interface_Name TEXT, State TEXT)''')
    cursor.execute("INSERT INTO LinkTraps (Date, Time, Router_IP, Interface_Name, State) VALUES (?, ?, ?, ?, ?)",
                   (date, time, router_ip, interface_name, state))
    conn.commit()
    conn.close()

# Define a function to handle incoming SNMP trap packets
def handle_snmp_packet(packet):
    """
    Handle incoming SNMP trap packets.

    Args:
        packet: Packet containing SNMP trap data.
    """
    current_date = time.strftime('%Y-%m-%d')
    current_time = time.strftime('%H:%M:%S')
    
    if UDP in packet and SNMP in packet:
        if packet[SNMP].version == 1:  # Adjust version as needed
            trap_type = packet[SNMP].PDU.type
            if trap_type == 6:  # LINK UP trap
                save_link_data(current_date, current_time, packet[IP].src, "Interface Name", "UP")
            elif trap_type == 7:  # LINK DOWN trap
                save_link_data(current_date, current_time, packet[IP].src, "Interface Name", "DOWN")
        elif packet[SNMP].version == 2:  # Adjust version as needed
            var_binds = packet[SNMP].PDU.varbindlist
            for var_bind in var_binds:
                if var_bind.oid == '1.3.6.1.6.3.1.1.5.1':  # SYSLOG trap
                    save_syslog_data(current_date, current_time, packet[IP].src, var_bind.value)

# Start sniffing SNMP packets on port 161
print("Starting SNMP trap capture...")
sniff(filter="udp and port 161", prn=handle_snmp_packet, store=0)
