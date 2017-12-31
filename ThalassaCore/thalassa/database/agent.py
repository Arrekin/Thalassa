""" Thalassa agents extracting data from database. """
from thalassa.database.models import User
import thalassa.factory

class Agent:
    """ Base class for agents. """

    pass


class PlayerAgent(Agent):
    """ Agent extracting players data from database. """

    def get_password_hash(self, *, username):
        """ Returns password hash for given username or None if user were not found. """
        session = thalassa.factory.CreateDatabaseSession()
        try:
            result = session.query(User.password_hash).\
                                    filter(User.login==username).\
                                    one_or_none()
            if result is None:
                return None
            password_hash, = result
            return password_hash
        finally:
            session.close()
