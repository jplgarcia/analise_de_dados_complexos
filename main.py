import networkx as nx
import matplotlib.pyplot as plt
import csv

def load_airports(filename):
    airports = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            airport_id, name, city, country, IATA, ICAO, latitude, longitude, *_ = row
            airports[(airport_id)] = {
                'name': name,
                'city': city,
                'country': country,
                'IATA': IATA,
                'ICAO': ICAO,
                'latitude': float(latitude),
                'longitude': float(longitude)
            }

    return airports

def load_routes(filename):
    routes = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            airline, _, _, source, _, dest, _, _, _ = row
            if source == "\\N" or dest == "\\N":
                continue
            routes.append({
                'airline': airline,
                'source': (source),  
                'dest': (dest)      
            })
    return routes

def create_airport_country_mapping(airports):
    airport_country_mapping = {}
    for airport_id, info in airports.items():
        airport_country_mapping[airport_id] = info['country']
 
    return airport_country_mapping

def create_flight_graph(airports, routes):
    G = nx.DiGraph()

    airport_map = create_airport_country_mapping(airports)

     # Add nodes with airport codes as IDs
    for airport_id, info in airports.items():
        if not G.has_node(info['country']): 
            G.add_node(info['country'], name=info['name'], city=info['city'])


    for route in routes:
        source_airport = route['source']
        dest_airport = route['dest']

        source_info = airports.get(source_airport)
        dest_info = airports.get(dest_airport)

        # Ignore routes that reference airports not registered on the dataset
        if route['source'] not in airport_map or route['dest'] not in airport_map: 
            continue

        source_country = airport_map[route['source']]
        dest_country = airport_map[route['dest']]

        # Excludes internal flights
        if source_country == dest_country: 
            continue
        
        if source_info and dest_info:
            source_name = f"{source_country}"
            dest_name = f"{dest_country}"
            if G.has_edge(source_name, dest_name):
                G[source_name][dest_name]['weight'] += 1
            else:
                G.add_edge(source_name, dest_name, weight=1)

    return G

def plot_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=50, font_size=6, edge_color='gray')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()
    # plt.savefig("image.png", format="png", dpi=300)


def heaviest_edges(graph, n=10):

    edges_with_weights = [(source, target, graph[source][target]['weight'])
                          for source, target in graph.edges()]

    # Sort edges based on weight in descending order
    sorted_edges = sorted(edges_with_weights, key=lambda x: x[2], reverse=True)

    # Return the top n heaviest edges
    return sorted_edges[:n]


def find_nodes_with_degree_zero(graph, degree_type='in'):
    if degree_type == 'in':
        nodes_with_degree_zero = [node for node in graph.nodes() if graph.in_degree(node) == 0]
    elif degree_type == 'out':
        nodes_with_degree_zero = [node for node in graph.nodes() if graph.out_degree(node) == 0]
    else:
        raise ValueError("Invalid degree_type. Use 'in' or 'out'.")

    return nodes_with_degree_zero


def get_maximum_degree(graph):
    degrees = dict(graph.degree())
    max_degree = max(degrees.values())
    nodes_with_max_degree = [node for node, degree in degrees.items() if degree == max_degree]
    return max_degree, nodes_with_max_degree

def get_nodes_with_highest_degrees(graph):
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    max_in_degree_node = max(in_degrees, key=in_degrees.get)
    max_out_degree_node = max(out_degrees, key=out_degrees.get)

    max_in_degree_value = in_degrees[max_in_degree_node]
    max_out_degree_value = out_degrees[max_out_degree_node]

    return max_in_degree_node, max_out_degree_node, max_in_degree_value, max_out_degree_value

def find_heaviest_edge(graph):
    heaviest_edge = max(graph.edges(data=True), key=lambda x: x[2]['weight'])
    return heaviest_edge

def calculate_edge_weight(graph, source, target):
    if graph.has_edge(source, target):
        return graph[source][target]['weight']
    else:
        return None  # Edge does not exist
    
def get_heaviest_edges(graph, n=20):
    edges_with_weights = [(source, target, graph[source][target]['weight'])
                          for source, target in graph.edges()]

    # Sort edges based on weight in descending order
    sorted_edges = sorted(edges_with_weights, key=lambda x: x[2], reverse=True)

    # Return the top n heaviest edges
    return sorted_edges[:n]

def main():
    airports = load_airports('airports.dat')
    routes = load_routes('routes.dat')
    flight_graph = create_flight_graph(airports, routes)
    

    # Calculate and print interesting graph metrics
    print("Graph Metrics:")
    print(f"Number of nodes: {flight_graph.number_of_nodes()}")
    print(f"Number of edges: {flight_graph.number_of_edges()}")

    # Print the adjacency matrix
    print("\nAdjacency Matrix:")
    print(nx.adjacency_matrix(flight_graph).todense())

    in0 = find_nodes_with_degree_zero(flight_graph, degree_type='in')
    out0 = find_nodes_with_degree_zero(flight_graph, degree_type='out')
    print(in0)
    print(out0)

    max_degree = get_maximum_degree(flight_graph)
    print(f"The maximum degree in the graph is: {max_degree}")
    max_in_degree_node, max_out_degree_node, max_in_degree_value, max_out_degree_value = get_nodes_with_highest_degrees(flight_graph)
    print(f"The maximum in degree in the graph is: {max_in_degree_node} - {max_in_degree_value}")
    print(f"The maximum out degree in the graph is: {max_out_degree_node} - {max_out_degree_value}")

    print(f"Average in-degree: {sum(dict(flight_graph.in_degree()).values()) / flight_graph.number_of_nodes()}")
    print(f"Average out-degree: {sum(dict(flight_graph.out_degree()).values()) / flight_graph.number_of_nodes()}")

    nx.write_gexf(flight_graph, "grafo.gexf")


    # print(f"Diameter: {nx.diameter(flight_graph)}")

    # print(heaviest_edges(flight_graph))

    weak_conected_components = nx.number_weakly_connected_components(flight_graph)
    print(weak_conected_components)

    strong_conected_components = nx.number_strongly_connected_components(flight_graph)
    print(strong_conected_components)

    heaviest_edges_list = get_heaviest_edges(flight_graph, n=20)
    print("Top 20 Heaviest Edges:")
    for edge in heaviest_edges_list:
        print(edge)

    new_fligh_graph = flight_graph.copy()
    node_to_remove = "France"
    new_fligh_graph.remove_node(node_to_remove)


    weak_conected_components = nx.number_weakly_connected_components(new_fligh_graph)
    print(weak_conected_components)

    strong_conected_components = nx.number_strongly_connected_components(new_fligh_graph)
    print(strong_conected_components)

    # Plot the graph
    # plot_graph(flight_graph)

if __name__ == "__main__":
    main()
