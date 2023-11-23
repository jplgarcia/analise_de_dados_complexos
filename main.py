import networkx as nx
import matplotlib.pyplot as plt
import csv

def load_airports(filename):
    airports = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            airport_id, name, city, country, code, _, latitude, longitude, *_ = row
            airports[code] = {
                'name': name,
                'city': city,
                'country': country,
                'code': code,
                'latitude': float(latitude),
                'longitude': float(longitude)
            }
    return airports

def load_routes(filename):
    routes = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            airline, _, source, _, dest, _, _, _, _ = row
            routes.append({
                'airline': airline,
                'source': source,  # Treat as string
                'dest': dest      # Treat as string
            })
    return routes

def create_flight_graph(airports, routes):
    G = nx.DiGraph()

     # Add nodes with airport codes as IDs
    for airport_id, info in airports.items():
        G.add_node(info['code'], name=info['name'], city=info['city'], country=info['country'])


    for route in routes:
        source_airport = route['source']
        dest_airport = route['dest']
        source_info = airports.get(source_airport)
        dest_info = airports.get(dest_airport)

        if source_info and dest_info:
            source_name = f"{source_info['code']}"
            dest_name = f"{dest_info['code']}"
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

def heaviest_edges(graph, n=10):

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

    # print(f"Average in-degree: {sum(dict(flight_graph.in_degree()).values()) / flight_graph.number_of_nodes()}")
    # print(f"Average out-degree: {sum(dict(flight_graph.out_degree()).values()) / flight_graph.number_of_nodes()}")
    # print(f"Diameter: {nx.diameter(flight_graph)}")

    print(heaviest_edges(flight_graph))

    # Plot the graph
    # plot_graph(flight_graph)

if __name__ == "__main__":
    main()
