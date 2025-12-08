"""
Script to create a 'road' graph with 25 cities connected by highways and normal roads
"""
import random
from utils.graph_utils import GraphUtils
from config import Config

# Initialize graph utilities
graph_utils = GraphUtils(Config.DATABASE_URL)

# List of 25 city names
cities = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Boston",
    "Portland", "Las Vegas", "Detroit", "Memphis", "Baltimore"
]

def create_road_graph():
    """Create the road graph with cities and roads"""
    print("Creating 'road' graph...")
    
    # Create the graph
    result = graph_utils.create_graph('road')
    if 'error' in result:
        if "already exists" in result['error']:
            print("Graph 'road' already exists. Using existing graph.")
        else:
            print(f"Error creating graph: {result['error']}")
            return
    else:
        print(result['message'])
    
    # Set the active graph
    graph_utils.set_graph('road')
    
    # Create city nodes
    print(f"\nCreating {len(cities)} city nodes...")
    city_ids = {}
    
    for i, city in enumerate(cities, 1):
        population = random.randint(50000, 5000000)
        result = graph_utils.create_node('City', {
            'name': city,
            'population': population,
            'state': 'USA'
        })
        
        if result.get('success'):
            # Extract node ID from result
            node_data = result['result'][0][0].split('::')[0]
            import json
            node = json.loads(node_data)
            city_ids[city] = node['id']
            print(f"  ✓ Created {city} (ID: {node['id']}, Population: {population:,})")
        else:
            print(f"  ✗ Error creating {city}: {result.get('error')}")
    
    # Create connections between cities
    print(f"\nCreating road connections...")
    
    # Create a network of roads - each city connects to 2-4 other cities
    connections_created = 0
    road_types = ['Highway', 'Normal']
    
    for city in cities:
        if city not in city_ids:
            continue
            
        # Pick 2-4 random cities to connect to
        num_connections = random.randint(2, 4)
        target_cities = random.sample([c for c in cities if c != city], num_connections)
        
        for target_city in target_cities:
            if target_city not in city_ids:
                continue
            
            # Check if connection already exists (avoid duplicates)
            # For simplicity, we'll create connections anyway
            
            # Random road type
            road_type = random.choice(road_types)
            
            # Generate realistic parameters based on road type
            if road_type == 'Highway':
                km = random.randint(50, 500)
                time = round(km / random.uniform(80, 120), 1)  # 80-120 km/h
            else:  # Normal road
                km = random.randint(20, 200)
                time = round(km / random.uniform(40, 60), 1)  # 40-60 km/h
            
            result = graph_utils.create_edge(
                city_ids[city],
                city_ids[target_city],
                road_type,
                {
                    'km': km,
                    'time': time,
                    'from': city,
                    'to': target_city
                }
            )
            
            if result.get('success'):
                connections_created += 1
                print(f"  ✓ {city} --[{road_type} {km}km, {time}h]--> {target_city}")
            else:
                print(f"  ✗ Error creating road from {city} to {target_city}: {result.get('error')}")
    
    print(f"\n{'='*60}")
    print(f"Graph creation completed!")
    print(f"  - Cities created: {len(city_ids)}")
    print(f"  - Roads created: {connections_created}")
    print(f"{'='*60}")
    print("\nYou can now select the 'road' graph from the web interface to visualize and query it.")

if __name__ == '__main__':
    try:
        create_road_graph()
    except Exception as e:
        print(f"Error: {e}")
