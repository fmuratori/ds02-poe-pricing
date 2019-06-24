# test postgresql

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# postgreSQL utility functionalities

def exists_database(db_name, username, host, password):
    try:
        conn, cursor = connect_to_database(db_name, username, host, password)
        disconnect_from_database(conn, cursor)
        return True
    except psycopg2.OperationalError:
        return False

def create_database(db_name, username, host, password):
    conn, cursor = connect_to_database('postgres', username, host, password)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    execute_query(conn, cursor, """CREATE DATABASE """ + db_name)
    disconnect_from_database(conn, cursor)

def delete_database(db_name, username, host, password):
    conn, cursor = connect_to_database('postgres', username, host, password)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    execute_query(conn, cursor, """DROP DATABASE """ + db_name)
    disconnect_from_database(conn, cursor)

def connect_to_database(db_name, username, host, password):
    connect_str = "dbname='" + db_name + "' user='" + username + "' host='" + host + "' password='" + password + "'"
    conn = psycopg2.connect(connect_str)
    return conn, conn.cursor()

def disconnect_from_database(conn, cursor):
    cursor.close()
    conn.close()

def execute_query(conn, cursor, query):
    cursor.execute(query)
    conn.commit()

class PoeDatabase:
    def __init__(self):
        self._db_name = 'poe'
        self._user = 'fabio'
        self._password = 'pssword96'
        self._host = 'localhost'

        if not exists_database(self._db_name, self._user, self._host, self._password):
            create_database(self._db_name, self._user, self._host, self._password)

            self.create_database_structure()

        self.conn, self.cursor = connect_to_database()

    def insert_record():
        pass

if __name__ == '__main__':
    # assert if an unexisting database exists

    # assert if an existing database exsists
    
    # assert if an user exists

