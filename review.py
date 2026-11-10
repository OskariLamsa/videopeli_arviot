import db


def updatereview(db_name, params):
    sql = """
            UPDATE reviews
            SET game_name = ?, score = ?, review = ?
            WHERE id = ?
        """
    db.execute(db_name, sql, params)

def newreview(db_name, params):
    sql = """
                INSERT INTO reviews (username, game_name, score, review, thumbs_up, thumbs_down)
                VALUES (?, ?, ?, ?, ?, ?)
            """
    db.execute(db_name, sql, params)

def new_thumb(db_name, params):
    sql = """
    INSERT INTO thumbs (review_id, username, positive)
    VALUES (?, ?, ?)
    ON CONFLICT(review_id, username)
    DO UPDATE SET positive = excluded.positive
    """
    db.execute(db_name, sql, params)

def get_user_reviews(db_name, param):
    sql = """
    SELECT id, game_name, score, review
    FROM reviews
    WHERE username = ?
    ORDER BY id DESC
    """
    return db.query(db_name, sql, param)

def get_user_by_reviewid(db_name, param):
    sql = """
    SELECT username
    FROM reviews
    WHERE id = ?
    """
    return db.query(db_name, sql, param)

def get_review_by_id(db_name, param):
    sql = """
    SELECT id, username, game_name, score, review
    FROM reviews
    WHERE rowid = ?
    """
    return db.query(db_name, sql, param)

def get_thumbs_by_game_name(db_name, params):
    sql = """
        SELECT r.id, r.username, r.score, r.review,
               COALESCE(SUM(t.positive = 1), 0) AS thumbs_up,
               COALESCE(SUM(t.positive = 0), 0) AS thumbs_down,
               (SELECT positive FROM thumbs
                WHERE review_id = r.id AND username = ?) AS my_vote
        FROM reviews r
        LEFT JOIN thumbs t ON t.review_id = r.id
        WHERE r.game_name = ?
        GROUP BY r.id
        ORDER BY r.id DESC
    """
    return db.query(db_name, sql, params)

def get_game_name_by_reviewid(db_name, param):
    sql = """
    SELECT game_name
    FROM reviews
    WHERE id = ?
    """
    return db.query(db_name, sql, param)

def delete_review(db_name, param):
    sql = """
    DELETE
    FROM reviews
    WHERE id = ?
    """
    db.execute(db_name, sql, param)