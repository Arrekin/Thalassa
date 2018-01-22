""" Thalassa agents extracting data from database. """
from sqlalchemy.orm import joinedload

from thalassa.database.models import Fleet, Island, User
from thalassa.database.models import FLEET_AT_THE_PORT, FLEET_ON_THE_SEA
import thalassa.container
import thalassa.factory

class Agent:
    """ Base class for agents. """

    pass


class PlayerAgent(Agent):
    """ Agent extracting players data from database. """

    def get_user(self, *, username):
        """ Returns user with given username or None if user were not found. """
        session = thalassa.factory.CreateDatabaseSession()
        try:
            result = session.query(User).\
                                    filter(User.login==username).\
                                    one_or_none()
            return result
        finally:
            session.close()


class WorldAgent(Agent):
    """ Class for extracting world data from database. """

    def get_islands(self):
        """ Return Islands container object with all islands. """
        session = thalassa.factory.CreateDatabaseSession()
        try:
            result = session.query(Island)
            return thalassa.container.IslandsContainer(result)
        finally:
            session.close()

    def get_fleets(self, *, on_sea, at_port):
        """ Return Fleets container object with all fleets.

        Args:
            on_sea(bool): Include fleets that are currently on the sea.
            at_port(bool): Include fleets that are currently at the port. 
        """
        session = thalassa.factory.CreateDatabaseSession()
        try:
            fleets = session.query(Fleet).options(joinedload(Fleet.journeys))
            if not on_sea:
                fleets = fleets.filter(~Fleet.status==FLEET_ON_THE_SEA)
            if not at_port:
                fleets = fleets.filter(~Fleet.status==FLEET_AT_THE_PORT)
            fleets = fleets.all()
            return thalassa.container.FleetsContainer(fleets)
        finally:
            session.close()
