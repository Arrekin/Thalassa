""" Module with all kinds of players entities. """
import thalassa.database.agent
import thalassa.factory
import thalassa.logging

class Player:
    """ Base class for entities that can influence game progress. """
    pass

class ExternalPlayer(Player):
    """ Process commands from entities that using Thalassa Api to access game world. 
    
    Args:
        session_hash (str):  Cached session stored in redis.

    Attributes:
        session_hash (str):  Cached session stored in redis.
    """

    def __init__(self):
        self.session_hash = None  # Cached session stored in redis.

        my_agent_type = thalassa.database.agent.PlayerAgent
        self.agent = thalassa.factory.Create(my_agent_type)


    def is_authenticated(self):
        """ Check whether player were authenticated. """

        return self.session_hash is not None


    def authenticate(self, *, session_hash=None, username=None, password=None):
        """ Checks if provided credentials are valid.

        Note:
            Options are mutually exclusive. Provide username and password to log-in the player
            or session_hash if player has already an active session.

        Args:
            session_hash (string): Hash generated when player was logging in.
            username (string): Player's username.
            password (string): Player's password.
        """

        if session_hash and (username or password):
            raise TypeError("Mutually exclusive arguments")

        # TODO:
        if session_hash:
            return

        if username and password:
            password_hash = self.agent.get_password_hash(username=username)
            logger = thalassa.logging.get_logger("thalassa_api")
            logger.debug("User's password hash is: "+str(password_hash))
            if password_hash is not None:
                self.session_hash = "MAKeiTGEnerAtedlaTER"
            return

        raise TypeError("Required arguments not provided")