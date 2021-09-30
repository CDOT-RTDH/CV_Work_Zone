import argparse
import copy
import json
import logging
from collections import OrderedDict
from datetime import datetime

from wzdx.tools import array_tools, date_tools, polygon_tools, wzdx_translator

PROGRAM_NAME = 'NavJoy568Translator'
PROGRAM_VERSION = '1.0'

DEFAULT_NAVJOY_FEED_INFO_ID = '2ed141dc-b998-4f7a-8395-9ae9dc7df2f8'

STRING_DIRECTION_MAP = {'north': 'northbound', 'south': 'southbound',
                        'west': 'westbound', 'east': 'eastbound'}

REVERSED_DIRECTION_MAP = {'northbound': 'southbound', 'southbound': 'northbound',
                          'eastbound': 'westbound', 'westbound': 'eastbound'}

CORRECT_KEY_NAMES = {
    'street_name': 'streetNameFrom',
    'mile_marker_start': 'mileMarkerStart',
    'mile_marker_end': 'mileMarkerEnd',
    'directions_of_traffic': 'directionOfTraffic',
    'current_posted_speed': 'currentPostedSpeed',
    'reduced_speed_limit': 'requestedTemporarySpeed',
    'start_date': 'workStartDate',
    'end_date': 'workEndDate',
}

NUMBERED_KEY_NAMES = [
    {
        'street_name': 'streetNameFrom',
        'mile_marker_start': 'mileMarkerStart',
        'mile_marker_end': 'mileMarkerEnd',
        'directions_of_traffic': 'directionOfTraffic',
        'current_posted_speed': 'currentPostedSpeed',
        'reduced_speed_limit': 'requestedTemporarySpeed',
        'start_date': 'workStartDate',
        'end_date': 'workEndDate',
    },
    {
        'street_name': 'streetNameFrom2',
        'mile_marker_start': 'mileMarkerStart2',
        'mile_marker_end': 'mileMarkerEnd2',
        'directions_of_traffic': 'directionOfTraffic2',
        'current_posted_speed': 'currentPostedSpeed2',
        'reduced_speed_limit': 'requestedTemporarySpeed2',
        'start_date': 'workStartDate2',
        'end_date': 'workEndDate2',
    },
    {
        'street_name': 'streetNameFrom3',
        'mile_marker_start': 'mileMarkerStart3',
        'mile_marker_end': 'mileMarkerEnd3',
        'directions_of_traffic': 'directionOfTraffic3',
        'current_posted_speed': 'currentPostedSpeed3',
        'reduced_speed_limit': 'requestedTemporarySpeed3',
        'start_date': 'workStartDate3',
        'end_date': 'workEndDate3',
    },
    {
        'street_name': 'streetNameFrom4',
        'mile_marker_start': 'mileMarkerStart4',
        'mile_marker_end': 'mileMarkerEnd4',
        'directions_of_traffic': 'directionOfTraffic4',
        'current_posted_speed': 'currentPostedSpeed4',
        'reduced_speed_limit': 'requestedTemporarySpeed4',
        'start_date': 'workStartDate4',
        'end_date': 'workEndDate4',
    }
]


def main():
    inputfile, outputfile = parse_navjoy_arguments()
    try:
        navjoy_obj = json.loads(open(inputfile).read())
    except ValueError as e:
        raise ValueError(
            'Invalid file type. Please specify a valid Json file!') from None
    wzdx_obj = wzdx_creator(navjoy_obj)

    location_schema = 'wzdx/sample_files/validation_schema/wzdx_v3.1_feed.json'
    wzdx_schema = json.loads(open(location_schema).read())

    if not wzdx_translator.validate_wzdx(wzdx_obj, wzdx_schema):
        logging.error(
            'validation error more message are printed above. output file is not created because the message failed validation.')
        return
    with open(outputfile, 'w') as fwzdx:
        fwzdx.write(json.dumps(wzdx_obj, indent=2))
        print(
            'Your wzdx message was successfully generated and is located here: ' + str(outputfile))


