from serviceoutages import ServiceOutages
from flapping import Flapping
from datetime import datetime, timedelta
import hug
import json


# function that opens file and load data from it
def initStart():
    with open('./outages.json') as file_dump:
        json_data = json.load(file_dump)

    return json_data


# function that create service with given properties
def createService(service_string):
    return ServiceOutages(service_string['service_id'],
                          datetime.strptime(service_string['startTime'], "%Y-%m-%d  %H:%M:%S"),
                          service_string['duration'],
                          datetime.strptime(service_string['startTime'], "%Y-%m-%d  %H:%M:%S")
                          + timedelta(minutes=service_string['duration']))


# function that visualize currently down services
@hug.get('/api/currently-down')
def get_currently_down():
    down_services = []
    services = initStart()
    for service_string in services:
        service = createService(service_string)
        if service.startTime.date() <= datetime.today().date() and service.startTime.time() <= datetime.today().time():
            if service.endTime.date() >= datetime.today().date() and service.endTime.time() <= datetime.today().time():
                down_services.append(service.__dict__)

    if not down_services:
        return 'There are currently no down services'

    return down_services


# function that visualize recently down services in last 3 hours
@hug.get('/api/recently-down')
def get_recently_down():
    recently_down_services = []
    services = initStart()
    for service_string in services:
        service = createService(service_string)
        recent_time = datetime.today() - timedelta(hours=3)
        if datetime.today().date() <= service.startTime.date() and recent_time.time() <= service.startTime.time():
            if service.endTime.date() >= datetime.today().date() and service.endTime.time() <= datetime.today().time():
                recently_down_services.append(service.__dict__)

    if not recently_down_services:
        return 'There are no recently down services'

    return recently_down_services


# function that adds new outage for service
@hug.post('/api/add-service')
def add_new_service(body):
    print("GOT {}: {}".format(type(body), repr(body)))
    service_outages = initStart()
    service_outages.append(body)
    with open('./outages.json', 'w') as outfile:
        json.dump(service_outages, outfile)


# function that detect flapping scenarios and visualize them
@hug.get('/api/flapping-scenarios')
def get_flapping_service():
    services_dump = initStart()
    service_set = {None}
    flappings = []
    f = None
    for service_dump in services_dump:
        service = createService(service_dump)
        service_set.add(service.service_id)
    for service_id in service_set:
        down_time = 0
        f = Flapping(service_id, 0, 0)
        for service_dump in services_dump:
            service = createService(service_dump)

            if service_id == service.service_id:
                f.service_id = service.service_id
                if service.startTime <= (datetime.today() - timedelta(hours=2)) < service.endTime:
                    f.sumOfOutages += service.endTime - timedelta(hours=datetime.today().time().hour - 2,
                                                                  minutes=datetime.today().time().minute)
                    f.amountOfOutages += 1

                if service.startTime >= (datetime.today() - timedelta(hours=2)):
                    f.sumOfOutages += service.duration
                    f.amountOfOutages += 1

                if f.sumOfOutages >= 15:
                    flappings.append(f.__dict__)

    if not flappings:
        return 'There was not flapping scenarios in last 2 hours'

    return flappings
