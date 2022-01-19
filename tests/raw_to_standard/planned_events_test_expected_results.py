test_expand_speed_zone_1_expected = [
    {
        "properties": {
            "laneImpacts": [
                {
                    "direction": "eastbound",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                }
            ],
            "direction": "eastbound"
        }
    },
    {
        "properties": {
            "laneImpacts": [
                {
                    "direction": "westbound",
                    "laneCount": 2,
                    "laneClosures": "0",
                    "closedLaneTypes": []
                }
            ],
            "direction": "westbound"
        }
    }
]
[{'properties': {'laneImpacts': [{'direction': 'eastbound', 'laneCount': 2, 'laneClosures': '6000', 'closedLaneTypes': ['left lane', 'right lane']}, {'direction': 'west', 'laneCount': 2, 'laneClosures': '0', 'closedLaneTypes': []}], 'direction': 'eastbound'}, 'laneImpacts': [{'direction': 'eastbound', 'laneCount': 2, 'laneClosures': '6000', 'closedLaneTypes': ['left lane', 'right lane']}]},
    {'properties': {'laneImpacts': [{'direction': 'east', 'laneCount': 2, 'laneClosures': '6000', 'closedLaneTypes': ['left lane', 'right lane']}, {'direction': 'westbound', 'laneCount': 2, 'laneClosures': '0', 'closedLaneTypes': []}], 'direction': 'westbound'}, 'laneImpacts': [{'direction': 'westbound', 'laneCount': 2, 'laneClosures': '0', 'closedLaneTypes': []}]}]

test_expand_speed_zone_2_expected = [{
    "type": "Feature",
    "geometry": {
            "srid": 4326,
            "type": "MultiPoint",
            "coordinates": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ]
    },
    "properties": {
        "clearTime": "2022-05-01T18:26:04.000+00:00",
        "startMarker": 50.0,
        "type": "Bridge Construction",
        "laneImpacts": [
                {
                    "direction": "eastbound",
                    "laneCount": 2,
                    "laneClosures": "6000",
                    "closedLaneTypes": [
                        "left lane",
                        "right lane"
                    ]
                }
        ],
        "routeName": "I-70E",
        "isOversizedLoadsProhibited": True,
        "lastUpdated": "2021-10-29T18:35:01.835+00:00",
        "schedule": [
            {
                "startTime": "2021-10-29T18:26:04.000Z",
                "endTime": "2022-05-01T18:26:04.000Z"
            }
        ],
        "endMarker": 60.0,
        "startTime": "2021-10-29T18:26:04.000+00:00",
        "id": "OpenTMS-Event1689408506",
        "travelerInformationMessage": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
        "direction": "eastbound"
    },
    "attributes": {}
}]


test_generate_standard_messages_from_string_expected = [
    {
        "rtdh_timestamp": 1639062865.0398643,
        "rtdh_message_id": "we234de",
        "event": {
            "type": 'work-zone',
            "types_of_work": [
                {
                    "type_name": "below-road-work",
                    "is_architectural_change": True
                }
            ],
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "eastbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "closed"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [{'type': 'permitted-oversize-loads-prohibited'}],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0
            }
        }
    },
    {
        "rtdh_timestamp": 1639062865.0398643,
        "rtdh_message_id": "23wsg54h",
        "event": {
            "type": 'work-zone',
            "types_of_work": [
                {
                    "type_name": "below-road-work",
                    "is_architectural_change": True
                }
            ],
            "source": {
                "id": "OpenTMS-Event1689408506",
                "creation_timestamp": 1635531964000,
                "last_updated_timestamp": 1635532501835
            },
            "geometry": [
                [
                    -108.279106,
                    39.195663
                ],
                [
                    -108.218549,
                    39.302392
                ]
            ],
            "header": {
                "description": "Between Exit 49: CO 65; Grand Mesa (5 miles east of the Palisade area) and US 6 (Debeque) from Mile Point 50 to Mile Point 60. Road closed expect delays due to bridge construction. Until May 1, 2022 at about 12:26PM MDT.",
                "start_timestamp": 1635531964000,
                "end_timestamp": 1651429564000
            },
            "detail": {
                "road_name": "I-70E",
                "road_number": "I-70E",
                "direction": "westbound"
            },
            "additional_info": {
                "lanes": [
                    {
                        "order": 1,
                        "type": "shoulder",
                        "status": "open"
                    },
                    {
                        "order": 2,
                        "type": "general",
                        "status": "open"
                    },
                    {
                        "order": 3,
                        "type": "general",
                        "status": "open"
                    },
                    {
                        "order": 4,
                        "type": "shoulder",
                        "status": "open"
                    }
                ],
                "restrictions": [{'type': 'permitted-oversize-loads-prohibited'}],
                "beginning_milepost": 50.0,
                "ending_milepost": 60.0
            }
        }
    }
]
