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