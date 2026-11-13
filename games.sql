CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    name TEXT,
    console TEXT,
    year INT,
    owner TEXT,
    UNIQUE (name)
);