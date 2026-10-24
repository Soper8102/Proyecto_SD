from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
database_url = "postgresql+psycopg2://postgres:1234@localhost:5432/uni_ride"
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()