# Flask Apache AGE Graph Database Manager

A comprehensive Flask web application for managing Apache AGE graph databases in PostgreSQL. This application provides a user-friendly interface to create, manage, and visualize graph data with AI-powered natural language query capabilities.

## Features

- 🌐 **Web UI**: Modern, responsive interface built with Bootstrap 5
- 📊 **Node Management**: Create, update, and delete nodes with labels and custom properties
- 🔗 **Edge Management**: Create, update, and delete relationships (edges) between nodes with properties
- 📈 **Interactive Graph Visualization**: Real-time graph visualization using vis.js with dynamic colors
- 🤖 **AI-Powered Natural Language Queries**: Ask questions in plain English (powered by Azure OpenAI)
  - Automatic query generation from natural language
  - Edit generated queries before execution
  - View results in table or interactive graph format
- 🎯 **Smart Property Handling**: Automatic type detection for numeric, boolean, and string values
- 🗂️ **Multi-Graph Support**: Create and switch between multiple graphs
- 🔧 **RESTful API**: Complete JSON API for programmatic access
- 🎨 **Dynamic Colors**: Auto-generated unique colors for different node and edge types
- ⚡ **Performance Optimization**: Built-in index creation for faster queries
- 📍 **Shortest Path Queries**: Find optimal paths in road networks or any connected graph

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ with Apache AGE extension installed
- Azure OpenAI account (for natural language queries)
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update with your credentials:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database
   AGE_ENABLED=true
   
   # Azure OpenAI Configuration (for Natural Language Queries)
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   ```

6. **Initialize the database**
   ```bash
   python database/init_graph.py
   ```

## Usage

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://localhost:5000`

3. **Create nodes**
   - Go to "Nodes" section
   - Enter a label (e.g., Person, Product, City)
   - Add properties as JSON with automatic type detection:
     ```json
     {
       "name": "Alice",
       "age": 30,
       "salary": 75000.50,
       "active": true
     }
     ```
   - Numeric values (integers/floats) and booleans are stored correctly without quotes
   - Click "Create Node"

4. **Create edges**
   - Go to "Edges" section
   - Enter source and target node IDs
   - Enter edge label (e.g., KNOWS, PURCHASED, Highway, Normal)
   - Add properties with type support:
     ```json
     {
       "km": 250,
       "time": 2.5,
       "toll": false
     }
     ```
   - Click "Create Edge"

5. **Visualize the graph**
   - Go to "Graph Visualization" to see an interactive view of your graph

6. **Query with Natural Language** (powered by Azure OpenAI)
   - Go to "Natural Language Query"
   - Type your question in plain English:
     - "Find all people older than 30"
     - "Show shortest path between New York and Los Angeles"
     - "Count all Highway edges"
   - Click "Translate to Cypher" to see the generated query
   - **Edit the query** if needed before execution
   - Click "Execute Query" to see results
   - **Toggle between two views**:
     - **Table View**: Traditional tabular display
     - **Graph View**: Interactive network visualization powered by vis.js

### Demo Data: Road Network Graph

Generate a sample road network with 25 US cities:

```bash
python create_road_graph.py
```

This creates a `road` graph with:
- 25 City nodes (New York, Los Angeles, Chicago, Miami, etc.)
- Properties: name, population, state
- Highway edges: 50-500 km, 0.5-5 hours travel time
- Normal road edges: 20-200 km, 0.5-4 hours travel time
- 2-4 connections per city for realistic network topology

**To recreate from scratch:**
```bash
python recreate_road_graph.py
```

**Example natural language queries for the road graph:**
- "Find shortest path between New York and Los Angeles"
- "Show all cities connected to Chicago"
- "What highways have distance greater than 300 km?"
- "Find all roads with time less than 2 hours"

### Performance Optimization: Index Creation

Analyze all graphs and create optimized indexes:

```bash
python create_graph_indexes.py
```

This automated script:
- Discovers all vertex and edge tables across all graphs
- Creates **BTREE indexes** on `id`, `start_id`, `end_id` columns for fast lookups
- Creates **GIN indexes** on `properties` JSONB columns for property queries
- Checks for existing indexes to avoid duplicates
- Significantly improves query performance, especially for large graphs

