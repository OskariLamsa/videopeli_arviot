CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    username TEXT,
    game_name TEXT,
    score INT,
    review TEXT
);

CREATE TABLE thumbs (
    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    positive INTEGER NOT NULL CHECK (positive IN (0, 1)),
    PRIMARY KEY (review_id, username)
)