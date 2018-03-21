""" Containers to store game objects. """
import math

import thalassa.database.models

class ThalassaObjectsContainer:
    """ Base class for Thalassa objects containers.

    Args:
        initial_object(any): If iterable add all objects that are inside,
            otherwise add the object itself.
    """

    def __init__(self, initial_object):
        self.container = {}

        try:
            for island in initial_object:
                self.add(island)
        except TypeError:
            self.add(initial_object)


    def __iter__(self):
        return iter(self.container.values())


    def add(self, object_to_add):
        """ Add an object to the container.
        
        Args:
            object_to_add(thalassa.databe.models): Object to be added to the container.
        """
        self.container[object_to_add.id] = object_to_add


    def to_jsonready_dict(self):
        """ Convert container to dict that is ready to be converted into JSON. """
        raise NotImplementedError("This is to_json() ThalassaObjectContainer method.")


class IslandsContainer(ThalassaObjectsContainer):
    """ Holds islands objects. """

    def to_jsonready_dict(self):
        """ Convert container to dict that is ready to be converted into JSON. """
        islands_list = [island.as_dict() for island in self.container.values()]
        import time
        fleets = [
            {"id":1, "owner":"blblb", "x":200, "y":200, "horizontalSpeed":10, "verticalSpeed":10, "timestamp": int(time.time())},
            {"id":2, "owner":"blblb", "x":500, "y":300, "horizontalSpeed":20, "verticalSpeed":1, "timestamp": int(time.time())},
            {"id":3, "owner":"blblb", "x":700, "y":700, "horizontalSpeed":-10, "verticalSpeed":-10, "timestamp": int(time.time())}
            ]
        json_dict = {"islands": islands_list, "fleets": fleets}

        return json_dict


class FleetsContainer(ThalassaObjectsContainer):
    """ Holds fleets objects. """

    def to_jsonready_dict(self):
        """ Convert container to dict that is ready to be converted into JSON. """
        fleets = []
        for fleet in self.container.values():
            new_fleet = {
                "id": fleet.id,
                "owner_id": fleet.owner_id,
                "x": fleet.position_x,
                "y": fleet.position_y,
                "timestamp": fleet.position_timestamp,
                }
            if not fleet.journeys:
                new_fleet['horizontal_speed'] = 0
                new_fleet['vertical_speed'] = 0
            else:
                curr_journey = min(fleet.journeys, key=lambda journey: journey.arrival_time)
                time_diff = curr_journey.arrival_time - fleet.position_timestamp
                new_fleet['horizontal_speed'] = time_diff / abs(fleet.position_x - curr_journey.target_x)
                new_fleet['vertical_speed'] = time_diff / abs(fleet.position_x - curr_journey.target_x)
            fleets.append(new_fleet)

        json_dict = {"fleets": fleets}

        return json_dict