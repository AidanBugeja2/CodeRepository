import time
import sqlite3
from netmiko import ConnectHandler
from github import Github

# Connect to SQLite database
conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')
cursor = conn.cursor()

# Fetch all rows from the routers table
cursor.execute("SELECT * FROM routers")
rows = cursor.fetchall()

# Defines routers as a list of dictionaries containing router details
routers = []
for row in rows:
    router_details = {
        'device_type': 'cisco_ios',
        'ip': row[2],  # The IP is stored in the third column (index 2)
        'username': row[3],  # The username is stored in the fourth column (index 3)
        'password': row[4]  # The password is stored in the fifth column (index 4)
    }
    routers.append(router_details)

# Query database for scheduled backup time
cursor.execute("SELECT backup_time FROM schedule")
result = cursor.fetchone()

# Extracts backup_time if result is not None
backup_time = None
if result is not None:
    backup_time = result[0]

# Closes database connection
conn.close()

# Main loop
while True:
    # Checks current time
    current_time = time.strftime('%H:%M')
    print(f"Current time: {current_time}")

    # Prints backup time for debugging
    print(f"Backup time: {backup_time}")
    

    # If it's time for backup and backup_time is not None
    if current_time == backup_time:
        print("Backup time reached. Initiating backup process.")

        # Connect to each router and backup configuration
        for router in routers:
            try:
                # Connects to router
                ssh_session = ConnectHandler(**router)

                # Backup running configuration
                running_config = ssh_session.send_command('show running-config')

                # Saves configuration to file
                filename = f"{router['ip']}.config"
                with open(filename, 'w') as file:
                    file.write(running_config)

                # Uploads to GitHub repository
                g = Github('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')
                repo = g.get_repo('AidanBugeja2/CodeRepository')
                repo.create_file(filename, f"Backup {filename}", running_config)

                print(f"Backup for {router['ip']} completed and uploaded to GitHub.")

                # Closes SSH session
                ssh_session.disconnect()

            except Exception as e:
                print(f"Failed to backup {router['ip']}: {str(e)}")

    else:
        print("Not backup time yet. Waiting...")

    # Waits for next iteration
    time.sleep(60)
