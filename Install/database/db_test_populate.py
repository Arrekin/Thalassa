""" Populate databse with test data. """
import time
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from thalassa.database.models import Base, Fleet, FleetJourney, Island, User, USER_EXTERNAL, USER_AI

engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

user = User(login='testo',
            type=USER_EXTERNAL,
            password_hash='xxx',
            email='test@test.test')
session.add(user)

island_otta = Island(name="Otta",
                     x=200,
                     y=300,
                     wood=random.randint(0,100),
                     wheat=random.randint(0,100),
                     wine=random.randint(0,100))
session.add(island_otta)

island_alda = Island(name="Alda",
                     x=500,
                     y=100,
                     wood=random.randint(0,100),
                     wheat=random.randint(0,100),
                     wine=random.randint(0,100))
session.add(island_alda)

island_grikmik = Island(name="Grikmik",
                     x=550,
                     y=400,
                     wood=random.randint(0,100),
                     wheat=random.randint(0,100),
                     wine=random.randint(0,100))
session.add(island_grikmik)

island_lothe = Island(name="Lothe",
                     x=150,
                     y=100,
                     wood=random.randint(0,100),
                     wheat=random.randint(0,100),
                     wine=random.randint(0,100))
session.add(island_lothe)

island_ivory = Island(name="Ivory",
                     x=350,
                     y=500,
                     wood=random.randint(0,100),
                     wheat=random.randint(0,100),
                     wine=random.randint(0,100))
session.add(island_ivory)

fleet_testo_1 = Fleet(status=1,
                      position_x=200,
                      position_y=200,
                      position_timestamp=int(time.time()))
user.fleets.append(fleet_testo_1)

flet_testo_1_journey_1 = FleetJourney(target_x=600,
                                      target_y=600,
                                      arrival_time=int(time.time())+60)
fleet_testo_1.journeys.append(flet_testo_1_journey_1)
flet_testo_1_journey_2 = FleetJourney(target_x=400,
                                      target_y=100,
                                      arrival_time=int(time.time())+120)
fleet_testo_1.journeys.append(flet_testo_1_journey_2)

ai_user = User(login='ai_test',
            type=USER_AI,
            password_hash='xxx',
            email='test@test.test')
session.add(ai_user)
islands = [island_otta, island_alda, island_grikmik, island_lothe, island_ivory]
for _ in range(10):
    fleet_ai_user = Fleet(status=0,
                          position_timestamp=int(time.time()))
    random.choice(islands).fleets.append(fleet_ai_user)
    ai_user.fleets.append(fleet_ai_user)


session.commit()