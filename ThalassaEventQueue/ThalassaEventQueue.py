import thalassa.factory
import thalassa.database.agent
import thalassa.event

EventType = thalassa.event.EventType

def load_events_from_db():
    """ Load all relevant events from database and put them into queue. """
    try:
        db_session = thalassa.factory.CreateDatabaseSession()
        world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
        fleets_on_sea = world_agent.get_fleets(db_session, on_sea=True, at_port=False)
    finally:
        db_session.close()

    for fleet in fleets_on_sea:
        for journey in fleet.journeys:
            event_queue.put(absolute_event_time=journey.arrival_time,
                      event_type=EventType.FLEET_ARRIVAL,
                      event_data=';'.join((str(journey.id), str(fleet.id))))


def manage_event(event):
    print("Got task from queue:{}".format(event.body))
    event_type, event_data = event.body.split(",")
    event_type = EventType[event_type]
    try:
        thalassa.event.execute_event(event_type, event_data)
    except thalassa.event.EventExecutionFailed as exc:
        print("Event execution Failed: {}".format(exc))
        event_queue.delete(event)
    except:
        import traceback
        traceback.print_exc()
        event_queue.release(event)
    else:
        event_queue.delete(event)


def process():
    load_events_from_db()
    while True:
        curr_event = event_queue.reserve()
        manage_event(curr_event)
        print("Event managed!")


if __name__ == '__main__':
    event_queue = thalassa.factory.Create(thalassa.event.EventQueue)
    process()