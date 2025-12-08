"""
OpenAI helper for translating natural language to Cypher queries
Supports both Azure OpenAI and standard OpenAI
"""
import os
from openai import AzureOpenAI, OpenAI

class OpenAIHelper:
    """Helper class for OpenAI integration"""
    
    def __init__(self, azure_endpoint=None, azure_api_key=None, azure_deployment=None, azure_api_version=None, graph_utils=None):
        """
        Initialize OpenAI helper with Azure OpenAI configuration
        
        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            azure_api_key: Azure OpenAI API key
            azure_deployment: Azure OpenAI deployment name
            azure_api_version: Azure OpenAI API version
            graph_utils: GraphUtils instance for accessing graph data
        """
        self.azure_endpoint = azure_endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_api_key = azure_api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_deployment = azure_deployment or os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
        self.azure_api_version = azure_api_version or os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
        self.graph_utils = graph_utils
        
        if not self.azure_endpoint or not self.azure_api_key:
            raise ValueError("Azure OpenAI endpoint and API key are required")
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.azure_api_key,
            api_version=self.azure_api_version
        )
        self.is_azure = True
    
    def natural_language_to_cypher(self, natural_query, graph_schema=None, graph_name=None):
        """
        Convert natural language query to Apache AGE SQL
        
        Args:
            natural_query: The natural language query from user
            graph_schema: Optional schema information about the graph
            graph_name: Name of the graph for the query
        
        Returns:
            Dictionary with cypher query and explanation
        """
        schema_context = ""
        if graph_schema:
            schema_context = f"\n\nGraph Schema Information:\n{graph_schema}"
        
        if graph_name:
            schema_context += f"\n\nCurrent Graph Name: {graph_name}\nUSE THIS GRAPH NAME in your query."
        
        system_prompt = f"""You are an expert in converting natural language queries to Apache AGE SQL queries for PostgreSQL.

CRITICAL RULES FOR APACHE AGE:
- NEVER use double-dash syntax: (n)--() is FORBIDDEN
- ALWAYS use brackets for relationships: (n)-[r]-() or (n)-[r:TYPE]->()
- NEVER use size() function on graph patterns - it's not supported in Apache AGE
- For counting relationships: MATCH (n)-[r]-() WITH n, count(r) as rel_count WHERE rel_count > X RETURN n
- Apache AGE does NOT support pipe syntax for multiple types: (a)-[r:TYPE1|TYPE2]-(b) is INVALID

IMPORTANT - Query Format:
- You MUST generate the COMPLETE AGE SQL query including the SELECT wrapper
- Format: SELECT * FROM cypher('graph_name', $$ CYPHER_QUERY $$) AS (col1 agtype, col2 agtype, ...);
- The column definition list MUST EXACTLY match the number and order of values in the RETURN clause
- Use current graph name from context

Query Guidelines:
- Generate valid OpenCypher queries compatible with Apache AGE
- Use MATCH, WHERE, RETURN, CREATE, DELETE, SET as needed
- For property access, use dot notation: n.property_name
- For undirected relationships: (a)-[r]-(b)
- For directed relationships: (a)-[r]->(b) or (a)<-[r]-(b)
- For any relationship type, use untyped patterns: (a)-[r]->(b) or (a)-[r*1..5]-(b)
- To match multiple relationship types, use WHERE clause: (a)-[r]-(b) WHERE r.label = 'TYPE1' OR r.label = 'TYPE2'
- Always return clear, readable queries
- If the query is ambiguous, make reasonable assumptions
- Use LIMIT when appropriate to avoid returning too much data

Shortest Path Queries (for graphs with distance/time properties):
- Use variable-length path patterns: (a)-[*1..6]-(b) for up to 6 hops (matches ANY relationship type)
- For path analysis with properties, use: MATCH paths = (a)-[r*1..6]-(b) WITH paths, relationships(paths) AS rels
- Then UNWIND and aggregate: UNWIND rels AS rel WITH nodes(paths) AS nodes, sum(rel.property) AS total
- Order by total distance/time: ORDER BY total

Examples of CORRECT queries:
- Find nodes: SELECT * FROM cypher('graph_name', $$ MATCH (n) RETURN n LIMIT 10 $$) AS (node agtype);
- Nodes with connections: SELECT * FROM cypher('graph_name', $$ MATCH (n)-[r]-() WITH n, count(r) as connections WHERE connections > 2 RETURN n, connections $$) AS (node agtype, connections agtype);
- Shortest path: SELECT * FROM cypher('graph_name', $$ MATCH paths = (a:City {{name: 'A'}})-[r*1..6]-(b:City {{name: 'B'}}) WITH paths, relationships(paths) AS rels UNWIND rels AS rel WITH nodes(paths) AS nodes, sum(rel.time) AS totalTime RETURN nodes, totalTime ORDER BY totalTime LIMIT 5 $$) AS (nodes agtype, totalTime agtype);
{schema_context}

Respond with a JSON object containing:
1. "cypher": The COMPLETE AGE SQL query (including SELECT wrapper and column definitions)
2. "explanation": A brief explanation of what the query does
3. "assumptions": Any assumptions made (if applicable)

Example response format:
{{
    "cypher": "SELECT * FROM cypher('graph_name', $$ MATCH (n:Person) WHERE n.age > 25 RETURN n $$) AS (person agtype);",
    "explanation": "This query finds all Person nodes where age is greater than 25",
    "assumptions": "Assumed you want all matching persons"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.azure_deployment if self.is_azure else "gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": natural_query}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "cypher": result.get("cypher", ""),
                "explanation": result.get("explanation", ""),
                "assumptions": result.get("assumptions", "")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_graph_schema_summary(self):
        """
        Generate a summary of the graph schema for context by loading data from the graph
        
        Returns:
            String summary of the graph schema
        """
        try:
            import json
            
            # Load graph data using graph_utils
            if not self.graph_utils:
                return "Error: GraphUtils not configured"
            
            graph_data = self.graph_utils.get_graph_data()
            
            if "error" in graph_data:
                return f"Error loading graph data: {graph_data.get('error')}"
            
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            # Extract unique node labels and properties
            node_labels = {}
            for node in nodes[:50]:  # Sample first 50 nodes
                try:
                    node_str = node[0].split('::')[0].strip()
                    node_data = json.loads(node_str)
                    label = node_data.get('label', 'Unknown')
                    properties = node_data.get('properties', {})
                    
                    if label not in node_labels:
                        node_labels[label] = set()
                    node_labels[label].update(properties.keys())
                except:
                    continue
            
            # Extract unique edge labels and properties
            edge_labels = {}
            for edge in edges[:50]:  # Sample first 50 edges
                try:
                    # Edges are returned as [from_node, edge, to_node]
                    # We need the edge which is at index 1
                    edge_str = edge[1].split('::')[0].strip()
                    edge_data = json.loads(edge_str)
                    label = edge_data.get('label', 'Unknown')
                    properties = edge_data.get('properties', {})
                    
                    if label not in edge_labels:
                        edge_labels[label] = set()
                    edge_labels[label].update(properties.keys())
                except Exception as e:
                    # Skip edges that can't be parsed
                    continue
            
            # Build schema summary
            schema = "Node Types:\n"
            for label, props in node_labels.items():
                schema += f"  - {label}: properties = {{{', '.join(sorted(props))}}}\n"
            
            schema += "\nRelationship Types:\n"
            for label, props in edge_labels.items():
                props_str = f": properties = {{{', '.join(sorted(props))}}}" if props else ""
                schema += f"  - {label}{props_str}\n"
            
            return schema
        except Exception as e:
            return f"Error generating schema: {str(e)}"
