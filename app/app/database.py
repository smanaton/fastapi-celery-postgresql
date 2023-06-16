from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Sqlite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# PostgresSQL
from sqlalchemy_utils import database_exists, create_database

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:example@postgresserver/db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)

# PostgresSQL

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
