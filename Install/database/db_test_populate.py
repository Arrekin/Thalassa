""" Populate databse with test data. """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_create import Base, User

engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(login='Test User',
            password_hash='xxx',
            email='test@test.test')

session.add(user)
session.commit()