""" Module with all kinds of players entities. """
import thalassa.cache
import thalassa.database.agent
import thalassa.event
import thalassa.exception
import thalassa.factory
import thalassa.logging

class Player:
    """ Base class for entities that can influence game progress. """

    def __init__(self):
        self.logger = thalassa.logging.get_logger("thalassa_player")

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
        session_hash (str):  Cached session stored in redis. """
    __agent_type = thalassa.database.agent.PlayerAgent

    def __init__(self):
        super().__init__()
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
            password (string): Player's password. """
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
            self.logger.debug("-> User's data loaded: "+str("None" if not user else user.as_dict()))
            if user.password_hash is not None:
                self.session_hash = b"MAKeiTGEnerAtedlaTER"
                cache_service.SetPlayerSession(session_hash=self.session_hash,
                                               session_data=user.id)
            return

        raise TypeError("Required arguments not provided")


    def move_fleet_command(self, db_session, *, fleet_id, target_x=None, target_y=None, target_port=None):
        """ Issue moving fleet to destined world location.
        
        Note: target coordinates(x & y) and target_port are mutually exclusive.

        Args:
            fleet_id(int): Fleet table row id.
            target_x(int): Target position on x-axis.
            target_y(int): Target_position on y-axis.
            target_port(int): Island table row id. """
        if (target_x is not None or target_y is not None) and target_port is not None:
            raise ValueError("Mutually exclusive arguments.")
        if (target_x is None or target_y is None) and target_port is None:
            raise ValueError("Invalid fleet movement target.")
        world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
        fleets = world_agent.get_fleets(db_session, on_sea=True, at_port=True, fleets_ids=[fleet_id])
        if len(fleets) == 0:
            self.logger.warning("Player[{}] tries to move non existing fleet[{}].".format(self.user_id,
                                                                                         fleet_id))
            raise thalassa.exception.FleetDoNotExistError;
        if len(fleets) >= 2:
            self.logger.error("Expected 1 fleet with id[{}] but got: {} entries.".format(fleet_id,
                                                                                        len(fleets)))
            raise thalassa.exception.ThalssaInternalError;
        fleet = next(iter(fleets))
        if fleet.owner.id != self.user_id:
            self.logger.warning("Player[{}] tries to move fleet[{}] that do not belong to him.".format(self.user_id,
                                                                                                       fleet.id))
            raise thalassa.exception.OwnershipError;
        new_journey = fleet.add_journey(target_x=target_x, target_y=target_y)
        db_session.flush()
        thalassa.event.create_fleet_arrival(journey_id=new_journey.id,
                        fleet_id=fleet.id,
                        arrival_time=new_journey.arrival_time)
