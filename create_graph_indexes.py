"""
Script to analyze all graphs and generate optimized indexes for Apache AGE
Creates BTREE indexes for ID fields and GIN indexes for JSON properties
"""
from sqlalchemy import create_engine, text
from config import Config

def analyze_and_create_indexes():
    """Analyze all graphs and create recommended indexes"""
    engine = create_engine(Config.DATABASE_URL)
    
    print("=" * 80)
    print("Apache AGE Index Creation Script")
    print("=" * 80)
    
    try:
        with engine.connect() as conn:
            # Set search path
            conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
            
            # Get all graphs
            result = conn.execute(text("SELECT name FROM ag_graph;"))
            graphs = [row[0] for row in result.fetchall()]
            
            if not graphs:
                print("\nNo graphs found in the database.")
                return
            
            print(f"\nFound {len(graphs)} graph(s): {', '.join(graphs)}")
            print("\n" + "=" * 80)
            
            for graph_name in graphs:
                print(f"\n📊 Analyzing graph: '{graph_name}'")
                print("-" * 80)
                
                # Get all vertex labels (node types)
                try:
                    vertex_result = conn.execute(text(f"""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = '{graph_name}'
                        AND table_name LIKE '%\\_vertex'
                        AND table_type = 'BASE TABLE';
                    """))
                    vertex_tables = [row[0] for row in vertex_result.fetchall()]
                    
                    # Get all edge labels (relationship types)
                    edge_result = conn.execute(text(f"""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = '{graph_name}'
                        AND table_name LIKE '%\\_edge'
                        AND table_type = 'BASE TABLE';
                    """))
                    edge_tables = [row[0] for row in edge_result.fetchall()]
                    
                    print(f"\n  Vertex tables found: {len(vertex_tables)}")
                    for table in vertex_tables:
                        print(f"    • {table}")
                    
                    print(f"\n  Edge tables found: {len(edge_tables)}")
                    for table in edge_tables:
                        print(f"    • {table}")
                    
                    # Create indexes for vertex tables
                    if vertex_tables:
                        print("\n  Creating indexes for VERTEX tables...")
                        for table in vertex_tables:
                            try:
                                # Check if indexes already exist
                                check_result = conn.execute(text(f"""
                                    SELECT indexname 
                                    FROM pg_indexes 
                                    WHERE schemaname = '{graph_name}' 
                                    AND tablename = '{table}';
                                """))
                                existing_indexes = [row[0] for row in check_result.fetchall()]
                                
                                # Create BTREE index on id
                                btree_index_name = f"{table}_id_btree_idx"
                                if btree_index_name not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{btree_index_name}" 
                                        ON "{graph_name}"."{table}" 
                                        USING BTREE (id);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created BTREE index on {table}.id")
                                else:
                                    print(f"    ⊙ BTREE index on {table}.id already exists")
                                
                                # Create GIN index on properties
                                gin_index_name = f"{table}_properties_gin_idx"
                                if gin_index_name not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{gin_index_name}" 
                                        ON "{graph_name}"."{table}" 
                                        USING GIN (properties);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created GIN index on {table}.properties")
                                else:
                                    print(f"    ⊙ GIN index on {table}.properties already exists")
                                
                            except Exception as e:
                                print(f"    ✗ Error creating indexes for {table}: {e}")
                                conn.rollback()
                    
                    # Create indexes for edge tables
                    if edge_tables:
                        print("\n  Creating indexes for EDGE tables...")
                        for table in edge_tables:
                            try:
                                # Check if indexes already exist
                                check_result = conn.execute(text(f"""
                                    SELECT indexname 
                                    FROM pg_indexes 
                                    WHERE schemaname = '{graph_name}' 
                                    AND tablename = '{table}';
                                """))
                                existing_indexes = [row[0] for row in check_result.fetchall()]
                                
                                # Create BTREE index on id
                                btree_id_index = f"{table}_id_btree_idx"
                                if btree_id_index not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{btree_id_index}" 
                                        ON "{graph_name}"."{table}" 
                                        USING BTREE (id);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created BTREE index on {table}.id")
                                else:
                                    print(f"    ⊙ BTREE index on {table}.id already exists")
                                
                                # Create BTREE index on start_id
                                btree_start_index = f"{table}_start_id_btree_idx"
                                if btree_start_index not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{btree_start_index}" 
                                        ON "{graph_name}"."{table}" 
                                        USING BTREE (start_id);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created BTREE index on {table}.start_id")
                                else:
                                    print(f"    ⊙ BTREE index on {table}.start_id already exists")
                                
                                # Create BTREE index on end_id
                                btree_end_index = f"{table}_end_id_btree_idx"
                                if btree_end_index not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{btree_end_index}" 
                                        ON "{graph_name}"."{table}" 
                                        USING BTREE (end_id);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created BTREE index on {table}.end_id")
                                else:
                                    print(f"    ⊙ BTREE index on {table}.end_id already exists")
                                
                                # Create GIN index on properties
                                gin_index_name = f"{table}_properties_gin_idx"
                                if gin_index_name not in existing_indexes:
                                    conn.execute(text(f'''
                                        CREATE INDEX "{gin_index_name}" 
                                        ON "{graph_name}"."{table}" 
                                        USING GIN (properties);
                                    '''))
                                    conn.commit()
                                    print(f"    ✓ Created GIN index on {table}.properties")
                                else:
                                    print(f"    ⊙ GIN index on {table}.properties already exists")
                                
                            except Exception as e:
                                print(f"    ✗ Error creating indexes for {table}: {e}")
                                conn.rollback()
                    
                except Exception as e:
                    print(f"  ✗ Error analyzing graph '{graph_name}': {e}")
                    continue
            
            print("\n" + "=" * 80)
            print("Index creation completed!")
            print("=" * 80)
            
            # Show summary
            print("\n📈 Index Summary:")
            print("\nFor each VERTEX table, the following indexes are created:")
            print("  1. BTREE index on 'id' - Fast exact match and range queries")
            print("  2. GIN index on 'properties' - Efficient JSON property searches")
            
            print("\nFor each EDGE table, the following indexes are created:")
            print("  1. BTREE index on 'id' - Fast exact match and range queries")
            print("  2. BTREE index on 'start_id' - Fast source node lookups")
            print("  3. BTREE index on 'end_id' - Fast target node lookups")
            print("  4. GIN index on 'properties' - Efficient JSON property searches")
            
            print("\n💡 Benefits:")
            print("  • Faster node lookups by ID")
            print("  • Improved relationship traversal performance")
            print("  • Efficient queries on node/edge properties")
            print("  • Better performance for path finding and pattern matching")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == '__main__':
    try:
        analyze_and_create_indexes()
    except Exception as e:
        print(f"Fatal error: {e}")
