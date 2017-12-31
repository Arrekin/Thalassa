""" Thalassa caching system. """

_temp_cache = {}

class CacheService:

    def SetPlayerSession(self, *, session_hash, username):
        _temp_cache[session_hash] = username

    def GetPlayerSession(self, *, session_hash):
      try:
          return _temp_cache[session_hash]
      except KeyError:
          raise PlayerSessionError("No such player session")

class PlayerSessionError(Exception):
    pass
