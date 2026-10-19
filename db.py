import sqlite3
from flask import g

def get_connection(db_name):
    con = sqlite3.connect(db_name)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(db_name, sql, params=[]):
    con = get_connection(db_name)
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def last_insert_id():
    return g.last_insert_id

def query(db_name, sql, params=[]):
    con = get_connection(db_name)
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def check_if_game_exists(db_name, game_name):
    con = sqlite3.connect(db_name)
    result= con.execute("SELECT * FROM games WHERE name = ?", [game_name]).fetchall()
    print(f"YAAAY{result}")
    con.close()
    if result:
        return True
    return False