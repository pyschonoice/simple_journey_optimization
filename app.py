from flask import Flask, render_template, request, jsonify
import networkx as nx
import osmnx as ox
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)

# Try loading the graph from a file if it exists
try:
    graph = ox.load_graphml('chandigarh_map.graphml')
except FileNotFoundError:
    print("Downloading map for Chandigarh, India...")
    graph = ox.graph_from_place('Chandigarh, India', network_type='drive')
    ox.save_graphml(graph, filepath='chandigarh_map.graphml')

@app.route('/')
def index():
    # Render the main index page
    return render_template('index.html')

@app.route('/find_route_page')
def find_route_page():
    # Render the route finding page with the map
    return render_template('find_route.html')


def heuristic(node1, node2):
    # Get the latitude and longitude of the nodes
    lat1, lon1 = graph.nodes[node1]['y'], graph.nodes[node1]['x']
    lat2, lon2 = graph.nodes[node2]['y'], graph.nodes[node2]['x']

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula to calculate the distance between two points on the Earth's surface
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    R = 6371  # Radius of Earth in kilometers
    return R * c

@app.route('/find_route', methods=['POST'])
def find_route():
    data = request.json
    start_coords = data.get('start')  # [lat, lon]
    end_coords = data.get('end')      # [lat, lon]

    print(f"Start Coordinates: {start_coords}, End Coordinates: {end_coords}")  # Debugging

    if not start_coords or not end_coords:
        return jsonify({'error': 'Please provide both start and end coordinates.'}), 400

    try:
        start_node = ox.nearest_nodes(graph, start_coords[1], start_coords[0])  # lon, lat
        end_node = ox.nearest_nodes(graph, end_coords[1], end_coords[0])        # lon, lat
        print(f"Start Node: {start_node}, End Node: {end_node}")  # Debugging
    except ValueError:
        return jsonify({'error': 'Could not find a path between the given coordinates.'}), 400

    try:
        # Use the A* algorithm with the custom heuristic
        path = nx.astar_path(graph, start_node, end_node, heuristic=heuristic)
        route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]

        print(f"Route Coordinates: {route_coords}")  # Debugging

        return jsonify({
            'path': route_coords,
            'length': nx.astar_path_length(graph, start_node, end_node, heuristic=heuristic)
        })
    except nx.NetworkXNoPath:
        return jsonify({'error': 'No path found between the specified points.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
