import time  # Import the time module
import sqlite3  # Import the sqlite3 module
from netmiko import ConnectHandler  # Import ConnectHandler from netmiko
from github import Github  # Import the Github class from the github module

# Connect to SQLite database
conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')  # Connect to the SQLite database
cursor = conn.cursor()  # Create a cursor object to interact with the database

# Fetch all rows from the routers table
cursor.execute("SELECT * FROM routers")  # Execute SQL query to select all rows from the routers table
rows = cursor.fetchall()  # Fetch all rows returned by the query

# Define routers as a list of dictionaries containing router details
routers = []  # Initialize an empty list to store router details
for row in rows:  # Iterate through each row fetched from the database
    router_details = {  # Create a dictionary to store router details
        'device_type': 'cisco_ios',
        'ip': row[2],  # Assuming IP is stored in the third column (index 2)
        'username': row[3],  # Assuming username is stored in the fourth column (index 3)
        'password': row[4]  # Assuming password is stored in the fifth column (index 4)
    }
    routers.append(router_details)  # Append router details to the routers list

# Query database for scheduled backup time
cursor.execute("SELECT backup_time FROM schedule")  # Execute SQL query to select backup_time from schedule table
result = cursor.fetchone()  # Fetch the first row returned by the query

# Extract backup_time if result is not None
backup_time = None  # Initialize backup_time variable to None
if result is not None:  # Check if result is not None
    backup_time = result[0]  # Extract backup_time from the first column of the result

# Close database connection
conn.close()  # Close the SQLite database connection

# Main loop
while True:  # Infinite loop
    # Check current time
    current_time = time.strftime('%H:%M')  # Get current time in HH:MM format
    print(f"Current time: {current_time}")  # Print current time for debugging

    # Print backup time for debugging
    print(f"Backup time: {backup_time}")

    # If it's time for backup and backup_time is not None
    if current_time == backup_time:  # Check if current time matches backup time
        print("Backup time reached. Initiating backup process.")  # Print message indicating backup process initiation

        # Connect to each router and backup configuration
        for router in routers:  # Iterate through each router in the routers list
            try:
                # Connect to router
                ssh_session = ConnectHandler(**router)  # Establish SSH session to the router using Netmiko

                # Backup running configuration
                running_config = ssh_session.send_command('show running-config')  # Send show running-config command to the router

                # Save configuration to file
                filename = f"{router['ip']}.config"  # Define filename based on router's IP address
                with open(filename, 'w') as file:  # Open file in write mode
                    file.write(running_config)  # Write running configuration to the file

                # Upload to GitHub repository
                g = Github('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')  # Create Github object with personal access token
                repo = g.get_repo('AidanBugeja2/CodeRepository')  # Get repository named 'CodeRepository'
                repo.create_file(filename, f"Backup {filename}", running_config)  # Create file in repository with backup content

                print(f"Backup for {router['ip']} completed and uploaded to GitHub.")  # Print success message

                # Close SSH session
                ssh_session.disconnect()  # Disconnect SSH session

            except Exception as e:  # Handle exceptions
                print(f"Failed to backup {router['ip']}: {str(e)}")  # Print error message if backup fails

    else:
        print("Not backup time yet. Waiting...")  # Print message indicating it's not backup time yet

    # Wait for next iteration
    time.sleep(60)  # Sleep for 60 seconds before next iteration

