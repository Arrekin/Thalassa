""" Contains definition of all database models. """
import datetime
import operator
import random
import time

from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

FLEET_AT_THE_PORT = 0
FLEET_ON_THE_SEA = 1

USER_EXTERNAL = 0
USER_AI = 1

Base = declarative_base()

class ThalassaModel:

    def as_dict(self):
        """ Return Island data as dict. """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ResourceStorage:

    def transfer_resources(self, recipient, *,
                           wood=0,
                           wheat=0,
                           wine=0):
        """ Transfer resources to recipient.

        Args:
            recipient(ResourceStorage): Other object that can store resources.
            other arguements(int): Number of resources to transfer. """
        self.wood -= wood
        recipient.wood += wood
        self.wheat -= wheat
        recipient.wheat += wheat
        self.wine -= wine
        recipient.wine += wine


class User(Base, ThalassaModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(64), nullable=False)
    # Type of the account:
    # USER_EXTERNAL - fe. regular players
    # ISER_AI - internal bots
    type = Column(Integer, nullable=False)
    # User password hashed with bcrypt
    password_hash = Column(CHAR(60), nullable=False)
    email = Column(String(64), nullable=False)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)

    fleets = relationship('Fleet', back_populates='owner')


class Island(Base, ThalassaModel, ResourceStorage):
    __tablename__ = 'island'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    # Resources
    wood = Column(Integer, nullable=False, default=0)
    wheat = Column(Integer, nullable=False, default=0)
    wine = Column(Integer, nullable=False, default=0)

    fleets = relationship('Fleet', back_populates='port')


class Fleet(Base, ThalassaModel, ResourceStorage):
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
    port_id = Column(Integer, ForeignKey('island.id'), nullable=True)

    # Resources
    wood = Column(Integer, nullable=False, default=0)
    wheat = Column(Integer, nullable=False, default=0)
    wine = Column(Integer, nullable=False, default=0)

    owner = relationship('User', back_populates='fleets')
    journeys = relationship('FleetJourney', back_populates='fleet')
    port = relationship('Island', back_populates='fleets')

    def soonest_journey(self):
        """ Return the journey that is closest in regards to time. """
        return min(self.journeys, key=operator.attrgetter('arrival_time'))

    def add_journey(self, *, target_x=None, target_y=None, target_port=None):
        """ Create new journey and start it if there is no any other ongoing journey.
        target coords and target port are mutually exclusive.
        
        Args:
            target_x(int): destination position on x-axis.
            target_y(int): destination position on y-axis.
            target_port(int): id of target port."""
        if target_x is None and target_y is None and target_port is None:
            raise ValueError("Provided arguments are invalid.")
        if (target_x is not None or target_y is not None) and target_port is not None:
            raise ValueError("Mutually exclusive arguments.")

        curr_time = int(time.time())
        new_journey = FleetJourney(target_port_id=target_port,
                                   target_x=target_x,
                                   target_y=target_y,
                                   arrival_time=curr_time+random.randint(60, 180))
        self.journeys.append(new_journey)
        if self.port is not None:
            self.set_sea_position(self.port.x, self.port.y, curr_time)
        elif len(self.journeys) == 1:
            self.set_sea_position(self.position_x, self.position_y, curr_time)
        return new_journey


    def set_sea_position(self, x, y, timestamp):
        """ Move fleet to the given corrds on the sea.
       
        Args:
            x(int): position on x-axis.
            y(int): position on y-axis.
            timestamp(int): date timestamp telling when fleet appeared at the position. """
        self.position_x = x
        self.position_y = y
        self.port_id = None
        self.position_timestamp = timestamp
        self.status = FLEET_ON_THE_SEA

    def set_port(self, port, timestamp):
        """ Move fleet into the port.
       
        Args:
            port(int): Id of island where port is located.
            timestamp(int): date timestamp telling when fleet appeared at the port. """
        self.port_id = port
        self.position_x = None
        self.position_y = None
        self.position_timestamp = timestamp
        self.status = FLEET_AT_THE_PORT


class FleetJourney(Base, ThalassaModel):
    __tablename__ = 'fleet_journey'
    id = Column(Integer, primary_key=True)
    fleet_id = Column(Integer, ForeignKey('fleet.id'))
    # target_port_id or target_coords(x & y) only one is non null.
    target_port_id = Column(Integer, ForeignKey('island.id'), nullable=True)
    target_x = Column(Integer, nullable=True)
    target_y = Column(Integer, nullable=True)
    arrival_time = Column(Integer, nullable=False)

    fleet = relationship('Fleet', back_populates='journeys')
    port = relationship('Island')