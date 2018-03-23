import operator

import thalassa.factory
import thalassa.database.agent
import thalassa.event

EventType = thalassa.event.EventType

def load_events_from_db():
    """ Load all relevant events from database and put them into queue. """
    world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
    fleets_on_sea = world_agent.get_fleets(on_sea=True, at_port=False)
    for fleet in fleets_on_sea:
        if len(fleet.journeys) > 0:
            closest_journey = min(fleet.journeys, key=operator.attrgetter('arrival_time'))
            event_queue.put(absolute_event_time=closest_journey.arrival_time,
                      event_type=EventType.FLEET_ARRIVAL,
                      event_data=str(fleet.id))    



def manage_event(event):
    print("Got task from queue:{}".format(event.body))
    event_type, event_data = event.body.split(",")
    event_type = EventType[event_type]

    event_queue.delete(event)


def process():
    load_events_from_db()
    while True:
        curr_event = event_queue.reserve()
        manage_event(curr_event)
        print("Event managed!")


event_queue = thalassa.factory.Create(thalassa.event.EventQueue)
process()