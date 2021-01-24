from keydb import ConnectionPool, KeyDB

pool = ConnectionPool(host='127.0.0.1')
connection = KeyDB(connection_pool=pool)


"""
def transaction(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        success = False

        while not success:
            try:
                connection.execute_command("MULTI")
                f(*args, **kwargs)
                result = connection.execute_command("EXEC")
                success = True
            except Exception as e:
                print(f"Transaction failed: {e}")
                connection.execute_command("DISCARD")
                time.sleep(0.01)

    return wrapper


def db(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        command = f(*args, **kwargs)
        if isinstance(command, str):
            command = [command]

        for c in command:
            connection.execute_command(c)
        return command
    return wrapper
"""