## Project Structure

```
grapgenric/
├── app.py                      # Main Flask application with REST API
├── config.py                   # Configuration settings (DB, Azure OpenAI)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── create_road_graph.py       # Demo road network generator (25 cities)
├── recreate_road_graph.py     # Drop and recreate road graph script
├── create_graph_indexes.py    # Automated index creation for all graphs
├── database/
│   └── init_graph.py          # Database initialization script
├── utils/
│   ├── graph_utils.py         # AGE graph utilities with smart type handling
│   └── openai_helper.py       # Azure OpenAI integration for NL to Cypher
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html              # Base template with Bootstrap 5
│   ├── index.html             # Home page with graph management
│   ├── nodes.html             # Node CRUD operations
│   ├── edges.html             # Edge CRUD operations
│   ├── graph.html             # Graph visualization page
│   └── query.html             # NL query interface with dual view (table/graph)
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom styles
    └── js/
        └── main.js            # Client-side JavaScript
```

## API Endpoints

### Graph Management
- `GET /api/graphs` - List all available graphs
- `POST /api/graphs` - Create a new graph
- `POST /api/graphs/select` - Select the active graph

### Node Management
- `GET /api/nodes` - Get all nodes (optional `?label=` filter)
- `POST /api/nodes` - Create a new node with automatic type detection
- `PUT /api/nodes/<id>` - Update a node
- `DELETE /api/nodes/<id>` - Delete a node

### Edge Management
- `GET /api/edges` - Get all edges (optional `?label=` filter)
- `POST /api/edges` - Create a new edge with automatic type detection
- `PUT /api/edges/<id>` - Update an edge
- `DELETE /api/edges/<id>` - Delete an edge

### Visualization & Query
- `GET /api/graph-data` - Get graph data for visualization (max 200 nodes)
- `POST /api/natural-query/translate` - Translate natural language to Cypher
- `POST /api/natural-query/execute` - Execute a Cypher query and return results

## Apache AGE Setup

Ensure Apache AGE is installed on your PostgreSQL server:

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, '$user', public;
```

The initialization script (`database/init_graph.py`) will handle this automatically.

## Natural Language Query Examples

Once you have configured your Azure OpenAI credentials in `.env`, you can ask questions like:

**Basic Queries:**
- "Find all people who are older than 30"
- "Show me products that cost more than 100"
- "Count how many nodes of each type exist"

**Relationship Queries:**
- "Get all relationships between companies and people"
- "Find nodes with more than 2 connections"
- "Show all people who work at Microsoft"

**Path Queries:**
- "Show me the shortest path between New York and Los Angeles"
- "Find all paths from node A to node B with max 5 hops"
- "What's the fastest route between Chicago and Miami?"

**Road Network Queries** (after running `create_road_graph.py`):
- "Find shortest path between Seattle and Boston"
- "Show all cities connected by highways"
- "Which roads have distance greater than 300 km?"

### How It Works

1. **Schema Analysis**: The system automatically loads your graph schema (vertex labels, edge types, sample properties)
2. **Translation**: Azure OpenAI (GPT-4o) translates your natural language to OpenCypher queries
3. **Review & Edit**: Generated query is displayed with syntax highlighting - you can modify it before execution
4. **Execution**: Query runs against Apache AGE and returns results
5. **Dual View**: Results can be viewed as a table or interactive graph visualization

## Performance Notes

- **Graph visualization**: Limited to 200 nodes for optimal browser performance
- **Query optimization**: Run `create_graph_indexes.py` to add indexes for faster queries
- **Large datasets**: Use natural language queries with filters to retrieve specific subsets
- **Property types**: Numeric values are stored as actual numbers (not strings) for efficient comparison queries

## Troubleshooting

### Common Issues

**AGE Extension Not Available**
- Ensure Apache AGE is installed: `CREATE EXTENSION IF NOT EXISTS age;`
- Check PostgreSQL version compatibility (12+)
- Verify search_path includes `ag_catalog`

**Connection Errors**
- Verify `DATABASE_URL` in `.env` file matches your PostgreSQL configuration
- Check PostgreSQL service is running
- Ensure port 5432 (or custom port) is accessible

**Permission Errors**
- Database user needs CREATE, SELECT, INSERT, UPDATE, DELETE permissions
- User must have permission to load extensions
- Check schema permissions for ag_catalog

**Natural Language Queries Not Working**
- Verify Azure OpenAI credentials in `.env`:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT`
- Check deployment name matches your Azure OpenAI resource
- Ensure API version is correct (2024-08-01-preview or later)

