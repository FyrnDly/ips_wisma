import os
from dotenv import load_dotenv
from mysql.connector import connect, Error

load_dotenv()

def create_server_connection(host_name, user_name, user_password, database_name):
    connection = None
    try:
        connection = connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=database_name,
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection

host = os.getenv("DB_Host", "localhost")
user = os.getenv("DB_User", "root")
password = os.getenv("DB_Password", None)
database = os.getenv("DB_Database", "test")

mydb = create_server_connection(host, user, password, database)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM logs")
myresult = mycursor.fetchall()

for record in myresult:
    print(record)