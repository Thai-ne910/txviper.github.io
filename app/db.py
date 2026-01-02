import mysql.connector

def connect_to_db():
    """Kết nối đến cơ sở dữ liệu MySQL"""
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='68686868',
        database='food',
        port=3306
    )

def query_data(query):
    """Truy vấn dữ liệu từ MySQL"""
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results
