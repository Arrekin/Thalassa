""" Populate databse with test data. """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from thalassa.database.models import Base, Island, User

engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(login='testo',
            password_hash='xxx',
            email='test@test.test')
session.add(user)

island_otta = Island(id="sdasdasd",
                     name="Otta",
                     x=200,
                     y=300)
session.add(island_otta)

island_alda = Island(id="jlkjkljl",
                     name="Alda",
                     x=500,
                     y=100)
session.add(island_alda)

island_grikmik = Island(id="kllkjlk",
                     name="Grikmik",
                     x=550,
                     y=400)
session.add(island_grikmik)

session.commit()