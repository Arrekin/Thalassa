import enum
import operator
import time

import greenstalk

import thalassa.factory
import thalassa.database.agent

class EventType(enum.Enum):
    FLEET_ARRIVAL = 0

def load_events_from_db():
    """ Load all relevant events from database and put them into queue. """
    world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
    fleets_on_sea = world_agent.get_fleets(on_sea=True, at_port=False)
    for fleet in fleets_on_sea:
        if len(fleet.journeys) > 0:
            closest_journey = min(fleet.journeys, key=operator.attrgetter('arrival_time'))
            add_event(absolute_event_time=closest_journey.arrival_time,
                      event_type=EventType.FLEET_ARRIVAL,
                      event_data=str(fleet.id))    

def add_event(*, relative_event_time = None, absolute_event_time = None, event_type, event_data, callback=None):
    """ Add new event to the beanstalk queue and get its id

    Args:
        relative_event_time (int): Time in seconds counting from now when event should trigger
        absolute_event_time (int): Timestamp in seconds when event should trigger
        event_type (EventType): Type of the event
        event_data (string): Custom data linked with event
        callback (function): Funtion to be called when event successfully inserted """
    if relative_event_time and absolute_event_time:
        raise ValueError("relative_event_time/absolute_event_time -> Only one can be specified.")
    elif not (relative_event_time or absolute_event_time):
        raise ValueError("realtive_event_time or absolute_event_time has to be specified.")
    if relative_event_time:
        event_time = relative_event_time
    else:
        event_time = absolute_event_time - int(time.time())
    event_time = max(0, event_time)
    return event_queue.put("{},{}".format(event_type.name, event_data), delay=event_time+20)


def manage_event(event):
    print("Got task from queue:{}".format(event.body))
    event_type, event_data = event.body.split(",")
    event_type = EventType[event_type]

    event_queue.delete(event)


def process():
    load_events_from_db()
    while True:
        event = event_queue.reserve()
        manage_event(event)
        print("Event managed!")


event_queue = greenstalk.Client()
process()