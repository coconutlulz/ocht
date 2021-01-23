from keydb import ConnectionPool, KeyDB

pool = ConnectionPool(host='127.0.0.1')
db = KeyDB(connection_pool=pool)
