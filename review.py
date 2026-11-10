import db


def updatereview(db_name, params):
    sql = """
            UPDATE reviews
            SET game_name = ?, score = ?, review = ?
            WHERE id = ?
        """
    db.execute("users.db", sql, params)