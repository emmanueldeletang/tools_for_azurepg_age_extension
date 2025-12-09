"""
Script to create a social network graph with:
- 100 Person nodes (name, age, city)
- 10 Sport nodes
- 10 Company nodes
- Edges: PRACTICE, LIKE (Person -> Sport)
- Edges: WORKS_AT (Person -> Company)
- Edges: FRIENDS, COWORKER (Person -> Person)
"""
import random
from utils.graph_utils import GraphUtils
from config import Config

# Sample data
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Catherine", "Patrick", "Carolyn", "Jack", "Janet",
    "Dennis", "Ruth", "Jerry", "Maria", "Tyler", "Heather", "Aaron", "Diane"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
    "Denver", "Washington", "Boston", "Nashville", "Detroit", "Portland", "Las Vegas",
    "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno",
    "Mesa", "Sacramento", "Atlanta", "Kansas City", "Colorado Springs", "Miami", "Raleigh",
    "Omaha", "Long Beach", "Virginia Beach", "Oakland", "Minneapolis", "Tampa", "Tulsa"
]

SPORTS = [
    "Soccer", "Basketball", "Tennis", "Swimming", "Running", 
    "Cycling", "Golf", "Volleyball", "Baseball", "Boxing"
]

COMPANIES = [
    "Tech Innovations Inc", "Global Solutions Corp", "Digital Dynamics LLC",
    "Enterprise Systems Group", "Cloud Services International", "Data Analytics Pro",
    "Software Development Hub", "Cyber Security Experts", "AI Research Labs",
    "Mobile Technologies United"
]

