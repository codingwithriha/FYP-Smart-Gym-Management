import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # XAMPP default empty
        database="smart_gym"
    )
    return connection
