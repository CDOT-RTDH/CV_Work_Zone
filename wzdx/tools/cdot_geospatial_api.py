from wzdx.tools import path_history_compression
from wzdx.tools import polygon_tools
import requests
import json
<< << << < HEAD
== == == =

>>>>>> > path_compression

BASE_URL = "https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded"
ROUTE_BETWEEN_MEASURES_API = "RouteBetweenMeasures"
GET_ROUTE_AND_MEASURE_API = "MeasureAtPoint"
GET_ROUTES_API = "ROUTES"
GET_ROUTE_API = "ROUTE"
SR = "4326"
<< << << < HEAD
DIRECTION_MARKER = ["positive", "negative"]
DIRECTION_MARKER_REVERSE = {"positive": "negative", "negative": "positive"}
== == == =
>>>>>> > path_compression


def get_routes_list():
    parameters = []
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTES_API}?{'&'.join(parameters)}"
    print(url)

    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Routes?f=pjson
    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/Route?routeId=070A&outSR=4326&f=pjson

    resp = json.loads(requests.get(url).content)
    # response = [{'routeID': '070A', 'MMin': 0, 'MMax': 499}]
    return resp


def get_route_details(routeId):
    parameters = []
    parameters.append(f'routeId={routeId}')
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_API}?{'&'.join(parameters)}"
    print(url)

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


