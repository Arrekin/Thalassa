""" Thalassa caching system. """

_temp_cache = {}

class CacheService:

    def SetPlayerSession(self, *, session_hash, session_data):
        _temp_cache[session_hash] = session_data

    def GetPlayerSession(self, *, session_hash):
      try:
          return _temp_cache[session_hash]
      except KeyError:
          raise PlayerSessionError("No such player session")


class PlayerSessionError(Exception):
    pass
