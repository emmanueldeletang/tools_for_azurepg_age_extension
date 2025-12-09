"""
Script to drop and recreate the social_network graph
This is useful for testing or resetting the graph to a clean state
"""
from sqlalchemy import create_engine, text
from config import Config
from create_social_network import create_social_network

def recreate_social_network():
    """Drop the existing social_network graph and create a new one"""
    
    print("Recreating social_network graph...")
    print("=" * 60)
    
    # Connect to database
    engine = create_engine(Config.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Set search path
            conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
            
            # Check if graph exists
            result = conn.execute(text("""
                SELECT name FROM ag_graph WHERE name = 'social_network'
            """))
            
            if result.fetchone():
                print("Dropping existing 'social_network' graph...")
                conn.execute(text("SELECT drop_graph('social_network', true);"))
                conn.commit()
                print("✓ Existing graph dropped\n")
            else:
                print("No existing 'social_network' graph found\n")
                
    except Exception as e:
        print(f"Error during graph recreation: {e}")
        return
    
    # Create new graph with data
    print("Creating new social_network graph with data...\n")
    create_social_network()

if __name__ == "__main__":
    recreate_social_network()
