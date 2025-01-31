# backend/db.py
import pymysql


db_config = {
    "host": "localhost",
    "user": 'root',
    "db_port": "8889",
    "password": 'root',
    "database": 'MASTERARTICLE',
}



def connect_to_db():
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=int(db_config['db_port']),
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
        )
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {e}")