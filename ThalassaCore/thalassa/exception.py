class ThalassaException(Exception):
    """ Base class for all thalassa exceptions. """

class ThalassaInternalError(ThalassaException):
    """ Happend something we know for sure that should not! """

#------------------------------------
# players.py exceptions
#------------------------------------
class ThalassaCommandError(ThalassaException):
    """ Base class for commands-related exceptions. """

class FleetDoNotExistError(ThalassaCommandError):
    """ Fleet with given id do not exists. """

class OwnershipError(ThalassaCommandError):
    """ Action requested on object that do not belong the player. """