**Numeric Values Stored as Strings**
- This was fixed in recent updates
- Ensure you're using the latest version of `graph_utils.py`
- Recreate old data if needed: numeric values should now be stored without quotes

**Apache AGE Syntax Errors**
- Don't use pipe syntax for multiple edge types: `[r:Type1|Type2]` (not supported)
- Use untyped patterns instead: `[r*1..6]`
- Use `length(path)` instead of `size(path)` for path operations
- Property access uses dot notation: `n.name` not `n['name']`

## Recent Updates

### Graph Visualization in Query Results
- Added vis.js integration to Natural Language Query page
- Toggle between Table and Graph views
- Interactive network visualization with zoom/pan
- Color-coded nodes and edges by type

### Query Editing Workflow
- Generated Cypher queries can be edited before execution
- Syntax highlighting for better readability
- "Edit Query" button prominently displayed

### Demo Data: Road Network
- `create_road_graph.py`: Generate 25-city road network
- `recreate_road_graph.py`: Drop and recreate road graph
- Realistic properties: km, time, city names, population

### Performance Optimization
- `create_graph_indexes.py`: Automated index creation
- BTREE indexes on ID columns
- GIN indexes on JSONB properties
- Significant query speedup for large graphs

### Smart Property Handling
- Automatic type detection for numeric values
- Boolean support (true/false)
- Proper quoting for strings only
- Fixed in all CRUD operations (create_node, create_edge, update_node, update_edge)

### Architecture Improvements
- `openai_helper.py` now loads graph schema internally via `graph_utils.get_graph_data()`
- Complete AGE SQL generation with proper column definitions
- Fixed column mismatch errors in query execution

## GraphUtils Library API Reference

The `graph_utils.py` module provides a Python wrapper for Apache AGE operations with automatic type handling and error management.

### Initialization

```python
from utils.graph_utils import GraphUtils

# Initialize with database URL
graph_utils = GraphUtils(database_url="postgresql://user:pass@localhost:5432/db")

# Set active graph
graph_utils.set_graph("my_graph")
```

### Core Methods

#### Graph Management

**`list_graphs()`**
- Returns all available graphs in the database
- Returns: `{"success": True, "graphs": ["graph1", "graph2", ...]}`

**`create_graph(graph_name)`**
- Creates a new graph with the specified name
- Args: `graph_name` (str) - Name of the graph to create
- Returns: `{"success": True, "message": "Graph 'name' created successfully"}`

**`set_graph(graph_name)`**
- Sets the active graph for subsequent operations
- Args: `graph_name` (str) - Name of the graph to use

#### Node Operations

**`create_node(label, properties)`**
- Creates a new node with automatic type detection
- Args:
  - `label` (str) - Node label (e.g., "Person", "City")
  - `properties` (dict) - Properties with automatic type handling
- Type Support:
  - **Integers/Floats**: Stored as numeric values (e.g., `age: 30`, `price: 99.99`)
  - **Booleans**: Stored as lowercase true/false (e.g., `active: true`)
  - **Strings**: Automatically quoted and escaped (e.g., `name: 'Alice'`)
- Returns: `{"success": True, "result": [...]}`
- Example:
  ```python
  graph_utils.create_node("Person", {
      "name": "Alice",
      "age": 30,
      "salary": 75000.50,
      "active": true
  })
  ```

**`get_all_nodes(label=None, limit=None)`**
- Retrieves all nodes, optionally filtered by label
- Args:
  - `label` (str, optional) - Filter by node label
  - `limit` (int, optional) - Maximum number of nodes to return
