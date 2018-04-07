""" Module with all kinds of players entities. """
import thalassa.cache
import thalassa.database.agent
import thalassa.factory
import thalassa.logging

class Player:
    """ Base class for entities that can influence game progress. """

    def get_full_world_data(self, db_session):
        """ Retrieve data about the world accessible to the player. 
            Return [IslandsContainer, FleetsContainer]
            
        Args:
            db_session(DatabeSession class): active session to database."""

        world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
        world_islands = world_agent.get_islands(db_session)
        world_fleets = world_agent.get_fleets(db_session, on_sea=True, at_port=False)

        return world_islands, world_fleets


class ExternalPlayer(Player):
    """ Process commands from entities that using Thalassa Api to access game world. 

    Args:
        session_hash (str):  Cached session stored in redis.

    Attributes:
        session_hash (str):  Cached session stored in redis.
    """
    __agent_type = thalassa.database.agent.PlayerAgent

    def __init__(self):
        self.session_hash = None  # Cached session stored in redis.
        self.user_id = None # User id in database

        self.agent = thalassa.factory.Create(self.__class__.__agent_type)


    def is_authenticated(self):
        """ Check whether player were authenticated. """

        return self.session_hash is not None


    def authenticate(self, db_session, *, session_hash=None, username=None, password=None):
        """ Checks if provided credentials are valid.

        Note:
            Options are mutually exclusive. Provide username and password to log-in the player
            or session_hash if player has already an active session.

        Args:
            db_session(DatabeSession class): active session to database.
            session_hash (string): Hash generated when player was logging in.
            username (string): Player's username.
            password (string): Player's password.
        """
        if session_hash and (username or password):
            raise TypeError("Mutually exclusive arguments")

        cache_service = thalassa.factory.Create(thalassa.cache.CacheService)

        if session_hash:
            try:
                session_data = cache_service.GetPlayerSession(session_hash=session_hash)
                self.session_hash = session_hash
                self.user_id = session_data
            except thalassa.cache.PlayerSessionError:
                self.session_hash = None
            return

        if username and password:
            user = self.agent.get_user(db_session, username=username)
            logger = thalassa.logging.get_logger("thalassa_api")
            logger.debug("-> User's data loaded: "+str("None" if not user else user.as_dict()))
            if user.password_hash is not None:
                self.session_hash = b"MAKeiTGEnerAtedlaTER"
                cache_service.SetPlayerSession(session_hash=self.session_hash,
                                               session_data=user.id)
            return

        raise TypeError("Required arguments not provided")
