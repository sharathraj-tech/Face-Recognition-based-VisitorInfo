import sqlite3

con=sqlite3.connect('uservisit.db')
cur=con.cursor()

print("Database Created Successfully")

cur.execute("DROP TABLE if EXISTS admin")
cur.execute('''CREATE TABLE admin
         (admin_id INT PRIMARY KEY     NOT NULL,
         admin_name           TEXT    NOT NULL,
         admin_uname            TEXT     NOT NULL,
         admin_password       TEXT,
         admin_email         TEXT);''')

print("Table admin Created Successfully")
cur.execute("DROP TABLE if EXISTS user")
cur.execute('''CREATE TABLE user
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_flname TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_mobile TEXT NOT NULL,
                user_address TEXT NOT NULL);''')

print("Table user Created Successfully")

cur.execute("DROP TABLE if EXISTS Notes")
cur.execute('''CREATE TABLE Notes
            (note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL);''')

print("Table Notes Created Successfully")

# insert data to admin table
admin_sql="INSERT INTO admin(admin_name,admin_id,admin_uname,admin_password,admin_email) VALUES(?,?,?,?,?)"
cur.execute(admin_sql,('Sharath Raj',1,'admin','admin','sharathrj143@gmail.com'))
cur.execute(admin_sql,('Jijo Joseph',2,'admin2','admin@2','jijojoseph@gmail.com'))
con.commit()
username='admin123'
password='Admin@123'
cur.execute("SELECT * FROM admin WHERE admin_uname=? AND admin_password=?",(username,password))
for x in cur:
    print(x)
con.close()
