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
    graph = ox.graph_from_place('Chandigarh, India', network_type='drive',simplify=False)
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

    if not start_coords or not end_coords:
        return jsonify({'error': 'Please provide both start and end coordinates.'}), 400

    # Find the nearest nodes in the graph to these coordinates
    start_node = ox.nearest_nodes(graph, start_coords[1], start_coords[0])  # lon, lat
    end_node = ox.nearest_nodes(graph, end_coords[1], end_coords[0])        # lon, lat

    try:
        # A* algorithm to find the path
        path = nx.astar_path(graph, start_node, end_node, heuristic=heuristic)

        # Extract the geometry or fallback to straight lines between nodes
        route_coords = []
        for u, v in zip(path[:-1], path[1:]):
            # Get the edge data between node u and v
            edge_data = graph.get_edge_data(u, v)

            # Ensure 'geometry' exists and coordinates are used in the correct (lat, lon) format
            for edge_key in edge_data:
                edge = edge_data[edge_key]
                if 'geometry' in edge:
                    # Correctly append geometry coordinates in (lat, lon) order
                    route_coords.extend([(lat, lon) for lon, lat in edge['geometry'].coords])
                else:
                    # Fallback to straight line, but ensure correct lat, lon order
                    route_coords.append((graph.nodes[u]['y'], graph.nodes[u]['x']))  # (lat, lon)
                    route_coords.append((graph.nodes[v]['y'], graph.nodes[v]['x']))  # (lat, lon)
        print(f"Route Coordinates: {route_coords}")

        # Return the route coordinates to the frontend
        return jsonify({
            'path': route_coords,
            'length': nx.astar_path_length(graph, start_node, end_node, heuristic=heuristic)
        })
    except nx.NetworkXNoPath:
        return jsonify({'error': 'No path found between the specified points.'}), 400



if __name__ == '__main__':
    app.run(debug=True)
