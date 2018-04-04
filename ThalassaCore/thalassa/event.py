import enum
import time
import traceback

import greenstalk

from thalassa.database.models import FLEET_AT_THE_PORT, FLEET_ON_THE_SEA
import thalassa.database.agent
import thalassa.factory
import thalassa.logging

logger = thalassa.logging.get_logger("thalassa_event")

class EventType(enum.Enum):
    FLEET_ARRIVAL = 0


class EventQueue:
    """ Facade for greenstalk(beanstalkd proxy). """

    def __init__(self, host='127.0.0.1', port=11300):
        self.event_queue = greenstalk.Client(host=host, port=port)


    def put(self, *, relative_event_time = None, absolute_event_time = None, event_type, event_data):
        """ Add new event to the beanstalk queue and get its id

        Args:
            relative_event_time(int): Time in seconds counting from now when event should trigger
            absolute_event_time(int): Timestamp in seconds when event should trigger
            event_type(EventType): Type of the event
            event_data(string): Custom data linked with event """
        if relative_event_time and absolute_event_time:
            raise ValueError("relative_event_time/absolute_event_time -> Only one can be specified.")
        elif not (relative_event_time or absolute_event_time):
            raise ValueError("realtive_event_time or absolute_event_time has to be specified.")
        if relative_event_time:
            event_time = relative_event_time
        else:
            event_time = absolute_event_time - int(time.time())
        event_time = max(0, event_time)
        return self.event_queue.put("{},{}".format(event_type.name, event_data), delay=event_time)


    def reserve(self, *, timeout=None):
        """ Look at greenstalk.reserve(). """
        return self.event_queue.reserve(timeout=timeout)


    def delete(self, job):
        """ Look at greenstalk.delete(). """
        return self.event_queue.delete(job=job)

    def close(self):
        """ Look at greenstalk.close(). """
        return self.event_queue.close()


class EventExecutionFailed(Exception):
    pass


def execute_event(event_type, event_data):
    """ Execute event of given type

    Args:
        event_type(EventType): Type of the event
        event_data(str): Details of the event(delimited by ";") """
    return _EXECUTION_MAP[event_type](event_data)


def fleet_arrival(event_data):
    """ Execute event of fleet with <fleet_id>
    Args:
        event_data(string): fleet_id """
    try:
        fleet_id = int(event_data)
    except (ValueError, TypeError) as exc:
        logger.error("Event FLEET_ARRIVAL data corrupted!")
        logger.error("Corrupted event data: {}".format(fleet_id))
        logger.debug(traceback.format_exc())
        raise EventExecutionFailed

    # First query the database for given fleet and validate it.
    world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
    fleets_search = world_agent.fleets(on_sea=True, at_port=True, fleet_ids=[fleet_id])
    try:
        fleet = fleets_search[fleet_id]
    except KeyError:
        logger.error("Event FLEET_ARRIVAL expected one fleet with id[{}]".format(fleet_id))
        logger.error("Instead received: []".format(fleets_search.to_jsonready_dict()))
        raise EventExecutionFailed
    if fleet.status != FLEET_ON_THE_SEA:
        logger.error("Event FLEET_ARRIVAL fleet[{}] is expected to be on the sea but"
                     " instead its status is [{}]".format(fleet_id, fleet.status))
        logger.debug("Full fleet info: {}".format(str(fleet.as_dict())))
        raise EventExecutionFailed
    if len(fleet.journeys) == 0:
        logger.error("Event FLEET_ARRIVAL fleet[{}] has no pending journeys!".format(fleet_id))
        raise EventExecutionFailed
    journey = fleet.soonest_journey()
    current_time = time.time()
    if current_time < journey.arrival_time:
        logger.error("Event FLEET_ARRIVAL fleet[{}] journey[{}] did not end yet!".format(fleet_id, journey.id))
        logger.error("Current time [{}], Arrival time [{}]".format(current_time, journey.arrival_time))
        logger.debug("All journeys for fleet[{}]: {}".format(fleet_id, 
                         '\n'.join(str(journey) for journey in fleet.journeys)))

_EXECUTION_MAP = {
    EventType.FLEET_ARRIVAL: fleet_arrival,
    }