CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL,
    user_id INTEGER REFERENCES users,
    book_id INTEGER REFERENCES books
);