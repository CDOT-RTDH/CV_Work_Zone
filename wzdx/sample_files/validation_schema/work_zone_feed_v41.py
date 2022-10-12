wzdx_v41_schema_string = {
  "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/WorkZoneFeed.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WZDx v4.1 Work Zone Feed",
  "description": "The GeoJSON output of a WZDx Work Zone Feed (v4.1)",
  "type": "object",
  "properties": {
    "feed_info": {
      "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/FeedInfo.json"
    },
    "type": {
      "description": "The GeoJSON type",
      "enum": ["FeatureCollection"]
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
                        "enum": ["work-zone", "detour"]
                      }
                    },
                    "required": ["event_type"]
                  }
                },
                "required": ["core_details"]
              }
            },
            "required": ["properties"]
          },
          {
            "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/RoadEventFeature.json"
          }
        ]
      }
    },
    "bbox": {
      "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/BoundingBox.json"
    },
    "road_event_feed_info": {
      "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/FeedInfo.json"
    }
  },
  "required": ["type", "features"],
  "anyOf": [
    { 
      "required": ["feed_info"]
    },
    {
      "required": ["road_event_feed_info"]
    }
  ]
}