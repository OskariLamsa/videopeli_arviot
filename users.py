import db

def new_user(db_name, params):
    sql = """
    INSERT INTO users (username, password_hash)
    VALUES (?, ?)
    """
    db.execute(db_name, sql, params)

def get_password_hash(db_name, param):
    sql = """
    SELECT password_hash
    FROM users
    WHERE username = ?
    """
    return db.query(db_name, sql, param)