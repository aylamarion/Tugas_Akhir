import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()
url_object = URL.create(
    "mysql+pymysql",
    username="root",  # os.getenv("DB_USERNAME"),
    password="adMin93@3",  # os.getenv("DB_PASSWORD"),
    host="localhost",  # os.getenv("DB_HOST"),
    database="data_jantung",  # os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT"),
)
engine = create_engine(url_object)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models

    Base.metadata.create_all(bind=engine)