# parse script command line arguments
def parse_navjoy_arguments():
    parser = argparse.ArgumentParser(
        description='Translate iCone data to WZDx')
    parser.add_argument('--version', action='version',
                        version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('navjoyFile', help='navjoy file path')
    parser.add_argument('--outputFile', required=False,
                        default='navjoy_wzdx_translated_output_message.geojson', help='output file path')

    args = parser.parse_args()
    return args.navjoyFile, args.outputFile


def wzdx_creator(messages, info=None, unsupported_message_callback=None):
    if not messages:
        return None
   # verify info obj
    if not info:
        info = wzdx_translator.initialize_info(DEFAULT_NAVJOY_FEED_INFO_ID)
    if not wzdx_translator.validate_info(info):
        return None

    wzd = wzdx_translator.initialize_wzdx_object(info)

    for message in messages:

        separated_messages = expand_speed_zone(message)
        for msg in separated_messages:
            feature = parse_reduction_zone(
                msg, callback_function=unsupported_message_callback)
            if feature:
                wzd.get('features').append(feature)

    if not wzd.get('features'):
        return None
    wzd = wzdx_translator.add_ids(wzd)
    return wzd


# take in individual message, spit out list of altered unique messages to be translated
# This function iterates over the list of NUMBERED_KEY_NAMES and correlates them to CORRECT_KEY_NAMES. For each
# set of numbered key names, generate a copy of the original message, check if the numbered keys exist, if they do
# then copy those values to the leys in CORRECT_KEY_NAMES. After, if directionOfTraffic yields more than one direction,
# generate a new message for each direction and save them with the key 'direction'

# TODO: consider deleting all numbered keys after they are copied
# TODO: consider removing duplicate messages
def expand_speed_zone(message):
    messages = []

    for key_set in NUMBERED_KEY_NAMES:
        if not message.get('data', {}).get(key_set['street_name']):
            continue
        new_message = copy.deepcopy(message)
        for key, value in key_set.items():
            new_message.get('data', {})[CORRECT_KEY_NAMES[key]] = message.get(
                'data', {}).get(value)

        directions = new_message.get('data', {}).get('directionOfTraffic')
        for direction in get_directions_from_string(directions):
            new_message_dir = copy.deepcopy(new_message)
            if new_message_dir.get('data', {}).get('directionOfTraffic'):
                del new_message_dir.get('data', {})['directionOfTraffic']
            new_message_dir.get('data', {})['direction'] = direction
            messages.append(new_message_dir)
    return messages


def get_linestring_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "LineString":
            return i


def get_polygon_index(map):
    for i in range(len(map)):
        if map[i].get("type") == "Polygon":
            return i


def get_directions_from_string(directions_string) -> list:
    if not directions_string or type(directions_string) != str:
        return []

    directions = []

    # iterate over directions and convert short direction names to WZDx enum directions
    directions_string = directions_string.strip()
    for dir in directions_string.split('/'):
        direction = STRING_DIRECTION_MAP.get(dir.lower())
        if direction:
            directions.append(direction)

    return directions


# TODO: Support additional zones per message (streetNameFrom2, ...)
# Convert individual Navjoy 658 speed reduction zone to WZDx feature
def parse_reduction_zone(obj, callback_function=None):
    if not validate_closure(obj):
        if callback_function:
            callback_function(obj)
        return None

    data = obj.get('data', {})

    map = data.get('srzmap')
    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates")
        coordinates = array_tools.get_2d_list(coordinates)
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates")
            coordinates = array_tools.get_2d_list(polygon)
            if coordinates:
                coordinates = polygon_tools.polygon_to_polyline_center(
                    coordinates)
        else:
            logging.warning(
                f"Invalid event with id = {obj.get('sys_gUid')}. No polygon or linestring")
            return None

    if not coordinates:
        logging.warning(
            f"Invalid event with id = {obj.get('sys_gUid')}. No valid coordinates found")
        return None

    direction = data.get('direction')

    # Reverse polygon if it is in the opposite direction as the message
    polyline_direction = polygon_tools.get_road_direction_from_coordinates(
        coordinates)
    if direction == REVERSED_DIRECTION_MAP.get(polyline_direction):
        coordinates.reverse()

    geometry = {}
    if len(coordinates) > 2:
        geometry['type'] = "LineString"
    else:
        geometry['type'] = "MultiPoint"

    geometry['coordinates'] = coordinates
    properties = wzdx_translator.initialize_feature_properties()

    # Event Type ['work-zone', 'detour']
    properties['event_type'] = 'work-zone'

    # start_date
    start_date = date_tools.parse_datetime_from_iso_string(
        data.get('workStartDate'))
    properties['start_date'] = date_tools.get_iso_string_from_datetime(
        start_date)

    # end_date
    end_date = date_tools.parse_datetime_from_iso_string(
        data.get('workEndDate'))
    if end_date:
        properties['end_date'] = date_tools.get_iso_string_from_datetime(
            end_date)
    else:
        properties['end_date'] = ''

    # start_date_accuracy
    properties['start_date_accuracy'] = "estimated"

    # end_date_accuracy
    properties['end_date_accuracy'] = "estimated"

    # beginning_accuracy
    properties['beginning_accuracy'] = "estimated"

    # ending_accuracy
    properties['ending_accuracy'] = "estimated"

    # road_name
    properties['road_names'] = [data.get('streetNameFrom')]

    # direction
    properties['direction'] = direction

    # vehicle impact
    properties['vehicle_impact'] = get_vehicle_impact(
        data.get('reductionJustification'))

    # event status
    properties['event_status'] = date_tools.get_event_status(
        start_date, end_date)

    # type_of_work
    # maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation
    projectDescription = data.get('descriptionForProject')
    types_of_work = get_types_of_work(projectDescription)
    if types_of_work:
        properties['types_of_work'] = types_of_work

    # reduced_speed_limit
    properties['reduced_speed_limit'] = wzdx_translator.string_to_number(
        data.get('requestedTemporarySpeed'))

    # description
    reductionJustification = data.get('reductionJustification')
    properties['description'] = data.get(
        'descriptionForProject', '') + '. ' + reductionJustification

    # creation_date
    properties['creation_date'] = date_tools.get_iso_string_from_datetime(
        datetime.utcnow())

    # update_date
    properties['update_date'] = date_tools.get_iso_string_from_datetime(
        datetime.utcnow())

    filtered_properties = copy.deepcopy(properties)

    for key, value in properties.items():
        if value == None and key not in ['road_event_id', 'data_source_id']:
            del filtered_properties[key]

    feature = {}
    feature['type'] = "Feature"
    feature['properties'] = filtered_properties
    feature['geometry'] = geometry

    return feature


# function to validate the alert
def validate_closure(obj):
    if not obj or (type(obj) != dict and type(obj) != OrderedDict):
        logging.warning('alert is empty or has invalid type')
        return False

    id = obj.get("sys_gUid")

    data = obj.get('data', {})
    street = data.get('streetNameFrom')

    map = data.get('srzmap', [{}])
    if type(map) != list or len(map) == 0:
        logging.warning(
            f'Invalid event with id = {id}. ConstructionWorkZonePlan object is either invalid or empty')

    # TODO: Support MultiPoint
    index = get_linestring_index(map)
    if index != None:
        coordinates = map[index].get("coordinates", [None])[0]
    else:
        index = get_polygon_index(map)
        if index != None:
            polygon = map[index].get("coordinates", [None])[0]
            coordinates = polygon_tools.polygon_to_polyline_center(polygon)
        else:
            logging.warning(
                f"Invalid event with id = {id}. No LineString or Polygon found")
            return False

    if not coordinates:
        logging.warning(
            f"Invalid event with id = {obj.get('sys_gUid')}. No valid coordinates found")
        return False

    starttime_string = data.get('workStartDate')
    endtime_string = data.get('workEndDate')
    description = data.get('descriptionForProject')
    direction = data.get('direction')

    required_fields = [street, starttime_string, description, direction]
    for field in required_fields:
        if not field:
            logging.warning(
                f'''Invalid event with id = {id}. not all required fields are present. Required fields are: 
                streetNameFrom, workStartDate, and descriptionForProject''')
            return False

    start_time = date_tools.parse_datetime_from_iso_string(starttime_string)
    end_time = date_tools.parse_datetime_from_iso_string(endtime_string)
    if not start_time:
        logging.error(
            f'Invalid incident with id = {id}. Unsupported start time format: {start_time}')
        return False
    elif endtime_string and not end_time:
        logging.error(
            f'Invalid incident with id = {id}. Unsupported end time format: {end_time}')
        return False

    return True


# function to calculate vehicle impact
def get_vehicle_impact(travelRestriction):
    if not travelRestriction or type(travelRestriction) != str:
        return None
    travelRestriction = travelRestriction.lower()
    vehicle_impact = 'all-lanes-open'
    if 'lane closure' in travelRestriction.lower():
        vehicle_impact = 'some-lanes-closed'
    elif 'all lanes closed' in travelRestriction.lower():
        vehicle_impact = 'all-lanes-closed'

    return vehicle_impact


# TODO: Support more types of work
def get_types_of_work(field):
    if not field or type(field) != str:
        return None
    field = field.lower()
    # valid_types_of_work = ['maintenance',
    #                        'minor-road-defect-repair',
    #                        'roadside-work',
    #                        'overhead-work',
    #                        'below-road-work',
    #                        'barrier-work',
    #                        'surface-work',
    #                        'painting',
    #                        'roadway-relocation',
    #                        'roadway-creation']

    if not field or type(field) != str:
        return []

    types_of_work = []

    if 'crack seal' in field:
        types_of_work.append({'type_name': 'minor-road-defect-repair',
                              'is_architectural_change': False})
    if 'restriping' in field:
        types_of_work.append({'type_name': 'painting',
                              'is_architectural_change': False})
    if 'repaving' in field:
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': False})
    if 'bridge' in field:
        types_of_work.append({'type_name': 'below-road-work',
                              'is_architectural_change': False})
    if 'traffic signal' in field:
        types_of_work.append({'type_name': 'overhead-work',
                              'is_architectural_change': False})
    if 'lane expansion' in field:
        types_of_work.append({'type_name': 'surface-work',
                              'is_architectural_change': True})

    return types_of_work


if __name__ == "__main__":
    main()
