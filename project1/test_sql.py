import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# SQL to get a user from the users table
username = "davidvann"
user = db.execute(
    'SELECT username FROM users WHERE username = :username', {"username":username}
    ).fetchone()
print(user.username)