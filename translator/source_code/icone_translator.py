
import json
from datetime import datetime
import sys
import logging
from collections import OrderedDict
from translator.source_code import translator_shared_library


# Features

# [*] Add local-access-only restriction
# [*] Add license property to the RoadEventFeedInfo object


# Refactoring

# [*] Refactor LaneType enumerated type to deprecate values that can be determined from other properties of the Lane object, such as order, status, and lane_restrictions
# [*] Add value alternating-flow to LaneStatus enumerated type and deprecate alternating-one-way
# [*] Add road_names property to the RoadEvent object and deprecate road_name and road_number
# [*] Deprecate the total_num_lanes property on the RoadEvent object as the RoadEvent's lanes array can be used to determine the number of lanes


# Fixes

# [*]  Add optional bbox property to allow providing a GeoJSON Bounding Box for the WZDxFeed and RoadEventFeature objects
# [*]  Add an id property to the RoadEventFeature object for providing the a road event's identifier to better follow GeoJSON ID recommendations


# Translator
def main():
    inputfile, outputfile = translator_shared_library.parse_arguments(
        sys.argv[1:], default_output_file_name='icone_wzdx_translated_output_message.geojson')

    if inputfile:
        # Added encoding argument because of weird character at start of incidents.xml file

        icone_obj = translator_shared_library.parse_xml(inputfile)
        wzdx = wzdx_creator(icone_obj, translator_shared_library.initialize_info(
            '104d7746-688c-44ed-b195-2ee948bf9dfa'))
        location_schema = 'translator/sample files/validation_schema/wzdx_v3.1_feed.json'
        wzdx_schema = json.loads(open(location_schema).read())

        if not translator_shared_library.validate_wzdx(wzdx, wzdx_schema):
            print('validation error more message are printed above. output file is not created because the message failed validation.')
            return
        with open(outputfile, 'w') as fwzdx:
            fwzdx.write(json.dumps(wzdx, indent=2))
            print(
                'huraaah ! your wzdx message is successfully generated and located here: ' + str(outputfile))
    else:
        print('please specify an input json file with -i')
        print(translator_shared_library.help_string)


def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages or not messages.get('incidents', {}).get('incident'):
        return None
   # verify info obj
    if not info:
        info = translator_shared_library.initialize_info(
            '104d7746-688c-44ed-b195-2ee948bf9dfa')
    if not translator_shared_library.validate_info(info):
        return None

    wzd = translator_shared_library.initialize_wzdx_object(info)

    for incident in messages.get('incidents').get('incident'):
        # Parse Incident to WZDx Feature
        feature = parse_incident(
            incident, callback_function=unsupported_message_callback)
        if feature:
            wzd.get('features').append(feature)
    if not wzd.get('features'):
        return None
    wzd = translator_shared_library.add_ids(wzd)
    return wzd


#################### Sample Incident ####################
#   <incident id="U13631714_202012161717">
#     <creationtime>2020-12-16T17:17:00Z</creationtime>
#     <updatetime>2020-12-16T17:47:00Z</updatetime>
#     <type>CONSTRUCTION</type>
#     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
#     <location>
#       <direction>ONE_DIRECTION</direction>
#       <polyline>[28.8060608,-96.9916512,28.8060608,-96.9916512]</polyline>
#     </location>
#     <starttime>2020-12-16T17:17:00Z</starttime>
#   </incident>


# function to calculate vehicle impact
def get_vehicle_impact(description):
    vehicle_impact = 'all-lanes-open'
    if 'lane closed' in description.lower():
        vehicle_impact = 'some-lanes-closed'
    return vehicle_impact


# function to parse polyline to geometry line string
def parse_polyline(polylinestring):
    if not polylinestring or type(polylinestring) != str:
        return None
    # polyline rightnow is a list which has an empty string in it.
    polyline = polylinestring.split(',')
    coordinates = []
    for i in range(0, len(polyline)-1, 2):
        try:
            coordinates.append([float(polyline[i + 1]), float(polyline[i])])
        except ValueError as e:
            logging.warning('failed to parse polyline!')
            return []
    return coordinates


