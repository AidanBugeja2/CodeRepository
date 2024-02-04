import sys  # Import the sys module for system-specific parameters and functions
import socket  # Import the socket module for low-level networking interface
import sqlite3  # Import the sqlite3 module for SQLite database operations
import time  # Import the time module for time-related functions
from github import Github  # Import the Github class from the github module
from Scripts.ManageDevices import ManageDevices  # Import the ManageDevices class from Scripts.ManageDevices module
import matplotlib.pyplot as plt  # Import the pyplot module from matplotlib for plotting
import difflib  # Import the difflib module for comparing sequences
from paramiko import SSHClient, AutoAddPolicy  # Import SSHClient and AutoAddPolicy classes from paramiko module
from netmiko import ConnectHandler  # Import ConnectHandler class from netmiko module
from elasticsearch import Elasticsearch  # Import Elasticsearch class from elasticsearch module
from elasticsearch.helpers import bulk  # Import bulk function from elasticsearch.helpers module

# Update these variables with your actual information
db_file = '/home/nigel/Desktop/AidanBugeja.db'  # Path to SQLite database file
github_token = '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'  # GitHub token for authentication
github_repo = 'AidanBugeja2/CodeRepository'  # GitHub repository name

elastic_cloud_id = "e8df6c2da90b436196ccc2faf7e80e11:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQyYTAyNDUyMGQ4NTI0NzFiOTM2ODFiMjc4N2M3MzgxNiQxY2MxYmJiMjk5N2E0M2M1YTkzMDc3MDAzYTIzY2U2Yg=="  # Elastic Cloud ID
elastic_username = "elastic"  # Elastic Cloud username
elastic_password = "8V6ma3ca!"  # Elastic Cloud password

es = Elasticsearch(  # Create Elasticsearch instance
    cloud_id=elastic_cloud_id,
    basic_auth=(elastic_username, elastic_password)
)

def main():
    manage_devices = ManageDevices(db_file)  # Initialize ManageDevices instance with database file path

    while True:
        print("\nMain Menu:")
        print("a. Add Router")
        print("b. Delete Router")
        print("c. List Router")
        print("d. Set Backup Time")
        print("e. Set Router Netflow Settings")
        print("f. Remove Router Netflow Settings")
        print("g. Set Router SNMP Settings")
        print("h. Remove Router SNMP Settings")
        print("i. Show Router Config")
        print("j. Show Changes in Router Config")
        print("k. Display Router Netflow Statistics")
        print("l. Show Router Syslog")
        print("q. Quit")

        choice = input("Enter your choice: ").lower()

        if choice == 'a':
            add_router(manage_devices) #Call function add a row in the routers table in the database
        elif choice == 'b':
            delete_router(manage_devices) #Call function remove a row in the routers table in the database
        elif choice == 'c':
            list_router(manage_devices)  #Call function list the routers table in the database
        elif choice == 'd':
            set_backup_time()  #Call function to set backup time in the database
        elif choice == 'e':
            set_netflow_settings()  # Call function to set Netflow settings
        elif choice == 'f':
            remove_netflow_settings() # Call function to remove Netflow settings
        elif choice == 'g':
            set_snmp_settings()  # Call function to set SNMP settings
        elif choice == 'h':
            remove_snmp_settings()  # Call function to remove SNMP settings
        elif choice == 'i':
            ip_address = input("Enter the IP address of the router: ")
            show_router_config(ip_address)  
        elif choice == 'j':
            ip_address = input("Enter the IP address of the router to show changes: ")
            show_changes_in_router_config(ip_address)  # Pass IP address as argument
        elif choice == 'k':
            display_netflow_statistics()
        elif choice == 'l':
            # Option to filter router logs
            ip_address = input("Enter the IP address of the router to filter logs: ")
            filter_router_logs(ip_address)  # Call filter_router_logs function with the specified IP address
            export_syslog_to_elastic()
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please try again.")

    manage_devices.close_connection()

def add_router(manage_devices):
    # Get user input
    name = input("Enter router name: ")
    ip_address = input("Enter router IP address: ")
    user = input("Enter router username: ")
    password = input("Enter router password: ")

    # Call add_device method
    response = manage_devices.add_device((name, ip_address, user, password))

    # Display the response
    print(response)

def delete_router(manage_devices):
    # Get user input
    ip_address = input("Enter the IP address of the router to delete: ")

    # Call remove_device method
    response = manage_devices.remove_device(ip_address)

    # Display the response
    print(response)

def list_router(manage_devices):
    # Retrieve and print a list of all devices from the Routers table.
    devices = manage_devices.list_devices()
    if devices:
        for device in devices:
            print(device)
    else:
        print("No devices found.")

