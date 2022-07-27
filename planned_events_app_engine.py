#!/usr/bin/env python

# Copyright 2020 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

from google.cloud import datastore, bigquery
import settings
import logging
import flask
import datetime
from wzdx.tools import cdot_geospatial_api
from wzdx.combination import attenuator
import json

app = flask.Flask(__name__)

# Set Logging Object and Functionality
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
l = logging.getLogger(__name__)


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
GEOTAB_AUTOMATED_ATTENUATOR_IDS = settings.GEOTAB_AUTOMATED_ATTENUATOR_IDS.split(
    ';')
# General Variables
# d0c2feba6d38df6fdd284d370cbd69636f337d48

_datastore_client = datastore.Client(project='cdot-rtdh-prod')
_bigquery_client = bigquery.Client(project=f'cdot-adap-prod')
try:
    QUERY_INTERVAL_MINUTES = int(settings.QUERY_INTERVAL_MINUTES)
except:
    QUERY_INTERVAL_MINUTES = 5


#######################
# METHODS
#######################


def get_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CachePlannedEventsStandard')
    resp = query.fetch()
    resp = list(resp)
    return resp


def get_incidents():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheIncidentsStandard')
    resp = query.fetch()
    resp = list(resp)
    return resp


def get_current_planned_events():
    query = _datastore_client.query(
        namespace='rtdh_cache_latest', kind='RTDHCache')
    query.add_filter('label', '=', 'CacheWZDxPlannedEventsStandard')
    query.add_filter('condition_1', '=', True)
    # query.add_filter('timestamp', '>', datetime.datetime.utcnow(
    # ) - datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES))

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
    now = datetime.datetime.utcnow()
    start = now
    if now.hour == 0 and now.minute < QUERY_INTERVAL_MINUTES:
        start1 = now - \
            datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES)
        end1 = start1.replace(minute=59, second=59, microsecond=99999)
        start2 = now.replace(minute=0, second=0, microsecond=0)
        end2 = now
        queries.append({'year': start1.year, 'month': start1.month, 'day': start1.day, 'startTimestamp': start1.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end1.strftime(ISO_8601_FORMAT_STRING)})
        queries.append({'year': start2.year, 'month': start2.month, 'day': start2.day, 'startTimestamp': start2.strftime(
            ISO_8601_FORMAT_STRING), 'endTimestamp': end2.strftime(ISO_8601_FORMAT_STRING)})
    else:
        start = now - \
            datetime.timedelta(minutes=QUERY_INTERVAL_MINUTES)
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
    l.debug(query_str)
    return query_str


def get_query_results(query_str):
    query_job = _bigquery_client.query(query_str)
    return list(query_job)


def get_recent_geotab(attenuator_ids):
    query_str = create_geotab_query(attenuator_ids)
    return [{'avl_location': i['avl_location'], 'rtdh_message_id': i['rtdh_message_id'], 'rtdh_timestamp': i['rtdh_timestamp'].strftime(ISO_8601_FORMAT_STRING)} for i in get_query_results(query_str)]

# Write API GET request response to PubSub topic


#######################
# Main Control Flow
#######################
# @app.route('/cron/wzdx-planned-events', methods=['GET'])
def main():
    # Prevent executions outside of App Engine Cron.
    # if flask.request.headers.get('X-AppEngine-Cron') != 'true':
    #     flask.abort(400)

    # l.info("Setting Environment Variables...")
    # l.info(f"Environment Variable: Project = {settings.PROJECT}")
    # l.info(f"Environment Variable: Region = {settings.REGION}")
    # l.info(f"Environment Variable: Raw Topic ID = {settings.TOPIC}")

    # request_timestamp = (flask.request.date
    #                      if flask.request.date is not None
    #                      else datetime.datetime.now(datetime.timezone.utc))

    # recent_planned_events = get_planned_events()
    # l.info(f"Grabbed planned events: {len(recent_planned_events)}")
    # wzdx_planned_events = get_wzdx_planned_events()
    # l.info(f"Grabbed WZDx planned events: {len(wzdx_planned_events)}")

    # entries = get_updated_planned_events(
    #     recent_planned_events, wzdx_planned_events)
    # entries += get_recent_incidents()

    # with open(f'planned_events_app_engine{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
    #     f.write(json.dumps(json.loads(entries, indent=2, default=str)))

    # blob_name = '{}/{}/{}.xml'.format(
    #     'wzdx_planned_events',
    #     request_timestamp.strftime('year=%Y/month=%m/day=%d/time=%H:%M:%SZ'),
    #     uuid.uuid4())
    # upload_blob(settings.BUCKET, blob_name, json.dumps(entries, default=str))
    # l.info(f"Upload raw data to GCS.")

    # write_raw_pubsub(entries)

    l.info(f"Open TMS Planned Events API Called at: {request_timestamp}")

    # return ((f"Open TMS Planned Events API Called - Data Written to PubSub. {request_timestamp}"), 200)


