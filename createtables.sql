CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE books (
    isbn VARCHAR UNIQUE PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    rev_count INTEGER,
    avg_score DECIMAL, CHECK (avg_score > 0 AND avg_score <= 5)
);

CREATE TABLE review (
    id SERIAL PRIMARY KEY,
    rev_text VARCHAR,
    rev_rate INTEGER NOT NULL, CHECK (rev_rate> 0 AND rev_rate <= 5),
    book_isbn VARCHAR REFERENCES books,
    user_id INTEGER REFERENCES accounts
);
