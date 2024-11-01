import json
from mysql.connector import connect, Error

def connect_db(host_name, user_name, user_password, database_name):
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

def execute_query(connection, query):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print("Query successful")
    except Error as e:
        print(f"Error: '{e}'")


def read_query(connection, query):
    result = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
        return result
    except Error as e:
        print(f"Error: '{e}'")
        
def get_room_id(mydb, room_id):
    query = f"""SELECT dv.name as name, dr.x as x, dr.y as y, log.data as data
                FROM rooms as rm
                LEFT JOIN data_rooms as dr ON dr.room_id = rm.id
                LEFT JOIN devices as dv ON dr.mac_address = dv.mac_address
                LEFT JOIN (SELECT log.data_room_id, log.data, log.created_at 
                           FROM logs as log 
                           WHERE (log.data_room_id, log.created_at) IN 
                                 (SELECT data_room_id, MAX(created_at) 
                                  FROM logs 
                                  GROUP BY data_room_id)) as log ON log.data_room_id = dr.id
                WHERE rm.id = {room_id}"""
    data_raw = read_query(mydb, query)
    data, labels = {}, []
    for item in data_raw:
        log_data = json.loads(item[3]) if item[3] else []
        data[item[0]] = {
            "pos": (item[1], item[2]),
            "logs": log_data
        }
        labels.append(item[0])
    return data, labels