"""
Graph utility functions for Apache AGE operations
"""
from sqlalchemy import create_engine, text
from config import Config

class GraphUtils:
    """Utility class for AGE graph operations"""
    
    def __init__(self, database_url, graph_name=None):
        self.engine = create_engine(database_url)
        self.graph_name = graph_name
        self.age_enabled = Config.AGE_ENABLED
    
    def execute_cypher(self, cypher_query, params=None):
        """Execute a Cypher query using AGE"""
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        if not self.graph_name:
            return {"error": "No graph selected"}
        
        try:
            with self.engine.connect() as conn:
                # Set the search path to include ag_catalog
                conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
                
                # Execute the Cypher query without parameter substitution
                # The text() function with no params will treat the query as-is
                if params:
                    result = conn.execute(text(cypher_query), params)
                else:
                    # Use raw connection to avoid bind parameter interpretation
                    result = conn.exec_driver_sql(cypher_query)
                conn.commit()
                
                # Convert Row objects to lists for JSON serialization
                rows = result.fetchall()
                serializable_rows = [list(row) for row in rows]
                
                return {"success": True, "result": serializable_rows}
        except Exception as e:
            return {"error": str(e)}
    
    def create_node(self, label, properties):
        """
        Create a node with the given label and properties
        
        Args:
            label: Node label (e.g., 'Person', 'Product')
            properties: Dictionary of properties
        
        Returns:
            Dictionary with success status and node info
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        # Build properties string with proper type handling
        props_list = []
        for k, v in properties.items():
            if isinstance(v, (int, float)):
                props_list.append(f"{k}: {v}")
            elif isinstance(v, bool):
                props_list.append(f"{k}: {str(v).lower()}")
            else:
                # String values need quotes, escape single quotes
                v_escaped = str(v).replace("'", "\\'") 
                props_list.append(f"{k}: '{v_escaped}'")
        props_str = ', '.join(props_list)
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            CREATE (n:{label} {{{props_str}}})
            RETURN n
        $$) as (node agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def create_edge(self, from_node_id, to_node_id, edge_label, properties=None):
        """
        Create an edge between two nodes
        
        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            edge_label: Edge label (e.g., 'KNOWS', 'PURCHASED')
            properties: Optional dictionary of edge properties
        
        Returns:
            Dictionary with success status and edge info
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        props_str = ""
        if properties:
            # Build properties string with proper type handling
            props_list = []
            for k, v in properties.items():
                if isinstance(v, (int, float)):
                    props_list.append(f"{k}: {v}")
                elif isinstance(v, bool):
                    props_list.append(f"{k}: {str(v).lower()}")
                else:
                    # String values need quotes, escape single quotes
                    v_escaped = str(v).replace("'", "\\'")
                    props_list.append(f"{k}: '{v_escaped}'")
            props_str = f" {{{', '.join(props_list)}}}"
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH (a), (b)
            WHERE id(a) = {from_node_id} AND id(b) = {to_node_id}
            CREATE (a)-[r:{edge_label}{props_str}]->(b)
            RETURN r
        $$) as (edge agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def update_node(self, node_id, properties):
        """
        Update a node's properties
        
        Args:
            node_id: ID of the node to update
            properties: Dictionary of properties to set
        
        Returns:
            Dictionary with success status
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        # Build SET clauses for properties with proper type handling
        set_clauses = []
        for k, v in properties.items():
            if isinstance(v, (int, float)):
                set_clauses.append(f"n.{k} = {v}")
            elif isinstance(v, bool):
                set_clauses.append(f"n.{k} = {str(v).lower()}")
            else:
                v_escaped = str(v).replace("'", "\\'")
                set_clauses.append(f"n.{k} = '{v_escaped}'")
        set_clauses_str = ', '.join(set_clauses)
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH (n)
            WHERE id(n) = {node_id}
            SET {set_clauses_str}
            RETURN n
        $$) as (node agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def update_edge(self, edge_id, properties):
        """
        Update an edge's properties
        
        Args:
            edge_id: ID of the edge to update
            properties: Dictionary of properties to set
        
        Returns:
            Dictionary with success status
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        # Build SET clauses for properties with proper type handling
        set_clauses = []
        for k, v in properties.items():
            if isinstance(v, (int, float)):
                set_clauses.append(f"r.{k} = {v}")
            elif isinstance(v, bool):
                set_clauses.append(f"r.{k} = {str(v).lower()}")
            else:
                v_escaped = str(v).replace("'", "\\'")
                set_clauses.append(f"r.{k} = '{v_escaped}'")
        set_clauses_str = ', '.join(set_clauses)
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH ()-[r]->()
            WHERE id(r) = {edge_id}
            SET {set_clauses_str}
            RETURN r
        $$) as (edge agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def delete_node(self, node_id):
        """
        Delete a node by ID
        
        Args:
            node_id: ID of the node to delete
        
        Returns:
            Dictionary with success status
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH (n)
            WHERE id(n) = {node_id}
            DETACH DELETE n
            RETURN true
        $$) as (result agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def delete_edge(self, edge_id):
        """
        Delete an edge by ID
        
        Args:
            edge_id: ID of the edge to delete
        
        Returns:
            Dictionary with success status
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH ()-[r]->()
            WHERE id(r) = {edge_id}
            DELETE r
            RETURN true
        $$) as (result agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def get_all_nodes(self, label=None, limit=None):
        """
        Get all nodes, optionally filtered by label
        
        Args:
            label: Optional node label to filter
            limit: Optional limit on number of nodes to return
        
        Returns:
            List of nodes
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        match_clause = f"(n:{label})" if label else "(n)"
        limit_clause = f" LIMIT {limit}" if limit else ""
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH {match_clause}
            RETURN n{limit_clause}
        $$) as (node agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def get_all_edges(self, label=None):
        """
        Get all edges with their source and target nodes, optionally filtered by label
        
        Args:
            label: Optional edge label to filter
        
        Returns:
            List of edges with source and target nodes
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        match_clause = f"-[r:{label}]->" if label else "-[r]->"
        
        cypher = f"""
        SELECT * FROM cypher('{self.graph_name}', $$
            MATCH (a){match_clause}(b)
            RETURN a, r, b
        $$) as (from_node agtype, edge agtype, to_node agtype);
        """
        
        return self.execute_cypher(cypher)
    
    def get_graph_data(self):
        """
        Get graph data for visualization (limited to 200 nodes max)
        
        Returns:
            Dictionary with nodes and edges
        """
        # Get up to 200 nodes for visualization
        nodes_result = self.get_all_nodes(limit=200)
        
        if "error" in nodes_result:
            return {
                "nodes": [],
                "edges": [],
                "error": nodes_result.get("error")
            }
        
        nodes = nodes_result.get("result", [])
        
        # If no nodes, return empty
        if not nodes:
            return {
                "nodes": [],
                "edges": [],
                "success": True
            }
        
        # Extract node IDs from the result
        try:
            import json
            node_ids = []
            for node in nodes:
                node_str = node[0].split('::')[0].strip()
                node_data = json.loads(node_str)
                node_ids.append(node_data['id'])
            
            # Get only edges between these nodes
            if node_ids:
                ids_str = ','.join(map(str, node_ids))
                cypher = f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    MATCH (a)-[r]->(b)
                    WHERE id(a) IN [{ids_str}] AND id(b) IN [{ids_str}]
                    RETURN a, r, b
                $$) as (from_node agtype, edge agtype, to_node agtype);
                """
                edges_result = self.execute_cypher(cypher)
            else:
                edges_result = {"result": []}
                
        except Exception as e:
            return {
                "nodes": nodes,
                "edges": [],
                "error": f"Error processing node IDs: {str(e)}"
            }
        
        if "error" in edges_result:
            return {
                "nodes": nodes,
                "edges": [],
                "error": edges_result.get("error")
            }
        
        return {
            "nodes": nodes,
            "edges": edges_result.get("result", []),
            "success": True
        }
    
    def list_graphs(self):
        """
        List all available graphs in the database
        
        Returns:
            List of graph names
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
                
                result = conn.execute(text("""
                    SELECT name FROM ag_graph
                """))
                
                graphs = [row[0] for row in result.fetchall()]
                return {"success": True, "graphs": graphs}
        except Exception as e:
            return {"error": str(e)}
    
    def create_graph(self, graph_name):
        """
        Create a new graph
        
        Args:
            graph_name: Name of the graph to create
        
        Returns:
            Dictionary with success status
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SET search_path = ag_catalog, '$user', public;"))
                conn.execute(text(f"SELECT create_graph('{graph_name}');"))
                conn.commit()
                return {"success": True, "message": f"Graph '{graph_name}' created successfully"}
        except Exception as e:
            if "already exists" in str(e):
                return {"error": f"Graph '{graph_name}' already exists"}
            return {"error": str(e)}
    
    def set_graph(self, graph_name):
        """Set the active graph name"""
        self.graph_name = graph_name
    
    def detect_anomalies(self):
        """
        Detect various types of anomalies in the graph
        
        Returns:
            Dictionary containing different types of anomalies
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        anomalies = {
            "isolated_nodes": [],
            "high_degree_nodes": [],
            "low_degree_nodes": [],
            "potential_missing_connections": [],
            "orphan_edges": []
        }
        
        # Store queries and raw results for debugging
        queries_info = []
        
        try:
            # Find isolated nodes (nodes with no connections)
            isolated_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) AS degree
                WHERE degree = 0
                RETURN n, id(n) as node_id, labels(n) as labels
            $$) as (node agtype, node_id agtype, labels agtype);
            """
            isolated_result = self.execute_cypher(isolated_query)
            
            # Store query info
            queries_info.append({
                'name': 'Isolated Nodes Detection',
                'description': 'Finds nodes that have no connections (edges) to any other node',
                'query': isolated_query.strip(),
                'raw_result': isolated_result.get('result', []) if isolated_result.get('success') else [],
                'error': isolated_result.get('error'),
                'count': len(isolated_result.get('result', [])) if isolated_result.get('success') else 0
            })
            
            if isolated_result.get('success'):
                for row in isolated_result.get('result', []):
                    try:
                        import json
                        node_str = str(row[0]).split('::')[0].strip()
                        node_data = json.loads(node_str)
                        anomalies['isolated_nodes'].append({
                            'id': node_data.get('id'),
                            'label': node_data.get('label'),
                            'properties': node_data.get('properties', {}),
                            'severity': 'medium',
                            'description': 'Node has no connections',
                            'raw_data': str(row[0])  # Include raw data for debugging
                        })
                    except Exception as e:
                        continue
            
            # Find nodes with unusually high degree (hub nodes)
            high_degree_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) AS degree
                WHERE degree > 10
                RETURN n, id(n) as node_id, labels(n) as labels, degree
                ORDER BY degree DESC
                LIMIT 20
            $$) as (node agtype, node_id agtype, labels agtype, degree agtype);
            """
            high_degree_result = self.execute_cypher(high_degree_query)
            
            queries_info.append({
                'name': 'High Degree Nodes (Hub Nodes)',
                'description': 'Finds nodes with more than 10 connections - potential hubs or bottlenecks',
                'query': high_degree_query.strip(),
                'raw_result': high_degree_result.get('result', []) if high_degree_result.get('success') else [],
                'error': high_degree_result.get('error'),
                'count': len(high_degree_result.get('result', [])) if high_degree_result.get('success') else 0
            })
            
            if high_degree_result.get('success'):
                for row in high_degree_result.get('result', []):
                    try:
                        import json
                        node_str = str(row[0]).split('::')[0].strip()
                        node_data = json.loads(node_str)
                        degree = int(str(row[3]))
                        anomalies['high_degree_nodes'].append({
                            'id': node_data.get('id'),
                            'label': node_data.get('label'),
                            'properties': node_data.get('properties', {}),
                            'degree': degree,
                            'severity': 'low',
                            'description': f'Node has {degree} connections - potential hub or bottleneck'
                        })
                    except Exception as e:
                        continue
            
            # Find nodes with exactly 1 connection (potential data quality issue)
            low_degree_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) AS degree
                WHERE degree = 1
                RETURN n, id(n) as node_id, labels(n) as labels, degree
                LIMIT 50
            $$) as (node agtype, node_id agtype, labels agtype, degree agtype);
            """
            low_degree_result = self.execute_cypher(low_degree_query)
            
            queries_info.append({
                'name': 'Low Degree Nodes',
                'description': 'Finds nodes with exactly 1 connection - may indicate incomplete data',
                'query': low_degree_query.strip(),
                'raw_result': low_degree_result.get('result', []) if low_degree_result.get('success') else [],
                'error': low_degree_result.get('error'),
                'count': len(low_degree_result.get('result', [])) if low_degree_result.get('success') else 0
            })
            
            if low_degree_result.get('success'):
                for row in low_degree_result.get('result', []):
                    try:
                        import json
                        node_str = str(row[0]).split('::')[0].strip()
                        node_data = json.loads(node_str)
                        anomalies['low_degree_nodes'].append({
                            'id': node_data.get('id'),
                            'label': node_data.get('label'),
                            'properties': node_data.get('properties', {}),
                            'degree': 1,
                            'severity': 'low',
                            'description': 'Node has only 1 connection - may be incomplete'
                        })
                    except Exception as e:
                        continue
            
            # Find potential missing connections (nodes with indirect but no direct connection)
            # This finds pairs of nodes that have 2-hop paths but no direct edge
            indirect_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (a)-[]-(m)-[]-(b)
                WHERE id(a) < id(b)
                WITH a, b, count(m) AS indirect_paths
                WHERE indirect_paths >= 2
                OPTIONAL MATCH (a)-[direct]-(b)
                WITH a, b, indirect_paths, count(direct) AS direct_count
                WHERE direct_count = 0
                RETURN a, b, indirect_paths
                ORDER BY indirect_paths DESC
                LIMIT 30
            $$) as (node_a agtype, node_b agtype, paths agtype);
            """
            indirect_result = self.execute_cypher(indirect_query)
            
            queries_info.append({
                'name': 'Potential Missing Connections',
                'description': 'Finds pairs of nodes connected by 2+ indirect paths but no direct edge',
                'query': indirect_query.strip(),
                'raw_result': indirect_result.get('result', []) if indirect_result.get('success') else [],
                'error': indirect_result.get('error'),
                'count': len(indirect_result.get('result', [])) if indirect_result.get('success') else 0
            })
            
            if indirect_result.get('success'):
                for row in indirect_result.get('result', []):
                    try:
                        import json
                        node_a_str = str(row[0]).split('::')[0].strip()
                        node_b_str = str(row[1]).split('::')[0].strip()
                        node_a = json.loads(node_a_str)
                        node_b = json.loads(node_b_str)
                        paths = int(str(row[2]))
                        
                        anomalies['potential_missing_connections'].append({
                            'node_a': {
                                'id': node_a.get('id'),
                                'label': node_a.get('label'),
                                'properties': node_a.get('properties', {})
                            },
                            'node_b': {
                                'id': node_b.get('id'),
                                'label': node_b.get('label'),
                                'properties': node_b.get('properties', {})
                            },
                            'indirect_paths': paths,
                            'severity': 'medium' if paths >= 3 else 'low',
                            'description': f'{paths} indirect path(s) exist but no direct connection'
                        })
                    except Exception as e:
                        continue
            
            return {
                "success": True, 
                "anomalies": anomalies,
                "queries": queries_info,
                "graph_name": self.graph_name
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def find_indirect_connections(self, node_id, max_depth=3):
        """
        Find indirect connections for a specific node
        
        Args:
            node_id: ID of the node to analyze
            max_depth: Maximum path length to search
        
        Returns:
            Dictionary with indirect connections and suggestions
        """
        if not self.age_enabled:
            return {"error": "AGE is not enabled"}
        
        if not node_id:
            return {"error": "node_id is required"}
        
        try:
            # Get the node details
            node_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                WHERE id(n) = {node_id}
                RETURN n, labels(n) as labels
            $$) as (node agtype, labels agtype);
            """
            node_result = self.execute_cypher(node_query)
            
            if not node_result.get('success') or not node_result.get('result'):
                return {"error": "Node not found"}
            
            # Find indirect connections
            indirect_query = f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (a)-[]-(m)-[]-(b)
                WHERE id(a) = {node_id}
                WITH a, b, count(m) AS path_count
                OPTIONAL MATCH (a)-[direct]-(b)
                WITH b, path_count, count(direct) AS direct_count
                WHERE direct_count = 0
                RETURN b, 2 AS distance, path_count
                ORDER BY path_count DESC
                LIMIT 30
            $$) as (node agtype, distance agtype, path_count agtype);
            """
            indirect_result = self.execute_cypher(indirect_query)
            
            suggestions = []
            if indirect_result.get('success'):
                for row in indirect_result.get('result', []):
                    try:
                        import json
                        node_str = str(row[0]).split('::')[0].strip()
                        node_data = json.loads(node_str)
                        distance = int(str(row[1]))
                        path_count = int(str(row[2]))
                        
                        suggestions.append({
                            'target_node': {
                                'id': node_data.get('id'),
                                'label': node_data.get('label'),
                                'properties': node_data.get('properties', {})
                            },
                            'distance': distance,
                            'path_count': path_count,
                            'suggestion': f'Consider adding a direct connection (found {path_count} indirect path(s) of length {distance})'
                        })
                    except Exception as e:
                        continue
            
            return {
                "success": True,
                "node_id": node_id,
                "suggestions": suggestions
            }
        
        except Exception as e:
            return {"error": str(e)}
