""" Containers to store game objects. """
import json

import thalassa.database.models

class ThalassaObjectsContainer:
    """ Base class for Thalassa objects containers. """

    def to_json(self, *, standalone=True):
        raise NotImplementedError("This is to_json() ThalassaObjectContainer method. Implement it...")


class IslandsContainer(ThalassaObjectsContainer):
    """ Holds islands objects. """

    def __init__(self, initial_object=None):
        self.__container = {}

        try:
            for island in initial_object:
                self.add(island)
        except TypeError:
            self.add(initial_object)


    def add(self, island):
        """ Add island to the container.
        
        Args:
            island(thalassa.databe.models): Object to be added to the container.
        """
        self.__container[island.name] = island


    def to_json(self, *, standalone=True):
        """ Convert container to JSON.
        
        Args:
            standalone(bool): When set to true function returns fully valid JSON.
                Otherwise returns fragment that can be treated as part of JSON object.
        """
        islands_list = [island.as_dict() for island in self.__container.values()]
        import time
        fleets = [
            {"id":1, "owner":"blblb", "x":200, "y":200, "horizontalSpeed":10, "verticalSpeed":10, "timestamp": int(time.time())},
            {"id":2, "owner":"blblb", "x":500, "y":300, "horizontalSpeed":20, "verticalSpeed":1, "timestamp": int(time.time())},
            {"id":3, "owner":"blblb", "x":700, "y":700, "horizontalSpeed":-10, "verticalSpeed":-10, "timestamp": int(time.time())}
            ]
        json_dict = {"islands": islands_list, "fleets": fleets}
        json_body = json.dumps(json_dict)

        return json_body
