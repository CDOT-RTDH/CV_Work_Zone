
import xmltodict
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import uuid
import random
import string


# Translator for icone
def wzdx_creator(messages, info):
    wzd = {}
    wzd['road_event_feed_info'] = {}
    # hardcode
    wzd['road_event_feed_info']['feed_info_id'] = info['feed_info_id']
    wzd['road_event_feed_info']['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    wzd['road_event_feed_info']['publisher'] = 'CDOT '
    wzd['road_event_feed_info']['contact_name'] = 'Abinash Konersman'
    wzd['road_event_feed_info']['contact_email'] = 'abinash.konersman@state.co.us'
    if info['metadata'].get('datafeed_frequency_update', False):
        wzd['road_event_feed_info']['update_frequency'] = info['metadata'][
            'datafeed_frequency_update']  # Verify data type
    wzd['road_event_feed_info']['version'] = '3.0'


    data_source = {}
    data_source['data_source_id'] = str(uuid.uuid4())
    data_source['feed_info_id'] = info['feed_info_id']
    data_source['organization_name'] = info['metadata']['issuing_organization']
    data_source['contact_name'] = info['metadata']['contact_name']
    data_source['contact_email'] = info['metadata']['contact_email']
    if info['metadata'].get('datafeed_frequency_update', False):
        data_source['update_frequency'] = info['metadata']['datafeed_frequency_update']
    data_source['update_date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data_source['location_verify_method'] = info['metadata']['location_verify_method']
    data_source['location_method'] = info['metadata']['wz_location_method']
    data_source['lrs_type'] = info['metadata']['lrs_type']
    # data_source['lrs_url'] = "basic url"

    wzd['road_event_feed_info'] ['data_sources'] = [data_source]
    wzd['type'] = 'FeatureCollection'
    nodes = []
    sub_identifier = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in
                             range(6))  # Create random 6 character digit/letter string
    road_event_id = str(uuid.uuid4())
    ids = {}
    ids['sub_identifier'] = sub_identifier
    ids['road_event_id'] = road_event_id

    wzd['features'] = []
    print(messages)
    print("")
    print("")
    print("")
    print("")
    print("")
    for incident in messages['incidents']['incident']:
        print(incident)
        print("")
        print("")
        # Parse Incident to WZDx Feature
        wzd['features'].append(parse_incident(incident))

        wzd = add_ids(wzd, True)
        return wzd

    #################### Sample Incident Xml format from icone data####################
    #   <incident id="U13631714_202012161717">
    #     <creationtime>2020-12-16T17:17:00Z</creationtime>
    #     <updatetime>2020-12-16T17:47:00Z</updatetime>
    #     <type>CONSTRUCTION</type>
    #     <description>Roadwork - Lane Closed, MERGE LEFT [iCone]</description>
    #     <location>
    #       <direction>ONE_DIRECTION</direction>
    #       <polyline>28.8060608,-96.9916512,28.8060608,-96.9916512</polyline>
    #     </location>
    #     <starttime>2020-12-16T17:17:00Z</starttime>
    #   </incident>

    # Parse Icone Incident to WZDx