- Returns: `{"success": True, "result": [...]}`

**`update_node(node_id, properties)`**
- Updates a node's properties with type detection
- Args:
  - `node_id` (int) - ID of the node to update
  - `properties` (dict) - Properties to set/update
- Returns: `{"success": True, "result": [...]}`

**`delete_node(node_id)`**
- Deletes a node and all its relationships (DETACH DELETE)
- Args: `node_id` (int) - ID of the node to delete
- Returns: `{"success": True, "result": [...]}`

#### Edge Operations

**`create_edge(from_node_id, to_node_id, edge_label, properties=None)`**
- Creates a relationship between two nodes
- Args:
  - `from_node_id` (int) - Source node ID
  - `to_node_id` (int) - Target node ID
  - `edge_label` (str) - Edge type (e.g., "KNOWS", "Highway")
  - `properties` (dict, optional) - Edge properties with type support
- Type Support: Same as `create_node()`
- Returns: `{"success": True, "result": [...]}`
- Example:
  ```python
  graph_utils.create_edge(1, 2, "Highway", {
      "km": 250,
      "time": 2.5,
      "toll": false
  })
  ```

**`get_all_edges(label=None)`**
- Retrieves all edges with source and target nodes
- Args: `label` (str, optional) - Filter by edge label
- Returns: `{"success": True, "result": [[from_node, edge, to_node], ...]}`

**`update_edge(edge_id, properties)`**
- Updates an edge's properties with type detection
- Args:
  - `edge_id` (int) - ID of the edge to update
  - `properties` (dict) - Properties to set/update
- Returns: `{"success": True, "result": [...]}`

**`delete_edge(edge_id)`**
- Deletes an edge by ID
- Args: `edge_id` (int) - ID of the edge to delete
- Returns: `{"success": True, "result": [...]}`

#### Query Operations

**`execute_cypher(cypher_query, params=None)`**
- Executes a raw Cypher query via Apache AGE
- Args:
  - `cypher_query` (str) - Complete AGE SQL query
  - `params` (dict, optional) - Query parameters
- Returns: `{"success": True, "result": [...]}`
- Example:
  ```python
  graph_utils.execute_cypher("""
      SELECT * FROM cypher('my_graph', $$
          MATCH (n:Person) WHERE n.age > 30
          RETURN n
      $$) as (node agtype);
  """)
  ```

**`get_graph_data()`**
- Retrieves graph data for visualization (max 200 nodes)
- Returns nodes and edges between those nodes
- Returns: `{"success": True, "nodes": [...], "edges": [...]}`
- Used internally by the visualization and AI query features

### Key Features

#### Automatic Type Detection
The library automatically detects and formats property values:
- **Numeric values** (int, float): `age: 30`, `price: 99.99`
- **Boolean values**: `active: true`, `verified: false`
- **String values**: `name: 'Alice'`, automatically escaped

#### Error Handling
All methods return a consistent format:
- **Success**: `{"success": True, "result": [...], ...}`
- **Error**: `{"error": "Error message"}`

#### AGE Integration
- Automatically sets search path to include `ag_catalog`
- Handles transaction management (commit/rollback)
- Converts AGE's agtype results to Python-serializable formats

### Usage Example

```python
from utils.graph_utils import GraphUtils
from config import Config

# Initialize
graph = GraphUtils(Config.DATABASE_URL)

# Create graph
graph.create_graph("social_network")
graph.set_graph("social_network")

# Create nodes
alice = graph.create_node("Person", {
    "name": "Alice",
    "age": 30,
    "city": "New York"
})

bob = graph.create_node("Person", {
    "name": "Bob", 
    "age": 35,
    "city": "Boston"
})

# Create relationship
graph.create_edge(
    alice_id, bob_id, "KNOWS",
    {"since": 2015, "strength": 0.85}
)

# Query
result = graph.execute_cypher("""
    SELECT * FROM cypher('social_network', $$
        MATCH (p:Person)-[k:KNOWS]->(friend)
        WHERE p.name = 'Alice'
        RETURN friend.name, k.since
    $$) as (name agtype, since agtype);
""")
```

