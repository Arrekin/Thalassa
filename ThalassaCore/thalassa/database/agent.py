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

    def get_user(self, db_session, *, username):
        """ Returns user with given username or None if user were not found.
        
        Args:
            db_session(DatabeSession class): active session to database.
            username(string): username to look for."""
        result = db_session.query(User).\
                                filter(User.login==username).\
                                one_or_none()
        return result


class WorldAgent(Agent):
    """ Class for extracting world data from database. """

    def get_islands(self, db_session):
        """ Return Islands container object with all islands.
        
        Args:
            db_session(DatabeSession class): active session to database."""
        result = db_session.query(Island)
        return thalassa.container.IslandsContainer(result)

    def get_fleets(self, db_session, *, on_sea, at_port, fleet_ids=None):
        """ Return Fleets container object with all fleets.

        Args:
            db_session(DatabeSession class): active session to database.
            on_sea(bool): Include fleets that are currently on the sea.
            at_port(bool): Include fleets that are currently at the port. 
            fleet_ids(list): Limit search to provided list of fleet ids.
        """
        fleets = db_session.query(Fleet).options(joinedload(Fleet.journeys))
        if not on_sea:
            fleets = fleets.filter(~Fleet.status==FLEET_ON_THE_SEA)
        if not at_port:
            fleets = fleets.filter(~Fleet.status==FLEET_AT_THE_PORT)
        if fleet_ids:
            fleets = fleets.filter(Fleet.id.in_(fleet_ids))
        fleets = fleets.all()
        return thalassa.container.FleetsContainer(fleets)