# function to get road direction by using geometry coordinates
def get_road_direction(coordinates):
    if not coordinates:
        return None
    try:
        long_dif = coordinates[-1][0] - coordinates[0][0]
        lat_dif = coordinates[-1][1] - coordinates[0][1]
    except ValueError as e:
        raise RuntimeError('Failed to get road direction.') from e

    if abs(long_dif) > abs(lat_dif):
        if long_dif > 0:
            direction = 'eastbound'
        else:
            direction = 'westbound'
    elif lat_dif > 0:
        direction = 'northbound'
    else:
        direction = 'southbound'

    if lat_dif == 0 and long_dif == 0:
        direction = None

    return direction

# function to parse direction from street name


def parse_direction_from_street_name(street):
    if not street or type(street) != str:
        return None
    street_char = street[-1]
    street_chars = street[-2:]
    if street_char == 'N' or street_chars == 'NB':
        direction = 'northbound'
    elif street_char == 'S' or street_chars == 'SB':
        direction = 'southbound'
    elif street_char == 'W' or street_chars == 'WB':
        direction = 'westbound'
    elif street_char == 'E' or street_chars == 'EB':
        direction = 'eastbound'
    else:
        direction = None

    return direction


# function to get event status
def get_event_status(start_time_string, end_time_string):
    start_time = datetime.strptime(start_time_string, "%Y-%m-%dT%H:%M:%SZ")

    event_status = "active"
    if datetime.now() < start_time:
        event_status = "planned"  # if < 2 to 3 weeks make it pending instead of planned
    elif end_time_string:
        end_time = datetime.strptime(end_time_string, "%Y-%m-%dT%H:%M:%SZ")

        if end_time < datetime.now():
            event_status = "completed"
    return event_status

# function to get description


def create_description(incident):
    description = incident.get('description')

    if incident.get('sensor'):
        description += '\n sensors: '
        for sensor in incident.get('sensor'):
            if not isinstance(sensor, str):
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)
            else:
                sensor = incident.get('sensor')
                if sensor['@type'] == 'iCone':
                    description += '\n' + \
                        json.dumps(parse_icone_sensor(sensor), indent=2)

    if incident.get('display'):
        description += '\n displays: '
        for display in incident.get('display'):
            if not isinstance(display, str):
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal
            else:
                display = incident.get('display')
                if display['@type'] == 'PCMS':
                    description += '\n' + json.dumps(parse_pcms_sensor(display),
                                                     indent=2)  # add baton,ab,truck beacon,ipin,signal

    return description


def parse_icone_sensor(sensor):
    icone = {}
    icone['type'] = sensor.get('@type')
    icone['id'] = sensor.get('@id')
    icone['location'] = [float(sensor.get('@latitude')),
                         float(sensor.get('@longitude'))]

    if sensor.get('radar', None):
        avg_speed = 0
        std_dev_speed = 0
        num_reads = 0
        for radar in sensor.get('radar'):
            timestamp = ''
            if not isinstance(radar, str):
                curr_reads = int(radar.get('@numReads'))
                if curr_reads == 0:
                    continue
                curr_avg_speed = float(radar.get('@avgSpeed'))
                curr_dev_speed = float(radar.get('@stDevSpeed'))
                total_num_reads = num_reads + curr_reads
                avg_speed = (avg_speed * num_reads +
                             curr_avg_speed * curr_reads) / total_num_reads
                std_dev_speed = (std_dev_speed * num_reads +
                                 curr_dev_speed * curr_reads) / total_num_reads
                num_reads = total_num_reads
                timestamp = radar.get('@intervalEnd')
            else:
                radar = sensor.get('radar')
                avg_speed = float(radar.get('@avgSpeed'))
                std_dev_speed = float(radar.get('@stDevSpeed'))
                timestamp = radar.get('@intervalEnd')

        radar = {}

        radar['average_speed'] = round(avg_speed, 2)
        radar['std_dev_speed'] = round(std_dev_speed, 2)
        radar['timestamp'] = timestamp
        icone['radar'] = radar
    return icone


