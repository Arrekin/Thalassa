import enum
import operator
import queue

import thalassa.factory
import thalassa.database.agent

class EventType(enum.Enum):
    FLEET_ARRIVAL = 0

def load_events_from_db(event_queue):
    """ Load all relevant events from database and put them into queue. """
    world_agent = thalassa.database.agent.WorldAgent()
    fleets_on_sea = world_agent.get_fleets(on_sea=True, at_port=False)
    for fleet in fleets_on_sea:
        if len(fleet.journeys) > 0:
            closest_journey = min(fleet.journeys, key=operator.attrgetter('arrival_time'))
            event_queue.put((closest_journey.arrival_time, EventType.FLEET_ARRIVAL, (fleet.id,)))    

event_queue = queue.PriorityQueue()

load_events_from_db(event_queue)

while True:
    event_time, event_type, event_data = event_queue.get()
    print(event_time, event_type.name, event_data)
