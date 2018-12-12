import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    users = db.execute("SELECT id, username, password FROM users").fetchall()
    for i in users:
        print(f"{i.id}, {i.username}, {i.password} username.")

if __name__ == "__main__":
    main()
