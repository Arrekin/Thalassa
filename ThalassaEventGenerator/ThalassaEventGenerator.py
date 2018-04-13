import random
import time

import thalassa.factory
import thalassa.event
import thalassa.database.agent
from thalassa.database.models import USER_AI

EventType = thalassa.event.EventType

if __name__ == '__main__':
    while True:
        time.sleep(0)
        print("Time to generate new event!")
        try:
            db_session = thalassa.factory.CreateDatabaseSession()
            world_agent = thalassa.factory.Create(thalassa.database.agent.WorldAgent)
            fleets_at_port = world_agent.get_fleets(db_session,
                                                    on_sea=False,
                                                    at_port=True,
                                                    owners_types=[USER_AI])
            if len(fleets_at_port) == 0:
                print("No any fleet at port.")
                continue
            choosen_fleet = fleets_at_port[random.choice(fleets_at_port.keys())]
            if len(choosen_fleet.journeys) > 0:
                print("ERROR! Fleet [{}] is in the port and still have journeys.".format(choosen_fleet.id))
                continue
            port = choosen_fleet.port
            wood_load = random.randint(0, min(port.wood, 10))
            wheat_load = random.randint(0, min(port.wheat, 10))
            wine_load = random.randint(0, min(port.wine, 10))
            port.transfer_resources(choosen_fleet, wood=wood_load, wheat=wheat_load, wine=wine_load)
            
            islands = world_agent.get_islands(db_session)
            islands_ids = islands.keys()
            islands_ids.remove(port.id)
            target_island = islands[random.choice(islands_ids)]

            new_journey = choosen_fleet.add_journey(target_port=target_island.id)
            db_session.commit()
            print("Fleet [{}] going to [{}] with [wood:{}, wheat:{}, wine:{}]".format(
                choosen_fleet.id, target_island.name, choosen_fleet.wood, choosen_fleet.wheat, choosen_fleet.wine))
        except:
            db_session.rollback()
            import traceback
            traceback.print_exc()
        else:
            try:
                event_queue = thalassa.factory.Create(thalassa.event.EventQueue)
                event_queue.put(absolute_event_time=new_journey.arrival_time,
                                event_type=EventType.FLEET_ARRIVAL,
                                event_data=str(choosen_fleet.id))
                print("Added to event queue.")
            except:
                import traceback
                traceback.print_exc()
            finally:
                event_queue.close()
        finally:
            db_session.close()
            print("going to sleep...")
            time.sleep(5)