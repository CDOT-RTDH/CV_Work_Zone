import json
from datetime import datetime, timedelta
from wzdx.tools import cdot_geospatial_api, date_tools
from operator import itemgetter
from google.cloud import datastore, bigquery
import pandas
import logging

_datastore_client = datastore.Client(project='cdot-rtdh-test')
_bigquery_client = bigquery.Client(project=f'cdot-adap-dev')

ATTENUATOR_TIME_AHEAD_SECONDS = 30 * 60
ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
QUERY_INTERVAL_MINUTES = 30
ATMA_IDS = ['G9NSJ6703F6J']


def get_current_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    query.add_filter('condition_1', '=', True)
    # query.add_filter('timestamp', '>', datetime.utcnow(
    # ) - timedelta(minutes=QUERY_INTERVAL_MINUTES))

    resp = query.fetch()
    resp = list(resp)
    return [json.loads(i['value']) for i in resp]


def get_route_info_planned_event(planned_event):
    start = cdot_geospatial_api.get_route_and_measure(
        planned_event['geometry']['coordinates'][0])
    end = cdot_geospatial_api.get_route_and_measure(
        planned_event['geometry']['coordinates'][1])
    if start['Route'] != end['Route'] or start['Measure'] == end['Measure']:
        return None
    else:
        return {
            'route': start['Route'],
            'start_measure': start['Measure'],
            'end_measure': end['Measure']
        }


def get_route_info_geotab(geotab):
    start = cdot_geospatial_api.get_route_and_measure(
        geotab['geometry']['coordinates'][0])
    end = cdot_geospatial_api.get_route_and_measure(
        geotab['geometry']['coordinates'][1])
    if start['Route'] != end['Route'] or start['Measure'] == end['Measure']:
        return None
    else:
        return {
            'route': start['Route'],
            'start_measure': start['Measure'],
            'end_measure': end['Measure']
        }


def create_geotab_query(attenuator_ids):
    queries = []
    now = datetime.utcnow()
    start = now
    if now.hour == 0 and now.minute < QUERY_INTERVAL_MINUTES:
        start1 = now - \
            timedelta(minutes=QUERY_INTERVAL_MINUTES)
        end1 = start1.replace(minute=59, second=59, microsecond=99999)
        start2 = now.replace(minute=0, second=0, microsecond=0)
        end2 = now
        queries.append({'year': start1.year, 'month': start1.month, 'day': start1.day, 'startTimestamp': start1.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end1.strftime(ISO_8601_FORMAT_STRING)})
        queries.append({'year': start2.year, 'month': start2.month, 'day': start2.day, 'startTimestamp': start2.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end2.strftime(ISO_8601_FORMAT_STRING)})
    else:
        start = now - \
            timedelta(minutes=QUERY_INTERVAL_MINUTES)
        queries.append({'year': now.year, 'month': now.month, 'day': now.day, 'startTimestamp': start.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': now.strftime(ISO_8601_FORMAT_STRING)})
    query_where_format = '(year = {year} and month = {month} and day = {day} and rtdh_timestamp BETWEEN TIMESTAMP("{startTimestamp}") and TIMESTAMP("{endTimestamp}"))'
    query_where = ' or '.join([query_where_format.format(
        **query_params) for query_params in queries])
    query_ids = ' or '.join(
        [f'avl_location.vehicle.id2 = "{id}"' for id in attenuator_ids])
    query_str = f'''
        SELECT *
        FROM `cdot-adap-prod.raw_from_rtdh_standard.geotab_avl_standard_v3` 
        where ({query_where}) 
        and ({query_ids})
    '''
    return query_str


def get_query_results(query_str):
    print(query_str)
    query_job = _bigquery_client.query(query_str)
    return list(query_job)


def get_recent_geotab(attenuator_ids):
    query_str = create_geotab_query(attenuator_ids)
    return [{'avl_location': i['avl_location'], 'rtdh_message_id': i['rtdh_message_id'], 'rtdh_timestamp': i['rtdh_timestamp'].strftime(ISO_8601_FORMAT_STRING)}
            for i in get_query_results(query_str)]


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime)):
        return obj.strftime(ISO_8601_FORMAT_STRING)
    raise TypeError("Type %s not serializable" % type(obj))


def main():

    geotab_msgs = get_recent_geotab(ATMA_IDS)
    print("writing to geotab")
    with open('./wzdx/sample_files/raw/geotab_avl/geotab_all_2.json', 'w+') as f:
        f.write(json.dumps(geotab_msgs, default=json_serial))
    # planned_events = get_current_planned_events()
    # print("writing to planned_events")
    # with open('./wzdx/sample_files/enhanced/planned_events/planned_event_all.json', 'w+') as f:
    #     f.write(json.dumps(planned_events, default=json_serial))

    # with open('./wzdx/sample_files/raw/geotab_avl/geotab_all.json') as f:
    #     geotab_avl = json.loads(f.read())
    # with open('./wzdx/sample_files/enhanced/planned_events/planned_event_all.json') as f:
    #     planned_event = json.loads(f.read())
    # combined_events = get_combined_events(geotab_avl, planned_event)
    # with open('./wzdx/sample_files/enhanced/planned_events/planned_event_combined.json', 'w+') as f:
    #     f.write(json.dumps(combined_events, indent='  '))

    # planned_event_wzdx_feature = planned_event['features'][0]


