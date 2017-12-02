""" Script for creating base database. """
import datetime

from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(64), nullable=False)
    # User password hashed with bcrypt
    password_hash = Column(CHAR(60), nullable=False)
    email = Column(String(64), nullable=False)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')

Base.metadata.create_all(engine)