""" Script for creating base database. """
import datetime

from sqlalchemy import create_engine

from thalassa.database.models import Base

engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')

Base.metadata.create_all(engine)