## OpenAIHelper Library API Reference

The `openai_helper.py` module provides AI-powered natural language to Cypher query translation using Azure OpenAI, making graph queries accessible to non-technical users.

### Initialization

```python
from utils.openai_helper import OpenAIHelper
from utils.graph_utils import GraphUtils
from config import Config

# Initialize GraphUtils first (required for schema analysis)
graph_utils = GraphUtils(Config.DATABASE_URL)
graph_utils.set_graph("my_graph")

# Initialize OpenAI Helper
openai_helper = OpenAIHelper(
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    azure_api_key=Config.AZURE_OPENAI_API_KEY,
    azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT,  # e.g., "gpt-4o"
    azure_api_version=Config.AZURE_OPENAI_API_VERSION,  # e.g., "2024-08-01-preview"
    graph_utils=graph_utils  # Required for automatic schema analysis
)
```

### Core Methods

#### Natural Language to Cypher Translation

**`natural_language_to_cypher(natural_query, graph_schema=None, graph_name=None)`**
- Converts natural language questions to Apache AGE SQL queries
- Uses Azure OpenAI (GPT-4o) to understand intent and generate queries
- Args:
  - `natural_query` (str) - The user's question in plain English
  - `graph_schema` (str, optional) - Schema information for context
  - `graph_name` (str) - Name of the graph to query
- Returns: Dictionary with:
  - `success` (bool) - Whether translation succeeded
  - `cypher` (str) - Complete AGE SQL query with SELECT wrapper
  - `explanation` (str) - Human-readable explanation of the query
  - `assumptions` (str) - Any assumptions made during translation
- Example:
  ```python
  result = openai_helper.natural_language_to_cypher(
      "Find all people older than 30",
      graph_name="social_network"
  )
  # Returns:
  # {
  #     "success": True,
  #     "cypher": "SELECT * FROM cypher('social_network', $$ MATCH (n:Person) WHERE n.age > 30 RETURN n $$) AS (person agtype);",
  #     "explanation": "Finds all Person nodes with age greater than 30",
  #     "assumptions": "Assumed you want all matching persons"
  # }
  ```

#### Schema Analysis

**`get_graph_schema_summary()`**
- Automatically analyzes the current graph and generates a schema summary
- Samples up to 50 nodes and 50 edges to discover:
  - All node labels (types)
  - Properties available for each node type
  - All relationship types
  - Properties available for each relationship type
- Used internally to provide context to the AI for better query generation
- Returns: String with formatted schema information
- Example Output:
  ```
  Node Types:
    - Person: properties = {age, city, name}
    - Product: properties = {name, price, category}
  
  Relationship Types:
    - KNOWS: properties = {since, strength}
    - PURCHASED: properties = {date, quantity}
  ```

### AI Query Generation Features

#### Intelligent Query Construction
The helper includes sophisticated prompts that ensure:

**Apache AGE Compatibility:**
- ✅ Always uses bracket syntax for relationships: `(n)-[r]-()`
- ✅ Never uses forbidden double-dash syntax: `(n)--()` 
- ✅ Avoids unsupported functions like `size()` on graph patterns
- ✅ Uses WHERE clauses instead of pipe syntax for multiple types
- ✅ Generates complete AGE SQL with proper column definitions

**Query Quality:**
- 📊 Automatically adds LIMIT clauses for large result sets
- 🎯 Uses graph schema context for accurate property names
- 🔍 Handles ambiguous queries with reasonable assumptions
- 📝 Provides clear explanations for generated queries

**Advanced Query Types:**
- **Basic Filtering**: "Find all people older than 30"
- **Relationship Queries**: "Show people who know each other"
- **Aggregations**: "Count nodes by type"
- **Path Queries**: "Find shortest path between New York and Los Angeles"
- **Complex Patterns**: "Find people who purchased products in the same category"

#### Shortest Path Optimization
Special handling for distance/time-based path queries:
- Uses variable-length patterns: `(a)-[*1..6]-(b)`
- Aggregates edge properties (km, time) along paths
- Orders results by total distance/time
- Returns top N shortest paths

### Usage Examples

