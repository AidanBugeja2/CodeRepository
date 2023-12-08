import sqlite3

conn = sqlite3.connect('/home/nigel/Desktop/AidanBugeja.db')
cur = conn.cursor()
data1 = ('1','R1','192.168.1.1','Admin','Password')

cur.execute('''INSERT INTO Routers (ID, Name, IP_Address, User, Password) 
            VALUES (?,?,?,?,?)''', data1)
for row in cur.execute('SELECT * FROM Routers'):
    print(row)
    
conn.commit()
cur.close()
conn.close()