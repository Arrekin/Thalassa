""" Contains definition of all database models. """
import datetime

from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ThalassaModel():

    def as_dict(self):
        """ Return Island data as dict. """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base, ThalassaModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(64), nullable=False)
    # User password hashed with bcrypt
    password_hash = Column(CHAR(60), nullable=False)
    email = Column(String(64), nullable=False)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)


class Island(Base, ThalassaModel):
    __tablename__ = 'island'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)


class Fleet(Base, ThalassaModel):
    __tablename__ = 'fleet'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('user.id'))
    state = Column(Integer, nullable=False)
    # The x & y positions represents the last reached location at the time
    # given in timestamp
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    position_timestamp = Column(TIMESTAMP, nullable=False)


class FleetJourney(Base, ThalassaModel):
    __tablename__ = 'fleet_journey'
    id = Column(Integer, primary_key=True)
    fleet = Column(Integer,  ForeignKey('fleet.id'))
    target_x = Column(Integer, nullable=False)
    target_y = Column(Integer, nullable=False)
    arrival_time = Column(TIMESTAMP, nullable=False)
