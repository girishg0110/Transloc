from dotenv import load_dotenv
import os
import requests
import json

api_host = "transloc-api-1-2.p.rapidapi.com"
api_key = None
agency_id = "1323"

route_name_to_id = {}
route_stops = {}
stop_name_to_id = {}
stop_routes = {}

def send_request(api_endpoint, extra_params = None):
    url = f"https://transloc-api-1-2.p.rapidapi.com/{api_endpoint}.json"
    if not extra_params: 
        extra_params = {}
    extra_params["agencies"] = agency_id
    extra_params["callback"] = "call"
    headers = {"X-RapidAPI-Host" : api_host, "X-RapidAPI-Key" : api_key}
    print(extra_params)

    response = requests.request("GET", url, headers=headers, params=extra_params)
    return json.loads(response.text)["data"]

def test_endpoints(endpoint):
    print(json.dumps(send_request(endpoint), indent=4), end="\n\n\n")

def init_routes_and_stops():
    global route_name_to_id, route_stops, stop_name_to_id, stop_routes
    route_dict = send_request("routes")
    #test_endpoints("routes")
    for route in route_dict[agency_id]:
        if route["is_active"]:
            name = route["short_name"] if route["short_name"] else route["long_name"]
            route_name_to_id[name] = route["route_id"]
            route_stops[route["route_id"]] = set(route["stops"])
    stop_list = send_request("stops")
    for stop in stop_list:
        stop_name_to_id[stop["name"]] = stop["stop_id"]
        stop_routes[stop["stop_id"]] = set(stop["routes"])

    #print(route_id_to_name, stop_id_to_name, sep = '\n')
    #print(route_id_to_name, stop_id_to_name, sep = '\n')
    #print(route_stops, stop_routes, sep = '\n')

def init_app():
    global api_key
    load_dotenv()
    api_key = os.getenv("TRANSLOC_API_KEY")
    init_routes_and_stops()
    
def get_routes(src, dest):
    # Get routes connecting src and dest
    target_routes = stop_routes[src].intersection(stop_routes[dest])
    upcoming_buses = send_request("arrival-estimates", extra_params = {"stops" : src, "routes": ','.join(target_routes)})
    print(upcoming_buses)
    return target_routes

if __name__ == "__main__":
    init_app()

    source = "Blumenthal Hall"
    destination = "Dental School"
    src_id = stop_name_to_id[source]
    dest_id = stop_name_to_id[destination]
    print(src_id, dest_id)
    print(route_stops, route_name_to_id, sep='\n')
    print(stop_name_to_id)

    upcoming_routes = get_routes(src_id, dest_id)
    print(upcoming_routes)

    # enter waiting stop/coordinates and destination : returns bus id, time of arrival, etc.
