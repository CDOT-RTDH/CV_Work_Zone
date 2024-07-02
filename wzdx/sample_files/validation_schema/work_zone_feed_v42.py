wzdx_v42_schema_string = {
    "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/WorkZoneFeed.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "WZDx v4.2 Work Zone Feed",
    "description": "The GeoJSON output of a WZDx Work Zone Feed (v4.2)",
    "type": "object",
    "properties": {
        "feed_info": {
            "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/FeedInfo.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "WZDx Feed Information",
            "description": "Describes WZDx feed header information such as metadata, contact information, and data sources",
            "type": "object",
            "properties": {
                "publisher": {
                    "description": "The organization responsible for publishing the feed",
                    "type": "string"
                },
                "contact_name": {
                    "description": "The name of the individual or group responsible for the data feed",
                    "type": "string"
                },
                "contact_email": {
                    "description": "The email address of the individual or group responsible for the data feed",
                    "type": "string",
                    "format": "email"
                },
                "update_frequency": {
                    "description": "The frequency in seconds at which the data feed is updated",
                    "type": "integer",
                    "minimum": 1
                },
                "update_date": {
                    "description": "The UTC date and time when the GeoJSON file (representing the instance of the feed) was generated",
                    "type": "string",
                    "format": "date-time"
                },
                "version": {
                    "description": "The WZDx specification version used to create the data feed, in 'major.minor' format",
                    "type": "string",
                    "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"
                },
                "license": {
                    "description": "The URL of the license that applies to the data in the WZDx feed. This *must* be the string \"https://creativecommons.org/publicdomain/zero/1.0/\"",
                    "enum": [
                        "https://creativecommons.org/publicdomain/zero/1.0/"
                    ]
                },
                "data_sources": {
                    "description": "A list of specific data sources for the road event data in the feed",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/FeedDataSource"
                    },
                    "minItems": 1
                }
            },
            "required": [
                "update_date",
                "version",
                "publisher",
                "data_sources"
            ],
            "definitions": {
                "FeedDataSource": {
                    "title": "WZDx Feed Data Source",
                    "description": "Describes information about a specific data source used to build the work zone data feed",
                    "type": "object",
                    "properties": {
                        "data_source_id": {
                            "description": "Unique identifier for the organization providing work zone data. It is recommended that this identifier is a Universally Unique IDentifier (UUID) as defined in [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122).",
                            "type": "string"
                        },
                        "organization_name": {
                            "description": "The name of the organization for the authoritative source of the work zone data",
                            "type": "string"
                        },
                        "contact_name": {
                            "description": "The name of the individual or group responsible for the data source",
                            "type": "string"
                        },
                        "contact_email": {
                            "description": "The email address of the individual or group responsible for the data source",
                            "type": "string",
                            "format": "email"
                        },
                        "update_frequency": {
                            "description": "The frequency in seconds at which the data source is updated",
                            "type": "integer",
                            "minimum": 1
                        },
                        "update_date": {
                            "description": "The UTC date and time when the data source was last updated",
                            "type": "string",
                            "format": "date-time"
                        },
                        "lrs_type": {
                            "description": "**DEPRECATED** Describes the type of linear referencing system used for the milepost measurements",
                            "type": "string"
                        },
                        "lrs_url": {
                            "description": "**DEPRECATED** A URL where additional information on the LRS information and transformation information is stored",
                            "type": "string",
                            "format": "uri"
                        },
                        "location_verify_method": {
                            "description": "***DEPRECATED***The method used to verify the accuracy of the location information",
                            "type": "string"
                        }
                    },
                    "required": [
                        "data_source_id",
                        "organization_name"
                    ]
                }
            }
        },
        "type": {
            "description": "The GeoJSON type",
            "enum": [
                "FeatureCollection"
            ]
        },
        "features": {
            "description": "An array of GeoJSON Feature objects which represent WZDx road events",
            "type": "array",
            "items": {
                "allOf": [
                    {
                        "properties": {
                            "properties": {
                                "properties": {
                                    "core_details": {
                                        "properties": {
                                            "event_type": {
                                                "enum": [
                                                    "work-zone",
                                                    "detour"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "event_type"
                                        ]
                                    }
                                },
                                "required": [
                                    "core_details"
                                ]
                            }
                        },
                        "required": [
                            "properties"
                        ]
                    },
                    {
                        "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/RoadEventFeature.json",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "title": "Road Event Feature (GeoJSON Feature)",
                        "description": "The container object for a specific WZDx road event; an instance of a GeoJSON Feature",
                        "type": "object",
                        "properties": {
                            "id": {
                                "description": "A unique identifier issued by the data feed provider to identify the WZDx road event. It is recommended that this identifier is a Universally Unique IDentifier (UUID) as defined in [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122).",
                                "type": "string"
                            },
                            "type": {
                                "description": "The GeoJSON object type; must be 'Feature'",
                                "enum": [
                                    "Feature"
                                ]
                            },
                            "properties": {
                                "type": "object",
                                "properties": {
                                    "core_details": {
                                        "$ref": "#/definitions/RoadEventCoreDetails"
                                    }
                                },
                                "required": [
                                    "core_details"
                                ],
                                "oneOf": [
                                    {
                                        "$ref": "#/definitions/WorkZoneRoadEvent"
                                    },
                                    {
                                        "$ref": "#/definitions/DetourRoadEvent"
                                    }
                                ]
                            },
                            "geometry": {
                                "oneOf": [
                                    {
                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                        "$id": "https://geojson.org/schema/LineString.json",
                                        "title": "GeoJSON LineString",
                                        "type": "object",
                                        "required": [
                                            "type",
                                            "coordinates"
                                        ],
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "LineString"
                                                ]
                                            },
                                            "coordinates": {
                                                "type": "array",
                                                "minItems": 2,
                                                "items": {
                                                    "type": "array",
                                                    "minItems": 2,
                                                    "items": {
                                                        "type": "number"
                                                    }
                                                }
                                            },
                                            "bbox": {
                                                "type": "array",
                                                "minItems": 4,
                                                "items": {
                                                    "type": "number"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                        "$id": "https://geojson.org/schema/MultiPoint.json",
                                        "title": "GeoJSON MultiPoint",
                                        "type": "object",
                                        "required": [
                                            "type",
                                            "coordinates"
                                        ],
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "MultiPoint"
                                                ]
                                            },
                                            "coordinates": {
                                                "type": "array",
                                                "items": {
                                                    "type": "array",
                                                    "minItems": 2,
                                                    "items": {
                                                        "type": "number"
                                                    }
                                                }
                                            },
                                            "bbox": {
                                                "type": "array",
                                                "minItems": 4,
                                                "items": {
                                                    "type": "number"
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                            "bbox": {
                                "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/BoundingBox.json",
                                "$schema": "http://json-schema.org/draft-07/schema#",
                                "title": "GeoJSON Bounding Box",
                                "description": "Information on the coordinate range for a Geometry, Feature, or FeatureCollection",
                                "type": "array",
                                "minItems": 4,
                                "items": {
                                    "type": "number"
                                }
                            }
                        },
                        "required": [
                            "id",
                            "type",
                            "properties",
                            "geometry"
                        ],
                        "definitions": {
                            "WorkZoneRoadEvent": {
                                "title": "Work Zone Road Event",
                                "description": "Describes a work zone road event including where, when, and what activities are taking place within a work zone on a roadway",
                                "type": "object",
                                "allOf": [
                                    {
                                        "properties": {
                                            "core_details": {
                                                "properties": {
                                                    "event_type": {
                                                        "const": "work-zone"
                                                    }
                                                },
                                                "required": [
                                                    "event_type"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "core_details"
                                        ]
                                    },
                                    {
                                        "properties": {
                                            "core_details": {
                                                "$ref": "#/definitions/RoadEventCoreDetails"
                                            },
                                            "beginning_cross_street": {
                                                "description": "Name or number of the nearest cross street along the roadway where the event begins",
                                                "type": "string"
                                            },
                                            "ending_cross_street": {
                                                "description": "Name or number of the nearest cross street along the roadway where the event ends",
                                                "type": "string"
                                            },
                                            "beginning_milepost": {
                                                "description": "The linear distance measured against a milepost marker along a roadway where the event begins",
                                                "type": "number",
                                                "minimum": 0
                                            },
                                            "ending_milepost": {
                                                "description": "The linear distance measured against a milepost marker along a roadway where the event ends",
                                                "type": "number",
                                                "minimum": 0
                                            },
                                            "is_start_position_verified": {
                                                "description": "Indicates if the start position (first geometric coordinate pair) is based on actual reported data from a GPS-equipped device that measured the location of the start of the work zone.",
                                                "type": "boolean"
                                            },
                                            "is_end_position_verified": {
                                                "description": "Indicates if the end position (last geometric coordinate pair) is based on actual reported data from a GPS-equipped device that measured the location of the end of the work zone.",
                                                "type": "boolean"
                                            },
                                            "start_date": {
                                                "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event begins (e.g. 2020-11-03T19:37:00Z)",
                                                "type": "string",
                                                "format": "date-time"
                                            },
                                            "end_date": {
                                                "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event ends (e.g. 2020-11-03T19:37:00Z)",
                                                "type": "string",
                                                "format": "date-time"
                                            },
                                            "is_start_date_verified": {
                                                "description": "Indicates if work has been confirmed to have started, such as from a person or field device",
                                                "type": "boolean"
                                            },
                                            "is_end_date_verified": {
                                                "description": "Indicates if work has been confirmed to have ended, such as from a person or field device",
                                                "type": "boolean"
                                            },
                                            "work_zone_type": {
                                                "description": "The type of work zone road event",
                                                "$ref": "#/definitions/WorkZoneType"
                                            },
                                            "vehicle_impact": {
                                                "$ref": "#/definitions/VehicleImpact"
                                            },
                                            "location_method": {
                                                "$ref": "#/definitions/LocationMethod"
                                            },
                                            "worker_presence": {
                                                "$ref": "#/definitions/WorkerPresence"
                                            },
                                            "reduced_speed_limit_kph": {
                                                "description": "If applicable, the reduced speed limit posted within the road event, in kilometers per hour",
                                                "type": "number",
                                                "minimum": 0
                                            },
                                            "restrictions": {
                                                "description": "A list of zero or more restrictions applying to the road event",
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/definitions/Restriction"
                                                }
                                            },
                                            "types_of_work": {
                                                "description": "A list of the types of work being done in a road event",
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/definitions/TypeOfWork"
                                                }
                                            },
                                            "lanes": {
                                                "description": "A list of individual lanes within a road event (roadway segment)",
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/definitions/Lane"
                                                }
                                            },
                                            "impacted_cds_curb_zones": {
                                                "description": "A list of references to external CDS Curb Zones impacted by the work zone",
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/definitions/CdsCurbZonesReference"
                                                }
                                            },
                                            "event_status": {
                                                "description": "**DEPRECATED**",
                                                "$ref": "#/definitions/EventStatus"
                                            },
                                            "start_date_accuracy": {
                                                "description": "**DEPRECATED** Use is_start_date_verified instead",
                                                "$ref": "#/definitions/TimeVerification"
                                            },
                                            "end_date_accuracy": {
                                                "description": "**DEPRECATED** Use is_end_date_verified instead",
                                                "$ref": "#/definitions/TimeVerification"
                                            },
                                            "beginning_accuracy": {
                                                "description": "**DEPRECATED** Use is_start_position_verified instead.",
                                                "$ref": "#/definitions/SpatialVerification"
                                            },
                                            "ending_accuracy": {
                                                "description": "**DEPRECATED** Use is_end_position_verified instead.",
                                                "$ref": "#/definitions/SpatialVerification"
                                            }
                                        },
                                        "required": [
                                            "core_details",
                                            "start_date",
                                            "end_date",
                                            "vehicle_impact",
                                            "location_method"
                                        ],
                                        "allOf": [
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_start_date_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "start_date_accuracy"
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_start_position_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "beginning_accuracy"
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_end_date_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "end_date_accuracy"
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_end_position_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "ending_accuracy"
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "DetourRoadEvent": {
                                "title": "Detour Road Event",
                                "description": "Describes a detour on a roadway",
                                "type": "object",
                                "allOf": [
                                    {
                                        "properties": {
                                            "core_details": {
                                                "properties": {
                                                    "event_type": {
                                                        "const": "detour"
                                                    }
                                                },
                                                "required": [
                                                    "event_type"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "core_details"
                                        ]
                                    },
                                    {
                                        "properties": {
                                            "core_details": {
                                                "$ref": "#/definitions/RoadEventCoreDetails"
                                            },
                                            "beginning_cross_street": {
                                                "description": "Name or number of the nearest cross street along the roadway where the event begins",
                                                "type": "string"
                                            },
                                            "ending_cross_street": {
                                                "description": "Name or number of the nearest cross street along the roadway where the event ends",
                                                "type": "string"
                                            },
                                            "beginning_milepost": {
                                                "description": "The linear distance measured against a milepost marker along a roadway where the event begins",
                                                "type": "number",
                                                "minimum": 0
                                            },
                                            "ending_milepost": {
                                                "description": "The linear distance measured against a milepost marker along a roadway where the event ends",
                                                "type": "number",
                                                "minimum": 0
                                            },
                                            "start_date": {
                                                "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event begins (e.g. 2020-11-03T19:37:00Z)",
                                                "type": "string",
                                                "format": "date-time"
                                            },
                                            "end_date": {
                                                "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event ends (e.g. 2020-11-03T19:37:00Z)",
                                                "type": "string",
                                                "format": "date-time"
                                            },
                                            "is_start_date_verified": {
                                                "description": "Indicates if the detour has been confirmed to have started, such as from a person or device in the field or a report from a traffic management center",
                                                "type": "boolean"
                                            },
                                            "is_end_date_verified": {
                                                "description": "Indicates if the detour has been confirmed to have ended, such as from a person or device in the field or a report from a traffic management center",
                                                "type": "boolean"
                                            },
                                            "event_status": {
                                                "description": "**DEPRECATED**",
                                                "$ref": "#/definitions/EventStatus"
                                            },
                                            "start_date_accuracy": {
                                                "description": "**DEPRECATED** Use is_start_date_verified instead",
                                                "$ref": "#/definitions/TimeVerification"
                                            },
                                            "end_date_accuracy": {
                                                "description": "**DEPRECATED** Use is_end_date_verified instead",
                                                "$ref": "#/definitions/TimeVerification"
                                            }
                                        },
                                        "required": [
                                            "core_details",
                                            "start_date",
                                            "end_date"
                                        ],
                                        "allOf": [
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_start_date_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "start_date_accuracy"
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                "anyOf": [
                                                    {
                                                        "required": [
                                                            "is_end_date_verified"
                                                        ]
                                                    },
                                                    {
                                                        "required": [
                                                            "end_date_accuracy"
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "RoadEventCoreDetails": {
                                "title": "Road Event Core Details",
                                "description": "The core details of an event occurring on a roadway (i.e. a road event) that is shared by all types of road events",
                                "type": "object",
                                "properties": {
                                    "data_source_id": {
                                        "description": "Identifies the data source from which the road event data is sourced from",
                                        "type": "string"
                                    },
                                    "event_type": {
                                        "$ref": "#/definitions/EventType"
                                    },
                                    "related_road_events": {
                                        "description": "A list describing one or more road events which are related to this road event, such as a work zone project it is part of or another road event that occurs before or after it in sequence.",
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/definitions/RelatedRoadEvent"
                                        }
                                    },
                                    "road_names": {
                                        "description": "A list of publicly known names of the road on which the event occurs. This may include the road number designated by a jurisdiction such as a county, state or interstate (e.g. I-5, VT 133)",
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "direction": {
                                        "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/Direction.json",
                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                        "title": "Direction Enumerated Type",
                                        "description": "The direction of a road based on standard naming for US roads; indicates the direction the traffic flow not the real heading angle.",
                                        "enum": [
                                            "northbound",
                                            "eastbound",
                                            "southbound",
                                            "westbound",
                                            "undefined",
                                            "unknown",
                                            "inner-loop",
                                            "outer-loop"
                                        ]
                                    },
                                    "name": {
                                        "description": "A human-readable name for the road event",
                                        "type": "string"
                                    },
                                    "description": {
                                        "description": "Short free text description of the road event",
                                        "type": "string"
                                    },
                                    "creation_date": {
                                        "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event was created (e.g. 2020-11-03T19:37:00Z)",
                                        "type": "string",
                                        "format": "date-time"
                                    },
                                    "update_date": {
                                        "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when any information in the RoadEventFeature (including child objects) that the RoadEventCoreDetails applies to was most recently updated or confirmed as up to date",
                                        "type": "string",
                                        "format": "date-time"
                                    },
                                    "relationship": {
                                        "description": "**DEPRECATED**",
                                        "$ref": "#/definitions/Relationship"
                                    }
                                },
                                "required": [
                                    "event_type",
                                    "data_source_id",
                                    "direction",
                                    "road_names"
                                ]
                            },
                            "LocationMethod": {
                                "title": "Location Method Enumerated Type",
                                "description": "The typical method used to locate the beginning and end of a work zone impact area",
                                "enum": [
                                    "channel-device-method",
                                    "sign-method",
                                    "junction-method",
                                    "other",
                                    "unknown"
                                ]
                            },
                            "Relationship": {
                                "title": "Relationship",
                                "description": "**DEPRECATED** Identifies both sequential and hierarchical relationships between road events and other entities. For example, a relationship can be used to link multiple road events to a common 'parent', such as a project or phase, or identify a sequence of road events",
                                "type": "object",
                                "properties": {
                                    "first": {
                                        "description": "Indicates the first (can be multiple) road event in a sequence of road events by RoadEventFeature 'id'",
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "next": {
                                        "description": "Indicates the next (can be multiple) road event in a sequence of road events by RoadEventFeature 'id'",
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "parents": {
                                        "description": "Indicates entities that the road event with this relationship is a part of, such as a work zone project or phase. Values can but do not have to correspond to a WZDx entity",
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "children": {
                                        "description": "Indicates entities that are part of the road event with this relationship, such as a detour or piece of equipment. Values can but do not have to correspond to a WZDx entity",
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {
                                            "type": "string"
                                        }
                                    }
                                }
                            },
                            "RelatedRoadEvent": {
                                "title": "RelatedRoadEvent",
                                "description": "Identifies a road event that is related to the road event that the RelatedRoadEvent object occurs on.",
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "description": "The type of road event being identified, such as another sequence of related work zones, a detour, or next road event in sequence.",
                                        "$ref": "#/definitions/RelatedRoadEventType"
                                    },
                                    "id": {
                                        "description": "An identifier for the related road event by the type property.",
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "type",
                                    "id"
                                ]
                            },
                            "TypeOfWork": {
                                "title": "Type of Work",
                                "description": "A description of the type of work being done in a road event and an indication of if that work will result in an architectural change to the roadway",
                                "type": "object",
                                "properties": {
                                    "type_name": {
                                        "$ref": "#/definitions/WorkTypeName"
                                    },
                                    "is_architectural_change": {
                                        "description": "A flag indicating whether the type of work will result in an architectural change to the roadway",
                                        "type": "boolean"
                                    }
                                },
                                "required": [
                                    "type_name"
                                ]
                            },
                            "Lane": {
                                "title": "Lane",
                                "description": "An individual lane within a road event",
                                "type": "object",
                                "properties": {
                                    "order": {
                                        "description": "The position (index) of the lane in sequence on the roadway, where '1' represents the left-most lane",
                                        "type": "integer",
                                        "minimum": 1
                                    },
                                    "status": {
                                        "$ref": "#/definitions/LaneStatus"
                                    },
                                    "type": {
                                        "$ref": "#/definitions/LaneType"
                                    },
                                    "lane_number": {
                                        "description": "***DEPRECATED*** The number assigned to the lane to help identify its position. Flexible, but usually used for regular, drivable lanes",
                                        "type": "integer",
                                        "minimum": 1
                                    },
                                    "restrictions": {
                                        "description": "A list of zero or more restrictions specific to the lane",
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/definitions/Restriction"
                                        }
                                    }
                                },
                                "required": [
                                    "status",
                                    "type",
                                    "order"
                                ]
                            },
                            "Restriction": {
                                "title": "Restriction",
                                "description": "A restriction on a roadway or lane, including type and value",
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "$ref": "#/definitions/RestrictionType"
                                    },
                                    "value": {
                                        "type": "number"
                                    },
                                    "unit": {
                                        "$ref": "#/definitions/UnitOfMeasurement"
                                    }
                                },
                                "required": [
                                    "type"
                                ],
                                "dependencies": {
                                    "value": [
                                        "unit"
                                    ]
                                }
                            },
                            "CdsCurbZonesReference": {
                                "title": "CdsCurbZonesReference",
                                "description": "A reference to one or more CDS curb zones that are impacted by road work",
                                "type": "object",
                                "properties": {
                                    "cds_curb_zone_ids": {
                                        "description": "A list of CDS Curb Zone ids",
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "cds_curbs_api_url": {
                                        "description": "An identifier for the source of the requested CDS Curbs API",
                                        "type": "string",
                                        "format": "uri"
                                    }
                                },
                                "required": [
                                    "cds_curb_zone_ids",
                                    "cds_curbs_api_url"
                                ]
                            },
                            "WorkerPresence": {
                                "title": "Worker Presence",
                                "description": "Information about the presence of workers in the work zone event area",
                                "type": "object",
                                "properties": {
                                    "are_workers_present": {
                                        "description": "Whether workers are present in the work zone event area, following the definition provided in the \u2018definition\u2019 property on the WorkerPresence object",
                                        "type": "boolean"
                                    },
                                    "method": {
                                        "$ref": "#/definitions/WorkerPresenceMethod"
                                    },
                                    "worker_presence_last_confirmed_date": {
                                        "description": "The UTC date and time at which the presence of workers was last confirmed",
                                        "type": "string",
                                        "format": "date-time"
                                    },
                                    "confidence": {
                                        "$ref": "#/definitions/WorkerPresenceConfidence"
                                    },
                                    "definition": {
                                        "description": "A list of situations in which workers are considered to be present in the jurisdiction of the data provider",
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/definitions/WorkerPresenceDefinition"
                                        },
                                        "uniqueItems": True
                                    }
                                },
                                "required": [
                                    "are_workers_present"
                                ]
                            },
                            "EventType": {
                                "title": "Road Event Type Enumerated Type",
                                "description": "The type of WZDx road event",
                                "enum": [
                                    "work-zone",
                                    "detour",
                                    "restriction"
                                ]
                            },
                            "SpatialVerification": {
                                "title": "Spatial Verification Enumerated Type",
                                "description": "An indication of how a geographical coordinate was defined",
                                "enum": [
                                    "estimated",
                                    "verified"
                                ]
                            },
                            "TimeVerification": {
                                "title": "Time Verification Enumerated Type",
                                "description": "A measure of how accurate a date-time is",
                                "enum": [
                                    "estimated",
                                    "verified"
                                ]
                            },
                            "EventStatus": {
                                "title": "Event Status Enumerated Type",
                                "description": "The status of the road event",
                                "enum": [
                                    "planned",
                                    "pending",
                                    "active",
                                    "completed",
                                    "cancelled"
                                ]
                            },
                            "WorkZoneType": {
                                "title": "Work Zone Type Enumerated Type",
                                "description": "The type of work zone road event",
                                "enum": [
                                    "static",
                                    "moving",
                                    "planned-moving-area"
                                ]
                            },
                            "VehicleImpact": {
                                "title": "Vehicle Impact Enumerated Type",
                                "description": "The impact to vehicular lanes along a single road in a single direction",
                                "enum": [
                                    "all-lanes-closed",
                                    "some-lanes-closed",
                                    "all-lanes-open",
                                    "alternating-one-way",
                                    "some-lanes-closed-merge-left",
                                    "some-lanes-closed-merge-right",
                                    "all-lanes-open-shift-left",
                                    "all-lanes-open-shift-right",
                                    "some-lanes-closed-split",
                                    "flagging",
                                    "temporary-traffic-signal",
                                    "unknown"
                                ]
                            },
                            "RestrictionType": {
                                "title": "Restriction Type Enumerated Type",
                                "description": "The type of vehicle restriction on a roadway",
                                "enum": [
                                    "no-trucks",
                                    "travel-peak-hours-only",
                                    "hov-3",
                                    "hov-2",
                                    "no-parking",
                                    "reduced-width",
                                    "reduced-height",
                                    "reduced-length",
                                    "reduced-weight",
                                    "axle-load-limit",
                                    "gross-weight-limit",
                                    "towing-prohibited",
                                    "permitted-oversize-loads-prohibited",
                                    "local-access-only",
                                    "no-passing"
                                ]
                            },
                            "WorkTypeName": {
                                "title": "Work Type Name Enumerated Type",
                                "description": "A high-level text description of the type of work being done in a road event",
                                "enum": [
                                    "maintenance",
                                    "minor-road-defect-repair",
                                    "roadside-work",
                                    "overhead-work",
                                    "below-road-work",
                                    "barrier-work",
                                    "surface-work",
                                    "painting",
                                    "roadway-relocation",
                                    "roadway-creation"
                                ]
                            },
                            "LaneStatus": {
                                "title": "Lane Status Enumerated Type",
                                "description": "The status of the lane for the traveling public",
                                "enum": [
                                    "open",
                                    "closed",
                                    "shift-left",
                                    "shift-right",
                                    "merge-left",
                                    "merge-right",
                                    "alternating-flow"
                                ]
                            },
                            "LaneType": {
                                "title": "Lane Type Enumerated Type",
                                "description": "An indication of the type of lane or shoulder",
                                "enum": [
                                    "general",
                                    "exit-lane",
                                    "exit-ramp",
                                    "entrance-lane",
                                    "entrance-ramp",
                                    "sidewalk",
                                    "bike-lane",
                                    "shoulder",
                                    "parking",
                                    "median",
                                    "two-way-center-turn-lane",
                                    "center-left-turn-lane"
                                ]
                            },
                            "UnitOfMeasurement": {
                                "title": "Unit of Measurement Enumerated Type",
                                "description": "Unit of measurement, used when providing a unit to accompany a value",
                                "enum": [
                                    "feet",
                                    "inches",
                                    "centimeters",
                                    "pounds",
                                    "tons",
                                    "kilograms"
                                ]
                            },
                            "WorkerPresenceMethod": {
                                "title": "Worker Presence Method Enumerated Type",
                                "description": "Describes methods for how worker presence in a work zone event area is determined",
                                "enum": [
                                    "camera-monitoring",
                                    "arrow-board-present",
                                    "cones-present",
                                    "maintenance-vehicle-present",
                                    "wearables-present",
                                    "mobile-device-present",
                                    "check-in-app",
                                    "check-in-verbal",
                                    "scheduled"
                                ]
                            },
                            "WorkerPresenceDefinition": {
                                "title": "Worker Presence Definition Enumerated Type",
                                "description": "Situations in which workers may be considered present in a work zone",
                                "enum": [
                                    "workers-in-work-zone-working",
                                    "workers-in-work-zone-not-working",
                                    "mobile-equipment-in-work-zone-moving",
                                    "mobile-equipment-in-work-zone-not-moving",
                                    "fixed-equipment-in-work-zone",
                                    "humans-behind-barrier",
                                    "humans-in-right-of-way"
                                ]
                            },
                            "WorkerPresenceConfidence": {
                                "title": "Worker Presence Confidence Enumerated Type",
                                "description": "A high-level description of the feed publisher's confidence in the reported WorkerPresence value of are_workers_present",
                                "enum": [
                                    "low",
                                    "medium",
                                    "high"
                                ]
                            },
                            "RelatedRoadEventType": {
                                "title": "Related Road Event Type Enumerated Type",
                                "description": "Describes how a road event is related to the road event that the RelatedRoadEvent object occurs on.",
                                "enum": [
                                    "first-in-sequence",
                                    "next-in-sequence",
                                    "first-occurrence",
                                    "next-occurrence",
                                    "related-work-zone",
                                    "related-detour",
                                    "planned-moving-operation",
                                    "active-moving-operation"
                                ]
                            }
                        }
                    }
                ]
            }
        },
        "bbox": {
            "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/BoundingBox.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "GeoJSON Bounding Box",
            "description": "Information on the coordinate range for a Geometry, Feature, or FeatureCollection",
            "type": "array",
            "minItems": 4,
            "items": {
                "type": "number"
            }
        },
        "road_event_feed_info": {
            "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/FeedInfo.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "WZDx Feed Information",
            "description": "Describes WZDx feed header information such as metadata, contact information, and data sources",
            "type": "object",
            "properties": {
                "publisher": {
                    "description": "The organization responsible for publishing the feed",
                    "type": "string"
                },
                "contact_name": {
                    "description": "The name of the individual or group responsible for the data feed",
                    "type": "string"
                },
                "contact_email": {
                    "description": "The email address of the individual or group responsible for the data feed",
                    "type": "string",
                    "format": "email"
                },
                "update_frequency": {
                    "description": "The frequency in seconds at which the data feed is updated",
                    "type": "integer",
                    "minimum": 1
                },
                "update_date": {
                    "description": "The UTC date and time when the GeoJSON file (representing the instance of the feed) was generated",
                    "type": "string",
                    "format": "date-time"
                },
                "version": {
                    "description": "The WZDx specification version used to create the data feed, in 'major.minor' format",
                    "type": "string",
                    "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"
                },
                "license": {
                    "description": "The URL of the license that applies to the data in the WZDx feed. This *must* be the string \"https://creativecommons.org/publicdomain/zero/1.0/\"",
                    "enum": [
                        "https://creativecommons.org/publicdomain/zero/1.0/"
                    ]
                },
                "data_sources": {
                    "description": "A list of specific data sources for the road event data in the feed",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/FeedDataSource"
                    },
                    "minItems": 1
                }
            },
            "required": [
                "update_date",
                "version",
                "publisher",
                "data_sources"
            ],
            "definitions": {
                "FeedDataSource": {
                    "title": "WZDx Feed Data Source",
                    "description": "Describes information about a specific data source used to build the work zone data feed",
                    "type": "object",
                    "properties": {
                        "data_source_id": {
                            "description": "Unique identifier for the organization providing work zone data. It is recommended that this identifier is a Universally Unique IDentifier (UUID) as defined in [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122).",
                            "type": "string"
                        },
                        "organization_name": {
                            "description": "The name of the organization for the authoritative source of the work zone data",
                            "type": "string"
                        },
                        "contact_name": {
                            "description": "The name of the individual or group responsible for the data source",
                            "type": "string"
                        },
                        "contact_email": {
                            "description": "The email address of the individual or group responsible for the data source",
                            "type": "string",
                            "format": "email"
                        },
                        "update_frequency": {
                            "description": "The frequency in seconds at which the data source is updated",
                            "type": "integer",
                            "minimum": 1
                        },
                        "update_date": {
                            "description": "The UTC date and time when the data source was last updated",
                            "type": "string",
                            "format": "date-time"
                        },
                        "lrs_type": {
                            "description": "**DEPRECATED** Describes the type of linear referencing system used for the milepost measurements",
                            "type": "string"
                        },
                        "lrs_url": {
                            "description": "**DEPRECATED** A URL where additional information on the LRS information and transformation information is stored",
                            "type": "string",
                            "format": "uri"
                        },
                        "location_verify_method": {
                            "description": "***DEPRECATED***The method used to verify the accuracy of the location information",
                            "type": "string"
                        }
                    },
                    "required": [
                        "data_source_id",
                        "organization_name"
                    ]
                }
            }
        }
    },
    "required": [
        "type",
        "features"
    ],
    "anyOf": [
        {
            "required": [
                "feed_info"
            ]
        },
        {
            "required": [
                "road_event_feed_info"
            ]
        }
    ]
}