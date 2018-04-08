""" Containers to store game objects. """
import math

import thalassa.database.models

class ThalassaObjectsContainer:
    """ Base class for Thalassa objects containers.

    Args:
        initial_object(any): If iterable add all objects that are inside,
            otherwise add the object itself. Each object has to have id field.
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

    def __len__(self):
        return len(self.container)

    def __getitem__(self, item_id):
        return self.container[item_id]


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
        json_dict = {"islands": islands_list}

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
                curr_journey = fleet.soonest_journey()
                time_diff = curr_journey.arrival_time - fleet.position_timestamp
                new_fleet['horizontal_speed'] = -(fleet.position_x - curr_journey.target_x) / time_diff
                new_fleet['vertical_speed'] = -(fleet.position_y - curr_journey.target_y) / time_diff
            fleets.append(new_fleet)

        json_dict = {"fleets": fleets}

        return json_dict