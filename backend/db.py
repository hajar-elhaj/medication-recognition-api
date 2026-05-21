import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="BrrBrrpatapim22",
        database="medicines_db"
    )