#### Basic Natural Language Query

```python
# Simple node query
result = openai_helper.natural_language_to_cypher(
    "Show all cities",
    graph_name="road"
)

if result["success"]:
    print(f"Generated Query: {result['cypher']}")
    print(f"Explanation: {result['explanation']}")
    
    # Execute the query
    query_result = graph_utils.execute_cypher(result["cypher"])
```

#### Relationship Query

```python
# Find connections
result = openai_helper.natural_language_to_cypher(
    "Show all cities connected by highways",
    graph_name="road"
)

# The AI automatically understands to:
# 1. Match City nodes
# 2. Find Highway relationships
# 3. Return relevant data
```

#### Shortest Path Query

```python
# Complex path finding
result = openai_helper.natural_language_to_cypher(
    "Find the fastest route from New York to Los Angeles",
    graph_name="road"
)

# The AI generates a query that:
# 1. Finds all paths between the cities
# 2. Sums the 'time' property along each path
# 3. Orders by total time
# 4. Returns the top 5 fastest routes
```

#### With Schema Context

```python
# Get schema for better context
schema = openai_helper.get_graph_schema_summary()

# Translate with schema awareness
result = openai_helper.natural_language_to_cypher(
    "Find expensive products",
    graph_schema=schema,
    graph_name="ecommerce"
)

# The AI uses the schema to know:
# - "Product" is the correct node label
# - "price" is the correct property name
# - What constitutes "expensive" based on data
```

#### Complete Workflow

```python
from utils.graph_utils import GraphUtils
from utils.openai_helper import OpenAIHelper
from config import Config

# Setup
graph_utils = GraphUtils(Config.DATABASE_URL)
graph_utils.set_graph("social_network")

openai_helper = OpenAIHelper(
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    azure_api_key=Config.AZURE_OPENAI_API_KEY,
    azure_deployment="gpt-4o",
    graph_utils=graph_utils
)

# Get schema for context
schema = openai_helper.get_graph_schema_summary()
print(f"Graph Schema:\n{schema}")

# Translate natural language
nl_query = "Find people who have more than 3 friends"
result = openai_helper.natural_language_to_cypher(
    nl_query,
    graph_schema=schema,
    graph_name="social_network"
)

if result["success"]:
    print(f"\nQuery: {nl_query}")
    print(f"Generated Cypher: {result['cypher']}")
    print(f"Explanation: {result['explanation']}")
    
    # Execute the generated query
    query_result = graph_utils.execute_cypher(result["cypher"])
    
    if query_result.get("success"):
        print(f"\nResults: {query_result['result']}")
    else:
        print(f"Error: {query_result.get('error')}")
else:
    print(f"Translation failed: {result.get('error')}")
```

### Error Handling

The helper provides consistent error responses:

```python
result = openai_helper.natural_language_to_cypher(
    "Some ambiguous query",
    graph_name="my_graph"
)

if not result["success"]:
    print(f"Error: {result['error']}")
    # Handle error (API issue, invalid config, etc.)
else:
    # Process successful result
    cypher_query = result["cypher"]
```

### Configuration Requirements

Ensure these environment variables are set in `.env`:

```env
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Best Practices

1. **Always pass `graph_utils` during initialization** - Required for automatic schema analysis
2. **Use `get_graph_schema_summary()` before queries** - Provides context for better AI responses
3. **Include `graph_name` in translation calls** - Ensures correct graph is queried
4. **Review generated queries before execution** - AI is powerful but can make mistakes
5. **Handle both success and error cases** - API calls can fail
6. **Use temperature=0.3** - Already configured for consistent, deterministic results

### Integration with Web Interface

The natural language query page (`templates/query.html`) demonstrates full integration:

1. User enters natural language question
2. Frontend calls `/api/natural-query/translate` endpoint
3. Backend uses `OpenAIHelper.natural_language_to_cypher()`
4. Generated query is displayed for user review
5. User can edit the query if needed
6. Frontend calls `/api/natural-query/execute` to run the query
7. Results displayed in table or graph visualization

This workflow ensures transparency and control while leveraging AI assistance.

## License

MIT License
