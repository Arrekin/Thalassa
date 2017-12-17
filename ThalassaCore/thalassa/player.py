""" Module with all kinds of players entities. """

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

    def __init__(self, *,
                 session_hash):
        self.session_hash = session_hash  # Cached session stored in redis.
