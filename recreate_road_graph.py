"""
Script to drop and recreate the road graph with proper numeric values
"""
from utils.graph_utils import GraphUtils
from config import Config
from sqlalchemy import create_engine, text

# Initialize graph utilities
graph_utils = GraphUtils(Config.DATABASE_URL)

def drop_road_graph():
    """Drop the road graph if it exists"""
    print("Dropping 'road' graph if it exists...")
    try:
        engine = create_engine(Config.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
            conn.execute(text("SELECT drop_graph('road', true);"))
            conn.commit()
            print("✓ Graph 'road' dropped successfully")
    except Exception as e:
        print(f"Note: {e}")
        print("(This is normal if the graph doesn't exist)")

if __name__ == '__main__':
    try:
        drop_road_graph()
        print("\nNow run: python create_road_graph.py")
    except Exception as e:
        print(f"Error: {e}")
