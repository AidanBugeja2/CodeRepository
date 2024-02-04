import sqlite3  # Import the sqlite3 module
import socket  # Import the socket module

class ManageDevices:
    def __init__(self, db_file):
        # Initialize the ManageDevices class with a SQLite database file.
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)  # Connect to the SQLite database
        self.cursor = self.conn.cursor()  # Create a cursor object to interact with the database

    def add_device(self, data):
        try:
            # Insert device information into the Routers table.
            self.cursor.execute("INSERT INTO Routers (name, ip_address, user, password) VALUES (?, ?, ?, ?)", data)
            self.conn.commit()  # Commit changes to the database
            return "Device added successfully."
        except sqlite3.IntegrityError:
            # Handle integrity error if IP address is not unique.
            return "Error: IP address must be unique. Device not added."

    def remove_device(self, ip_address):
        try:
            # Remove a device based on its IP address from the Routers table.
            self.cursor.execute("DELETE FROM Routers WHERE ip_address=?", (ip_address,))
            self.conn.commit()  # Commit changes to the database
            return "Device removed successfully."
        except sqlite3.Error:
            # Handle error if device not found or unable to remove.
            return "Error: Device not found or unable to remove."

    def list_devices(self):
        # Retrieve and return a list of all devices from the Routers table.
        self.cursor.execute("SELECT name, ip_address, user, password FROM Routers")
        devices = self.cursor.fetchall()
        return devices if devices else "No devices found."

    def close_connection(self):
        # Close the SQLite database connection.
        self.conn.close()

def handle_client(conn, manage_devices):
    while True:
        # Receive a request from the client.
        request = conn.recv(1024).decode()
        if not request:
            break

        if request == '1':
            # If the request is to add a device, receive device information and call add_device method.
            data = tuple(conn.recv(1024).decode() for _ in range(4))
            response = manage_devices.add_device(data)
        elif request == '2':
            # If the request is to remove a device, receive the IP address and call remove_device method.
            ip_address = conn.recv(1024).decode()
            response = manage_devices.remove_device(ip_address)
        elif request == '3':
            # If the request is to list devices, call the list_devices method.
            devices = manage_devices.list_devices()
            response = devices

        # Send the response back to the client.
        conn.send(str(response).encode())

if __name__ == "__main__":
    # Set up a server socket and bind it to localhost on port 12345.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen(5)  # Listen for incoming connections

    # Create an instance of the ManageDevices class with a specific database file.
    manage_devices = ManageDevices('/home/nigel/Desktop/AidanBugeja.db')

    print("Server is listening on port 12345...")

    while True:
        # Accept a client connection.
        conn, addr = server.accept()
        print("Connection from", addr)

        # Handle the client in a separate function.
        handle_client(conn, manage_devices)  # Call handle_client function to handle client requests
