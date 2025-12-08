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
                
                # Execute the Cypher query
                result = conn.execute(text(cypher_query), params or {})
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
