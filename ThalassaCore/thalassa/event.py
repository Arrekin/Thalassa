import enum
import time

import greenstalk

class EventType(enum.Enum):
    FLEET_ARRIVAL = 0


class EventQueue:
    """ Facade for greenstalk(beanstalkd proxy). """

    def __init__(self, host='127.0.0.1', port=11300):
        self.event_queue = greenstalk.Client(host=host, port=port)


    def put(self, *, relative_event_time = None, absolute_event_time = None, event_type, event_data):
        """ Add new event to the beanstalk queue and get its id

        Args:
            relative_event_time (int): Time in seconds counting from now when event should trigger
            absolute_event_time (int): Timestamp in seconds when event should trigger
            event_type (EventType): Type of the event
            event_data (string): Custom data linked with event """
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
