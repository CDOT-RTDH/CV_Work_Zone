import requests
import json

BASE_URL = "https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded"
ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
GET_ROUTE_AND_MEASURE_API = "GetMeasure"
GET_ROUTES_API = "ROUTES"
GET_ROUTE_API = "ROUTE"
SR = "4326"


def get_routes_list():
    parameters = []
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTES_API}?{'&'.join(parameters)}"

    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

    resp = json.loads(requests.get(url).content)
    # response = [{'routeID': '070A', 'MMin': 0, 'MMax': 499}]
    return resp


def get_route_details(routeId, pointsToSkip=1):
    parameters = []
    parameters.append(f'routeId={routeId}')
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_API}?{'&'.join(parameters)}"

    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

    resp = json.loads(requests.get(url).content)
    # response = {'routeID': '070A', 'MMin': 0, 'MMax': 499}

    route_details = {
        'Route': resp['features'][0]['attributes']['Route'],
        'MMin': float(resp['features'][0]['attributes']['MMin']),
        'MMax': float(resp['features'][0]['attributes']['MMax']),
    }

    return route_details


def get_route_and_measure(latLng, bearing):
    # Get route ID and mile marker from lat/long and heading
    lat, lng = latLng

    parameters = []
    parameters.append(f"latitude={lat}")
    parameters.append(f"longitude={lng}")
    parameters.append(f"heading={bearing}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"

    # response = requests.get(url).content
    # raise NotImplementedError("No geospatial endpoint")
    return {"Route": "070A", "measure": 12, 'direction': 'N'}


def get_routes_ahead(route, startMeasure, direction, distanceAhead):
    # Get list of routes and mile markers for a distance ahead and distance

    parameters = []
    parameters.append(f"routeId={route}")
    parameters.append(f"startMeasure={startMeasure}")
    parameters.append(f"direction={direction}")
    parameters.append(f"distance={distanceAhead}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"

    # response = requests.get(url).content
    # raise NotImplementedError("No geospatial endpoint")
    resp = [
        {"Route": "070A", "MMin": 12, 'MMax': 499},
        {"Route": "070B", 'MMin': 0, 'MMax': 2}
    ]

    return resp


def get_route_between_measures(routeId, startMeasure, endMeasure, pointsToSkip=1):
    # Get lat/long points between two mile markers on route

    parameters = []
    parameters.append(f"routeId={routeId}")
    parameters.append(f"fromMeasure={startMeasure}")
    parameters.append(f"toMeasure={endMeasure}")
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{ROUTE_BETWEEN_MEASURES_API}?{'&'.join(parameters)}"

    # call api
    response = json.loads(requests.get(url).content)
    # response = json.loads(open(
    #     './wzdx/sample_files/raw/geotab_avl/geospatial_endpoint_response.json').read())

    # COMMENTED OUT because I am not sure whether to combine paths into one or leave them separate
    # paths = []
    # for feature_index, feature in enumerate(response.get('features', [])):
    #     for path in feature.get('geometry', {}).get('paths', []):
    #         linestring = [v for i, v in enumerate(
    #             path) if i % (pointsToSkip+1) == 0]
    #         paths.append(linestring)

    # return paths

    linestring = []
    for feature in response.get('features', []):
        for path in feature.get('geometry', {}).get('paths', []):
            linestring.extend(path)

    linestring = [v for i, v in enumerate(
        linestring) if i % (pointsToSkip+1) == 0]

    return linestring

    # RouteBetweenMeasures?routeId=070A&fromMeasure=50&toMeasure=60&outSR=4326&f=pjson