def set_backup_time():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Get user input
    backup_time = input("Enter the backup time in HH:MM format: ")
    
    # Update the backup time in the schedule table
    cursor.execute('UPDATE schedule SET backup_time = ?', (backup_time,))
    
    # Commit the changes to the database
    conn.commit()
    
    # Close the database connection
    conn.close()
    
    print("Backup time has been set to", backup_time)

# Function to set Netflow settings on a router
def set_netflow_settings():
    # Get user input for router details
    ip_address = input("Enter the router's IP address: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Define router parameters
    router = {
        'device_type': 'cisco_ios',
        'ip': ip_address,
        'username': username,
        'password': password,
    }

    try:
        # Connect to the router
        net_connect = ConnectHandler(**router)
        print("Connected to the router.")

        # Enter configuration mode
        net_connect.config_mode()

        # Set Netflow settings (replace commands with actual ones)
        commands = [
            'ip flow-export source GigabitEthernet0/1',  # Example command to set source interface
            'ip flow-export version 9',
            'ip flow-export destination 192.168.122.1 2055'
            'ip flow-cache timeout active 1',
            # Add more commands to set other Netflow settings as needed
        ]
        output = net_connect.send_config_set(commands)
        print("Netflow settings configured.")

        # Exit configuration mode
        net_connect.exit_config_mode()

        # Close SSH connection
        net_connect.disconnect()
        print("Disconnected from the router.")

    except Exception as e:
        print(f"An error occurred: {str(e)}") 
    
def remove_netflow_settings():
    # Get user input for router details
    ip_address = input("Enter the router's IP address: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Define router parameters
    router = {
        'device_type': 'cisco_ios',
        'ip': ip_address,
        'username': username,
        'password': password,
    }

    try:
        # Connect to the router
        net_connect = ConnectHandler(**router)
        print("Connected to the router.")

        # Enter configuration mode
        net_connect.config_mode()

        # Remove Netflow settings (replace commands with actual ones)
        commands = [
            'no ip flow-cache timeout active 1'
            'no ip flow-export source FastEthernet0/1',
            'no ip flow-export version 9',
            'no ip flow-export destination 192.168.122.1 2055',
            'interface FastEthernet0/1',
            'no ip flow egress',
            'write memory',
        ]
        output = net_connect.send_config_set(commands)
        print("Netflow settings removed.")

        # Exit configuration mode
        net_connect.exit_config_mode()

        # Close SSH connection
        net_connect.disconnect()
        print("Disconnected from the router.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Function to set SNMP settings on a router
def set_snmp_settings():
    # Get user input for router details
    ip_address = input("Enter the router's IP address: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    snmp_community = input("Enter SNMP community string: ")
    snmp_trap_receiver = input("Enter SNMP trap receiver IP address: ")

    # Define router parameters
    router = {
        'device_type': 'cisco_ios',
        'ip': ip_address,
        'username': username,
        'password': password,
    }

    try:
        # Connect to the router
        net_connect = ConnectHandler(**router)
        print("Connected to the router.")

        # Enter configuration mode
        net_connect.config_mode()

        # Set SNMP settings (replace commands with actual ones)
        commands = [
            f'snmp-server community {snmp_community} RO',
            f'snmp-server host {snmp_trap_receiver} traps version 2c {snmp_community}',
            # Add more commands to set other SNMP settings as needed
        ]
        output = net_connect.send_config_set(commands)
        print("SNMP settings configured.")

        # Exit configuration mode
        net_connect.exit_config_mode()

        # Close SSH connection
        net_connect.disconnect()
        print("Disconnected from the router.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Function to remove SNMP settings from a router
def remove_snmp_settings():
    # Get user input for router details
    ip_address = input("Enter the router's IP address: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    snmp_community = input("Enter SNMP community string: ")
    snmp_trap_receiver = input("Enter SNMP trap receiver IP address: ")

    # Define router parameters
    router = {
        'device_type': 'cisco_ios',
        'ip': ip_address,
        'username': username,
        'password': password,
    }

    try:
        # Connect to the router
        net_connect = ConnectHandler(**router)
        print("Connected to the router.")

        # Enter configuration mode
        net_connect.config_mode()

        # Remove SNMP settings (replace commands with actual ones)
        commands = [
            f'logging history debugging',
            f'no snmp-server community {snmp_community}',
            f'no snmp-server ifindex persist',
            f'no snmp-server enable traps snmp linkdown linkup',
            f'no snmp-server enable traps syslog '
            f'no snmp-server host {snmp_trap_receiver} traps version 2c {snmp_community}',
            f'write memory',
        ]
        output = net_connect.send_config_set(commands)
        print("SNMP settings removed.")

        # Exit configuration mode
        net_connect.exit_config_mode()

        # Close SSH connection
        net_connect.disconnect()
        print("Disconnected from the router.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def show_router_config(ip_address):
    # Fetch router config from GitHub based on the IP address
    github_client = Github(github_token)
    repo = github_client.get_repo(github_repo)
    file_path = f'{ip_address}.config'  # Assuming file name is the IP address with ".config" extension
    try:
        file_content = repo.get_contents(file_path)
        router_config = file_content.decoded_content.decode('utf-8')
        print(f"Router Configuration for {ip_address}:\n{router_config}")  # Print the router configuration
    except Exception as e:
        print(f"Error fetching router config for {ip_address}: {e}")
        return None  # Return None if there's an error

def show_changes_in_router_config(ip_address):
    # Prompt user for router's IP address
    ip_address = input("Enter the IP address of the router: ")
    
    # Retrieve the current router config from the device
    current_config = retrieve_current_config(ip_address)
    if not current_config:
        print(f"Unable to retrieve current config for router {ip_address}.")
        return

    # Retrieve the backed-up router config from GitHub
    backup_config = retrieve_backup_config(ip_address)
    if not backup_config:
        print(f"Unable to retrieve backup config for router {ip_address}.")
        return

    # Calculate differences using difflib
    diff = difflib.unified_diff(backup_config.splitlines(), current_config.splitlines(), lineterm='')

    # Display differences
    print(f"Differences in Router Config for {ip_address}:")
    print('\n'.join(diff))

def retrieve_current_config(ip_address):
    try:
        # Define router parameters
        router = {
            'device_type': 'cisco_ios',
            'ip': ip_address,
            'username': 'cisco',
            'password': 'cisco'
        }

        # Connect to the router
        net_connect = ConnectHandler(**router)
        print("Connected to the router.")

        # Send command to retrieve router configuration
        current_router_config = net_connect.send_command("show running-config")

        # Close the SSH connection
        net_connect.disconnect()
        print("Disconnected from the router.")

        return current_router_config

    except Exception as e:
        print(f"Error fetching current router config: {e}")
        return None

def retrieve_backup_config(ip_address):
    try:
        # Fetch router config from GitHub based on the IP address
        github_client = Github(github_token)
        repo = github_client.get_repo(github_repo)
        file_path = f'{ip_address}.config'  # Assuming file name is the IP address with ".config" extension
        file_content = repo.get_contents(file_path)
        return file_content.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"Error fetching backup router config for {ip_address}: {e}")
        return None

def display_netflow_statistics():
    ip_address = input("Enter the IP address of the router to display Netflow statistics: ")

    # Fetch data from the database for the specified router
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT protocol, COUNT(*) as packet_count
        FROM netflow_data
        WHERE router_ip = ?
        GROUP BY protocol
    ''', (ip_address,))
    protocol_data = cursor.fetchall()

    conn.close()

    if not protocol_data:
        print("No data found for the specified router.")
        return

    # Calculate the percentage of packets per protocol
    total_packets = sum(packet_count for _, packet_count in protocol_data)
    percentages = [(protocol, packet_count / total_packets * 100) for protocol, packet_count in protocol_data]

    # Create a pie chart using Matplotlib
    protocols = [protocol for protocol, _ in percentages]
    percentage_values = [percentage for _, percentage in percentages]

    plt.figure(figsize=(8, 6))
    plt.pie(percentage_values, labels=protocols, autopct='%1.1f%%', startangle=140)
    plt.title(f'Packet Distribution for Router {ip_address}')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

def export_syslog_to_elastic():
    # Connect to the syslog database
    conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')
    cursor = conn.cursor()

    # Fetch syslog data
    cursor.execute("SELECT * FROM SyslogTraps WHERE router_ip=?", ("router_ip_to_filter",))
    syslog_data = cursor.fetchall()

    # Define index name in Elastic Cloud
    index_name = "syslog_index"

    # Prepare data for bulk indexing
    actions = [
        {
            "_index": index_name,
            "_source": {
                "timestamp": row[0],  # The timestamp is the first column
                "message": row[1],    # The message is the second column
            }
        }
        for row in syslog_data
    ]

    # Bulk index data into Elasticsearch
    success, failed = bulk(es, actions)

    # Print success and failure information
    print(f"Successfully indexed {success} documents.")
    print(f"Failed to index {failed} documents.")

    # Close the database connection
    conn.close()

def filter_router_logs(router_ip):
    # Define index name in Elastic Cloud
    index_name = "syslog_index"

    # Search for logs of a specific router
    search_query = {
        "query": {
            "match": {
                "router_ip": router_ip
            }
        }
    }

    # Perform search
    search_results = es.search(index=index_name, body=search_query)

    # Display search results
    for hit in search_results['hits']['hits']:
        print(f"Timestamp: {hit['_source']['timestamp']}, Message: {hit['_source']['message']}")

main()  # Call the main function to start the program
