""" Contains definition of all database models. """
import datetime

from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String
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


class Island(Base):
    __tablename__ = 'island'
    id = Column(String(32), primary_key=True)
    name = Column(String(32), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    def as_dict(self):
       """ Return Island data as dict. """
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