def geotab():

    # now = datetime.datetime.now()
    # with open(f'testing_results/planned_events_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
    #     f.write(json.dumps(get_planned_events(), indent=2, default=str))
    # return
    planned_events = [
        {
            "road_event_feed_info": {
                "feed_info_id": "49253be7-0c6a-4a65-8113-450f9041f989",
                "update_date": "2022-07-27T16:36:55Z",
                "publisher": "CDOT",
                "contact_name": "Ashley Nylen",
                "contact_email": "ashley.nylen@state.co.us",
                "version": "4.0",
                "license": "https://creativecommons.org/publicdomain/zero/1.0/",
                "data_sources": [
                    {
                        "data_source_id": "15c4cc92-658c-4a58-ba08-dc6d36a0631b",
                        "feed_info_id": "49253be7-0c6a-4a65-8113-450f9041f989",
                        "organization_name": "CDOT",
                        "contact_name": "Ashley Nylen",
                        "contact_email": "ashley.nylen@state.co.us",
                        "update_date": "2022-07-27T16:36:55Z",
                        "location_method": "channel-device-method",
                        "lrs_type": "lrs_type"
                    }
                ]
            },
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "road_event_id": None,
                        "data_source_id": None,
                        "core_details": {
                            "event_type": "work-zone",
                            "data_source_id": "15c4cc92-658c-4a58-ba08-dc6d36a0631b",
                            "road_names": [
                                "CO-159"
                            ],
                            "direction": "southbound",
                            "relationship": {},
                            "description": "Between West Jasper Drive (near San Luis) and County Road P7 (1 mile south of the San Luis area) from Mile Point 20 to Mile Point 14. Striping operations. Until today at about 3:11PM MDT.",
                            "update_date": "2022-07-27T14:22:31Z",
                            "road_event_id": "8d2c0b62-8d02-4bf4-9510-0614d93ce963"
                        },
                        "start_date": "2022-07-27T14:20:00Z",
                        "end_date": "2022-07-27T21:11:00Z",
                        "start_date_accuracy": "estimated",
                        "end_date_accuracy": "estimated",
                        "beginning_accuracy": "estimated",
                        "ending_accuracy": "estimated",
                        "location_method": "channel-device-method",
                        "vehicle_impact": "all-lanes-open",
                        "lanes": [
                            {
                                "order": 1,
                                "type": "general",
                                "status": "open"
                            }
                        ],
                        "event_status": "completed",
                        "types_of_work": [
                            {
                                "type_name": "painting",
                                "is_architectural_change": True
                            }
                        ],
                        "beginning_milepost": 14.0,
                        "ending_milepost": 20.0
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [
                                -105.491141,
                                37.190608
                            ],
                            [
                                -105.42735,
                                37.228158
                            ]
                        ]
                    },
                    "id": "OpenTMS-Event4707772849_southbound"
                }
            ]
        }
    ]

    now = datetime.datetime.now()
    geotab_msgs = get_recent_geotab(GEOTAB_AUTOMATED_ATTENUATOR_IDS)
    l.info(f"Grabbed attenuator messages: {len(geotab_msgs)}")
    with open(f'testing_results/geotab/geotab_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
        f.write(json.dumps(geotab_msgs, indent=2, default=str))
    if geotab_msgs:
        # planned_events = get_current_planned_events()
        with open(f'testing_results/planned_events/planned_events_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
            f.write(json.dumps(planned_events, indent=2, default=str))
        l.info(f"Grabbed planned events wzdx messages: {len(planned_events)}")
        combined_events = attenuator.get_combined_events(
            geotab_msgs, planned_events)
        l.info(f"Generated combined events: {len(combined_events)}")

        with open(f'testing_results/combined_events/combined_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w+', newline='') as f:
            f.write(json.dumps(combined_events, indent=2, default=str))


if __name__ == "__main__":
    # main()
    geotab()
    # app.run(debug=True)
