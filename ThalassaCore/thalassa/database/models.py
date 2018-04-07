""" Contains definition of all database models. """
import datetime
import operator

from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

FLEET_AT_THE_PORT = 0
FLEET_ON_THE_SEA = 1

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

    fleets = relationship('Fleet', back_populates='owner')


class Island(Base, ThalassaModel):
    __tablename__ = 'island'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)


class Fleet(Base, ThalassaModel):
    __tablename__ = 'fleet'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    # Current fleet status:
    # 0 - At port
    # 1 - On the sea
    status = Column(Integer, nullable=False)
    # The x & y positions represents the last reached location at the time
    # given in the timestamp
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    position_timestamp = Column(Integer, nullable=False)
    # Port in which the fleet is currently in
    port = Column(Integer, ForeignKey('island.id'), nullable=True)

    owner = relationship('User', back_populates='fleets')
    journeys = relationship('FleetJourney', back_populates='fleet')

    def soonest_journey(self):
        """ Return the journey that is closest in regards to time. """
        return min(self.journeys, key=operator.attrgetter('arrival_time'))

    def set_sea_position(self, x, y):
        self.position_x = x
        self.position_y = y
        self.port = None

    def set_port(self, port):
        self.port = port
        self.position_x = None
        self.position_y = None

class FleetJourney(Base, ThalassaModel):
    __tablename__ = 'fleet_journey'
    id = Column(Integer, primary_key=True)
    fleet_id = Column(Integer,  ForeignKey('fleet.id'))
    # target_port or target_coords(x & y) only one is non null.
    target_port = Column(Integer, nullable=True)
    target_x = Column(Integer, nullable=True)
    target_y = Column(Integer, nullable=True)
    arrival_time = Column(Integer, nullable=False)

    fleet = relationship('Fleet', back_populates='journeys')