def get_combined_events(gebtab_msgs, planned_events):
    conmbined_events = []
    for i in identify_overlapping_features(gebtab_msgs, planned_events):
        feature = combine_geotab_with_planned_event(*i)
        wzdx = i[1]
        wzdx['features'] = [feature]
        conmbined_events.append(wzdx)
    return conmbined_events


def identify_overlapping_features(gebtab_msgs, planned_events):
    geotab_routes = {}
    matching_routes = []

    for gebtab_msg in gebtab_msgs:
        # assume 1 feture per wzdx planned_event
        geometry = gebtab_msg['avl_location']['position']
        gebtab_msg = add_route(
            gebtab_msg, geometry['latitude'], geometry['longitude'])
        geotab_route_details = cdot_geospatial_api.get_route_and_measure(
            (geometry['latitude'], geometry['longitude']))
        if not geotab_route_details:
            logging.info(
                f"No geotab route info for {gebtab_msg['rtdh_message_id']}")
            continue
        if geotab_route_details['Route'] in geotab_routes:
            geotab_routes[geotab_route_details['Route']].append(gebtab_msg)
        else:
            geotab_routes[geotab_route_details['Route']] = [gebtab_msg]

    if not geotab_routes:
        return []
    for planned_event in planned_events:
        # assume 1 feture per wzdx planned_event
        coordinates = planned_event['features'][0]['geometry']['coordinates']
        planned_event = add_route(
            planned_event, coordinates[0][1], coordinates[0][0], 'route_details_start')

        matching_geotab_routes = geotab_routes.get(
            planned_event['route_details_start']['Route'], [])
        if matching_geotab_routes:
            logging.info(
                f"FOUND MATCHING ROUTE FOR {planned_event['features'][0]['id']}")

            planned_event = add_route(
                planned_event, coordinates[-1][1], coordinates[-1][0], 'route_details_end')
            if (planned_event['route_details_start']['Route'] != planned_event['route_details_end']['Route']):
                continue

            for geotab in matching_geotab_routes:
                logging.debug("Mile markers. geotab: {}, planned_event start: {}, planned_event_end: {}".format(
                    geotab['route_details']['Measure'], planned_event['route_details_start']['Measure'], planned_event['route_details_end']['Measure']))
                if planned_event['route_details_start']['Measure'] >= geotab['route_details']['Measure'] and planned_event['route_details_end']['Measure'] <= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, planned_event))
                    return matching_routes
                    break
                elif planned_event['route_details_start']['Measure'] <= geotab['route_details']['Measure'] and planned_event['route_details_end']['Measure'] >= geotab['route_details']['Measure']:
                    matching_routes.append((geotab, planned_event))
                    return matching_routes
                    break

    return matching_routes


def add_route(obj, lat, lng, name='route_details'):
    route_details = cdot_geospatial_api.get_route_and_measure((lat, lng))
    obj[name] = route_details
    return obj


def combine_geotab_with_planned_event(geotab_avl, planned_event_wzdx):
    planned_event_wzdx_feature = planned_event_wzdx['features'][0]
    speed = geotab_avl['avl_location']['position']['speed']
    bearing = geotab_avl['avl_location']['position']['bearing']
    route_details = geotab_avl['route_details']
    distance_ahead = get_distance_ahead(speed, ATTENUATOR_TIME_AHEAD_SECONDS)
    combined_event = combine_with_planned_event(
        planned_event_wzdx_feature,
        route_details,
        distance_ahead,
        bearing,
        planned_event_wzdx['route_details_start']['Measure'],
        planned_event_wzdx['route_details_end']['Measure'])

    for i in ['route_details', 'route_details_start', 'route_details_end']:
        if i in combined_event:
            del combined_event[i]
    return combined_event


def combine_with_planned_event(planned_event_wzdx_feature, route_details, distance_ahead, bearing, event_start_marker, event_end_marker):
    startMarker = min(max(
        route_details['Measure'], event_start_marker), event_end_marker)
    endMarker = max(min(
        route_details['Measure'] + distance_ahead, event_end_marker), event_start_marker)
    modified_distance_ahead = endMarker - startMarker
    print(startMarker, endMarker, modified_distance_ahead)
    geometry = get_geometry_for_distance_ahead(
        modified_distance_ahead, route_details, bearing)
    planned_event_wzdx_feature['properties']['beginning_milepost'] = startMarker
    planned_event_wzdx_feature['properties']['ending_milepost'] = endMarker
    planned_event_wzdx_feature['geometry']['coordinates'] = geometry

    return planned_event_wzdx_feature


def get_geometry_for_distance_ahead(distance_ahead, route_details, bearing):
    route_ahead = cdot_geospatial_api.get_route_geometry_ahead(
        route_details['Route'], route_details['Measure'], bearing, distance_ahead, routeDetails=route_details)
    return route_ahead['coordinates']


# Speed in mph, time in seconds
def get_distance_ahead(speed, time):
    speed = max(speed, 10)
    return speed * time / 3600


if __name__ == "__main__":
    main()