def parse_pcms_sensor(sensor):
    pcms = {}
    pcms['type'] = sensor.get('@type')
    pcms['id'] = sensor.get('@id')
    pcms['timestamp'] = sensor.get('@id')
    pcms['location'] = [float(sensor.get('@latitude')),
                        float(sensor.get('@longitude'))]
    if sensor.get('message', None):
        pcms['messages'] = []
        for message in sensor.get('message'):
            if not isinstance(message, str):
                pcms['timestamp'] = message.get('@verified')
                if message.get('@text') not in pcms.get('messages'):
                    pcms.get('messages').append(message.get('@text'))
            else:
                message = sensor.get('message')
                pcms['timestamp'] = message.get('@verified')
                if message['@text'] not in pcms.get('messages'):
                    pcms.get('messages').append(message.get('@text'))
    return pcms


# Parse Icone Incident to WZDx
def parse_incident(incident, callback_function=None):
    if not validate_incident(incident):
        if callback_function:  # Note :a call back fucnction , which will trigger every time the invalid data is given
            callback_function(incident)
        return None
    geometry = {}
    geometry['type'] = "LineString"
    geometry['coordinates'] = parse_polyline(
        incident.get('location').get('polyline'))
    properties = {}

    # I included a skeleton of the message, fill out all required fields and as many optional fields as you can. Below is a link to the spec page for a road event
    # https://github.com/usdot-jpo-ode/jpo-wzdx/blob/master/spec-content/objects/RoadEvent.md

    # id
    # Leave this empty, it will be populated by add_ids
    properties['road_event_id'] = ''

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # data_source_id
    # Leave this empty, it will be populated by add_ids
    properties['data_source_id'] = ''

    # start_date
    properties['start_date'] = incident.get('starttime')

    # end_date
    properties['end_date'] = incident.get('endtime', '')

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    road_names = [incident.get('location').get('street')]
    properties['road_names'] = road_names

    # direction
    direction = parse_direction_from_street_name(road_names)

    if not direction:
        direction = get_road_direction(geometry.get('coordinates'))
    if not direction:
        
        properties['direction'] = direction

    # vehicle impact

    properties['vehicle_impact'] = get_vehicle_impact(
        incident.get('description'))

    # Relationship
    properties['relationship'] = {}

    # lanes
    properties['lanes'] = []

    # beginning_cross_street
    properties['beginning_cross_street'] = ""

    # beginning_cross_street
    properties['ending_cross_street'] = ""

    # event status
    properties['event_status'] = get_event_status(
        incident.get('starttime'), incident.get('endtime'))

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    properties['types_of_work'] = []

    # restrictions
    properties['restrictions'] = []

    # description
    properties['description'] = create_description(incident)

    # creation_date
    properties['creation_date'] = incident.get('creationtime')

    # update_date
    properties['update_date'] = incident.get('updatetime')

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry'] = geometry

    return feature

# function to validate the incident


def validate_incident(incident):

    if not incident or (type(incident) != dict and type(incident) != OrderedDict):
        logging.warning('incident is empty or has invalid type')
        return False

    location = incident.get('location')
    if not location:
        logging.warning(
            f'Invalid incident with id = {incident.get("@id")}. Location object not present')
        return False

    polyline = location.get('polyline')
    coords = parse_polyline(polyline)
    street = location.get('street', '')

    starttime = incident.get('starttime')
    description = incident.get('description')
    creationtime = incident.get('creationtime')
    updatetime = incident.get('updatetime')
    direction = parse_direction_from_street_name(street)
    if not direction:
        direction = get_road_direction(coords)
        if not direction:
            logging.warning(
                f'Invalid incident with id = {incident.get("@id")}.unable to parse direction from street name or polyline')
            return False
    required_fields = [location, polyline, coords, street,
                       starttime, description, creationtime, updatetime, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'Invalid incident with id = {incident.get("@id")}. Not all required fields are present')
            return False

    try:
        datetime.strptime(incident.get('starttime'), "%Y-%m-%dT%H:%M:%SZ")
        if incident.get('endtime'):
            datetime.strptime(incident.get('endtime'), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        logging.warning(
            f'Invalid incident with id = {incident.get("@id")}. Invalid date time format')
        return False

    return True


if __name__ == "__main__":
    main()
