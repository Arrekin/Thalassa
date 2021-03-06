""" Thalassa factory module. """
import thalassa.cache
import thalassa.database.agent
import thalassa.database.queries
import thalassa.event
import thalassa.players

# Reference to all possible dependencies
_reference_bank = None


def Create(object_type):
    """ Creates new instance of object of given type. 

    Args:
        object_type (type): Type of the object that should be created.
    """
    if _reference_bank is None:
        SetReferences()

    return _reference_bank[object_type]()


def CreateDatabaseSession():
    """ Creates new SQLAlchemy session to the database. """
    return thalassa.database.queries.DatabaseSessionManager().CreateNewSession()


def SetReferences(new_references=None, *, replace=False):
    """ Sets _reference_bank.

    Args:
        new_references (None/dict): If None sets default dependencies references.
            Otherwise it merges new setting to olds ones.
        
        replace (bool): If set to true new references will replace old ones
            instead of merge.
    """
    global _reference_bank

    if new_references is None:
        # Set default references
        _reference_bank = {
            #    ---   thalassa.player   ---    #
            thalassa.players.ExternalPlayer: thalassa.players.ExternalPlayer,
            #    ---   thalassa.database.agents   ---    #
            thalassa.database.agent.PlayerAgent: thalassa.database.agent.PlayerAgent,
            thalassa.database.agent.WorldAgent:  thalassa.database.agent.WorldAgent,
            #    ---   thalassa.database.cache   ---    #
            thalassa.cache.CacheService: thalassa.cache.CacheService,
            #    ---   thalassa.event   ---    #
            thalassa.event.EventQueue: thalassa.event.EventQueue,
        }
        return

    if replace or _reference_bank is None:
        _reference_bank = new_references
        return

    _reference_bank = {**_reference_bank, **new_references}
