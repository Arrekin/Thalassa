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


    def release(self, job):
        """ Look at greenstalk.release(). """
        return self.event_queue.release(job=job)


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
    try:
        db_session = thalassa.factory.CreateDatabaseSession()
        _EXECUTION_MAP[event_type](event_data, db_session)
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def create_fleet_arrival(*, journey_id, fleet_id, arrival_time):
    """ Create event FLEET_ARRIVAL and push it into queue.
    
    Args:
        journey_id(int): FleetJourney table row id.
        fleet_id(int): Fleet table row id.
        arrival_time(int): Timestamp indicating end of the journey."""
    try:
        event_queue = thalassa.factory.Create(thalassa.event.EventQueue)
        event = event_queue.put(absolute_event_time=arrival_time,
                        event_type=EventType.FLEET_ARRIVAL,
                        event_data=';'.join((str(journey_id),str(fleet_id))))
        logger.info("Added to event queue.")
        return event
    except:
        import traceback
        traceback.print_exc()
    finally:
        event_queue.close()


def finalize_fleet_arrival(event_data, db_session):
    """ Execute event of fleet with <fleet_id>
    Args:
        event_data(string): fleet_id
        db_session(DatabeSession class): active session to database"""
    try:
        journey_id, fleet_id = [int(elem) for elem in event_data.split(';')]
    except (ValueError, TypeError) as exc:
        logger.error("Event FLEET_ARRIVAL data corrupted!")
        logger.error("Corrupted event data: {}".format(fleet_id))
        logger.debug(traceback.format_exc())
        raise EventExecutionFailed

    # First query the database for given fleet and validate it.
    world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
    fleets_search = world_agent.get_fleets(db_session, on_sea=True, at_port=True, fleets_ids=[fleet_id])
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
    if journey.fleet.id != fleet_id:
        logger.error("Event FLEET_ARRIVAL journey[{} does not belong to fleet[{}]!".format(journey.id, fleet_id))
        logger.debug("Journey data: {}, Fleet data: {}".format(journey.as_dict(), fleet.as_dict()))
        raise EventExecutionFailed
    if journey.id != journey_id:
        logger.error("Event FLEET_ARRIVAL journey[{}] marked for finish but it seems there are some earlier unfinished journeys!".format(journey.id))
        raise EventExecutionFailed
    current_time = int(time.time())
    if current_time < journey.arrival_time:
        logger.error("Event FLEET_ARRIVAL fleet[{}] journey[{}] did not end yet!".format(fleet_id, journey.id))
        logger.error("Current time [{}], Arrival time [{}]".format(current_time, journey.arrival_time))
        logger.debug("All journeys for fleet[{}]: {}".format(fleet_id, 
                         '\n'.join(str(journey) for journey in fleet.journeys)))
        raise EventExecutionFailed

    # Now it's time to update fleet position
    if journey.target_port_id is not None:
        fleet.set_port(journey.target_port_id, journey.arrival_time)
        fleet.transfer_resources(journey.port, wood=fleet.wood, wheat=fleet.wheat, wine=fleet.wine)
    else:
        fleet.set_sea_position(journey.target_x, journey.target_y, journey.arrival_time)

    # And at the end remove the journey
    db_session.delete(journey)
    logger.debug("Journey[{}] of Fleet[{}] has ended".format(journey.id, fleet.id))


_EXECUTION_MAP = {
    EventType.FLEET_ARRIVAL: finalize_fleet_arrival,
    }