def create_social_network():
    """Create a comprehensive social network graph"""
    
    # Initialize graph utilities
    graph_utils = GraphUtils(Config.DATABASE_URL)
    
    print("Creating 'social_network' graph...")
    result = graph_utils.create_graph("social_network")
    if "error" in result and "already exists" not in result["error"]:
        print(f"Error creating graph: {result['error']}")
        return
    
    graph_utils.set_graph("social_network")
    print("Graph 'social_network' is ready.\n")
    
    # Create 100 Person nodes
    print("Creating 100 Person nodes...")
    person_ids = []
    for i in range(100):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        age = random.randint(22, 65)
        city = random.choice(CITIES)
        
        result = graph_utils.create_node("Person", {
            "name": name,
            "age": age,
            "city": city
        })
        
        if result.get("success"):
            # Extract node ID from result
            import json
            node_str = result["result"][0][0].split('::')[0].strip()
            node_data = json.loads(node_str)
            person_ids.append(node_data['id'])
            
            if (i + 1) % 20 == 0:
                print(f"  Created {i + 1} persons...")
        else:
            print(f"  Error creating person: {result.get('error')}")
    
    print(f"✓ Created {len(person_ids)} Person nodes\n")
    
    # Create 10 Sport nodes
    print("Creating 10 Sport nodes...")
    sport_ids = []
    for sport in SPORTS:
        result = graph_utils.create_node("Sport", {
            "name": sport,
            "category": "Outdoor" if sport in ["Soccer", "Running", "Cycling", "Golf"] else "Indoor"
        })
        
        if result.get("success"):
            import json
            node_str = result["result"][0][0].split('::')[0].strip()
            node_data = json.loads(node_str)
            sport_ids.append(node_data['id'])
    
    print(f"✓ Created {len(sport_ids)} Sport nodes\n")
    
    # Create 10 Company nodes
    print("Creating 10 Company nodes...")
    company_ids = []
    for company in COMPANIES:
        result = graph_utils.create_node("Company", {
            "name": company,
            "employees": random.randint(50, 500),
            "industry": random.choice(["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"])
        })
        
        if result.get("success"):
            import json
            node_str = result["result"][0][0].split('::')[0].strip()
            node_data = json.loads(node_str)
            company_ids.append(node_data['id'])
    
    print(f"✓ Created {len(company_ids)} Company nodes\n")
    
    # Create PRACTICE and LIKE edges (Person -> Sport)
    print("Creating Person -> Sport relationships...")
    sport_edges = 0
    for person_id in person_ids:
        # Each person practices 1-3 sports
        num_practice = random.randint(1, 3)
        practiced_sports = random.sample(sport_ids, num_practice)
        
        for sport_id in practiced_sports:
            result = graph_utils.create_edge(
                person_id, sport_id, "PRACTICE",
                {
                    "years": random.randint(1, 20),
                    "skill_level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"])
                }
            )
            if result.get("success"):
                sport_edges += 1
        
        # Each person likes 1-4 sports (may overlap with practiced)
        num_like = random.randint(1, 4)
        liked_sports = random.sample(sport_ids, num_like)
        
        for sport_id in liked_sports:
            result = graph_utils.create_edge(
                person_id, sport_id, "LIKE",
                {
                    "interest_level": random.randint(1, 10)
                }
            )
            if result.get("success"):
                sport_edges += 1
    
    print(f"✓ Created {sport_edges} Person->Sport relationships (PRACTICE, LIKE)\n")
    
    # Create WORKS_AT edges (Person -> Company)
    print("Creating Person -> Company relationships...")
    work_edges = 0
    for person_id in person_ids:
        # Each person works at one company
        company_id = random.choice(company_ids)
        result = graph_utils.create_edge(
            person_id, company_id, "WORKS_AT",
            {
                "position": random.choice(["Engineer", "Manager", "Analyst", "Designer", "Developer", "Consultant"]),
                "years": random.randint(1, 15),
                "salary": random.randint(50000, 150000)
            }
        )
        if result.get("success"):
            work_edges += 1
    
    print(f"✓ Created {work_edges} Person->Company relationships (WORKS_AT)\n")
    
    # Create FRIENDS edges (Person -> Person)
    print("Creating Person -> Person FRIENDS relationships...")
    friends_edges = 0
    for person_id in person_ids:
        # Each person has 3-8 friends
        num_friends = random.randint(3, 8)
        # Avoid self-friendship and ensure unique friends
        possible_friends = [pid for pid in person_ids if pid != person_id]
        friends = random.sample(possible_friends, min(num_friends, len(possible_friends)))
        
        for friend_id in friends:
            result = graph_utils.create_edge(
                person_id, friend_id, "FRIENDS",
                {
                    "since": random.randint(2010, 2024),
                    "closeness": random.randint(1, 10)
                }
            )
            if result.get("success"):
                friends_edges += 1
    
    print(f"✓ Created {friends_edges} Person->Person relationships (FRIENDS)\n")
    
    # Create COWORKER edges (Person -> Person)
    # Group people by company and create coworker relationships
    print("Creating Person -> Person COWORKER relationships...")
    coworker_edges = 0
    
    # First, group people by company
    company_employees = {}
    for person_id in person_ids:
        # Find which company this person works at
        result = graph_utils.execute_cypher(f"""
            SELECT * FROM cypher('social_network', $$
                MATCH (p)-[w:WORKS_AT]->(c:Company)
                WHERE id(p) = {person_id}
                RETURN c
            $$) as (company agtype);
        """)
        
        if result.get("success") and result.get("result"):
            import json
            company_str = result["result"][0][0].split('::')[0].strip()
            company_data = json.loads(company_str)
            company_id = company_data['id']
            
            if company_id not in company_employees:
                company_employees[company_id] = []
            company_employees[company_id].append(person_id)
    
    # Create coworker relationships within each company
    for company_id, employees in company_employees.items():
        if len(employees) > 1:
            # Each person is coworker with 2-5 others in the same company
            for person_id in employees:
                num_coworkers = min(random.randint(2, 5), len(employees) - 1)
                possible_coworkers = [pid for pid in employees if pid != person_id]
                coworkers = random.sample(possible_coworkers, min(num_coworkers, len(possible_coworkers)))
                
                for coworker_id in coworkers:
                    result = graph_utils.create_edge(
                        person_id, coworker_id, "COWORKER",
                        {
                            "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Operations"]),
                            "collaboration_score": random.randint(1, 10)
                        }
                    )
                    if result.get("success"):
                        coworker_edges += 1
    
    print(f"✓ Created {coworker_edges} Person->Person relationships (COWORKER)\n")
    
    # Summary
    print("=" * 60)
    print("SOCIAL NETWORK GRAPH CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Nodes:")
    print(f"  - Person nodes: {len(person_ids)}")
    print(f"  - Sport nodes: {len(sport_ids)}")
    print(f"  - Company nodes: {len(company_ids)}")
    print(f"\nEdges:")
    print(f"  - Person->Sport (PRACTICE, LIKE): {sport_edges}")
    print(f"  - Person->Company (WORKS_AT): {work_edges}")
    print(f"  - Person->Person (FRIENDS): {friends_edges}")
    print(f"  - Person->Person (COWORKER): {coworker_edges}")
    print(f"\nTotal edges: {sport_edges + work_edges + friends_edges + coworker_edges}")
    print("=" * 60)
    
    print("\nExample queries you can try:")
    print("  - 'Show all people who practice Soccer'")
    print("  - 'Find friends of John Smith'")
    print("  - 'Show all employees at Tech Innovations Inc'")
    print("  - 'Find people who work at the same company and are friends'")
    print("  - 'Show coworkers who also practice the same sport'")
    print("  - 'Find people in New York who like Basketball'")

if __name__ == "__main__":
    create_social_network()