def get_route_and_measure(latLng, heading=None, tolerance=10000):
    # Get route ID and mile marker from lat/long and heading
    lat, lng = latLng

    parameters = []
    parameters.append(f"x={lng}")
    parameters.append(f"y={lat}")
    parameters.append(f"tolerance={tolerance}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"
    print(url)

    # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/MeasureAtPoint?x=-105&y=39.5&inSR=4326&tolerance=10000&outSR=&f=html
    resp = json.loads(requests.get(url).content)
    # raise NotImplementedError("No geospatial endpoint")

    if not resp.get('features'):
        return None
    route_details = {
        'Route': resp['features'][0]['attributes']['Route'],
        'Measure': float(resp['features'][0]['attributes']['Measure']),
        'MMin': float(resp['features'][0]['attributes']['MMin']),
        'MMax': float(resp['features'][0]['attributes']['MMax']),
        'Distance': float(resp['features'][0]['attributes']['Distance']),
    }

    if heading:
        step = 0.1  # 250 ft
        route = route_details['Route']
        measure = route_details['Measure']
        mmin = route_details['MMin']
        mmax = route_details['MMax']
        startMeasure = measure - step
        endMeasure = measure
        if startMeasure < mmin:
            # reverse order
            startMeasure = measure
            endMeasure = measure + step
        coords = get_route_between_measures(route, startMeasure, endMeasure)
        bearing = polygon_tools.get_heading_from_coordinates(coords)

        if bearing > 180:
            bearing -= 360
        if abs(bearing - heading) < 90:
            route_details['Direction'] = '+'
        else:
            route_details['Direction'] = '-'

    return route_details


def get_route_measure_direction(latLng, bearing):
    # Get route ID and mile marker from lat/long and heading
    lat, lng = latLng

    parameters = []


<< << << < HEAD
  parameters.append(f"x={lng}")
   parameters.append(f"y={lat}")
    parameters.append(f"tolerance={tolerance}")
    parameters.append(f"inSR={SR}")
    parameters.append(f"outSR={SR}")
== == == =
  parameters.append(f"latitude={lat}")
   parameters.append(f"longitude={lng}")
    parameters.append(f"heading={bearing}")
    parameters.append(f"inSR={SR}")
>>>>>> > path_compression
  parameters.append(f"f=pjson")

   url = f"{BASE_URL}/{GET_ROUTE_AND_MEASURE_API}?{'&'.join(parameters)}"
    print(url)

<< << << < HEAD
  # https://dtdapps.coloradodot.info/arcgis/rest/services/LRS/Routes/MapServer/exts/CdotLrsAccessRounded/MeasureAtPoint?x=-105&y=39.5&inSR=4326&tolerance=10000&outSR=&f=html
  resp = json.loads(requests.get(url).content)
   # raise NotImplementedError("No geospatial endpoint")

   if not resp.get('features'):
        return None
    route_details = {
        'Route': resp['features'][0]['attributes']['Route'],
        'Measure': float(resp['features'][0]['attributes']['Measure']),
        'MMin': float(resp['features'][0]['attributes']['MMin']),
        'MMax': float(resp['features'][0]['attributes']['MMax']),
        'Distance': float(resp['features'][0]['attributes']['Distance']),
    }

== == ===
  # response = requests.get(url).content
>>>>>> > path_compression
  # raise NotImplementedError("No geospatial endpoint")
  return {"Route": "070A", "Measure": 12, 'Direction': 'N'}


<< <<<< < HEAD


def get_route_geometry_ahead(routeId, startMeasure, heading, distanceAhead, pointsToSkip=0, routeDetails=None, mmin=None, mmax=None):
    # Get list of routes and mile markers for a distance ahead and distance

    # TODO: Integrate direction to determine whether to add/subtract distance
    if not routeDetails:
        routeDetails = get_route_and_measure(routeId, heading)

    # process direction here
    if (routeDetails.get('Direction', '+') == '+'):
        endMeasure = startMeasure + distanceAhead
        endMeasure = min(endMeasure, routeDetails['MMax'])
    else:
        endMeasure = startMeasure - distanceAhead
        endMeasure = max(endMeasure, routeDetails['MMin'])

    if mmin != None and mmax != None:
        # Force mmin > mmax
        if mmin > mmax:
            temp = mmin
            mmin = mmax
            mmax = temp

        # Force measures between bounds
        startMeasure = min(max(startMeasure, mmin), mmax)
        endMeasure = min(max(endMeasure, mmin), mmax)

== == ===


def get_route_geometry_ahead(routeId, startMeasure, direction, distanceAhead, pointsToSkip=0, routeDetails=None):
    # Get list of routes and mile markers for a distance ahead and distance

    # TODO: Integrate direction to determine whether to add/subtract distance
    endMeasure = startMeasure + distanceAhead
    if not routeDetails:
        routeDetails = get_route_details(routeId)

    # process direction here
    if (direction):
        # assume startMeasure is on road
        endMeasure = min(endMeasure, routeDetails['MMax'])
    else:
        endMeasure = max(endMeasure, routeDetails['MMin'])

>>>>>> > path_compression
  print(f"Measures: {startMeasure}, {endMeasure}")

   return {'start_measure': startMeasure, 'end_measure': endMeasure,
            'coordinates': get_route_between_measures(
                routeId, startMeasure, endMeasure, pointsToSkip)}


def get_routes_ahead(route, startMeasure, direction, distanceAhead):
    # Get list of routes and mile markers for a distance ahead and distance
    raise NotImplementedError("No geospatial endpoint")

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


<< <<<< < HEAD
def get_route_between_measures(routeId, startMeasure, endMeasure, pointsToSkip=0):
== == ===
def get_route_between_measures(routeId, startMeasure, endMeasure, compressed=False):

>>>>>> > path_compression
  # Get lat/long points between two mile markers on route

  parameters = []
   parameters.append(f"routeId={routeId}")
    parameters.append(f"fromMeasure={startMeasure}")
    parameters.append(f"toMeasure={endMeasure}")
    parameters.append(f"outSR={SR}")
    parameters.append(f"f=pjson")

    url = f"{BASE_URL}/{ROUTE_BETWEEN_MEASURES_API}?{'&'.join(parameters)}"
    print(url)

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

<< <<<< < HEAD
  linestring = [v for i, v in enumerate(
       linestring) if i % (pointsToSkip+1) == 0]
== == ===
  # linestring = [v for i, v in enumerate(
  #     linestring) if i % (pointsToSkip+1) == 0]

  if compressed:
       linestring = path_history_compression.generage_compressed_path(
            linestring)
>>>>>> > path_compression

  return linestring

   # RouteBetweenMeasures?routeId=070A&fromMeasure=50&toMeasure=60&outSR=4326&f=pjson


def get_route_between_measures_dual_carriageway(routeId, startMeasure, endMeasure, direction, pointsToSkip=0):
    # Get lat/long points between two mile markers on route

    routeId = "070A"
    startMeasure = 10
    endMeasure = 12

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
