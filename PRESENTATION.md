# AGE Graph Manager — Application Presentation

---

## Slide 1: Title

### AGE Graph Manager
**A Web Application for Graph Database Management with AI-Powered Queries**

- **Stack**: Flask + PostgreSQL + Apache AGE + Azure OpenAI
- **Purpose**: Make graph databases accessible through a visual, intuitive interface
- **Audience**: Developers, data analysts, and anyone who needs to explore connected data

---

## Slide 2: The Problem

### Why Graph Databases?

Relational databases struggle with questions like:
- "What is the shortest path between two cities?"
- "Who are the friends of my friends?"
- "Which nodes are most connected in the network?"

**Graphs naturally model relationships** — but querying them requires learning Cypher or similar languages.

**AGE Graph Manager bridges this gap** by letting users:
1. Build graphs visually through a web UI
2. Query graphs in plain English using AI
3. See results as interactive network visualizations

---

## Slide 3: Architecture

### System Architecture

```
 ┌──────────────────────────────────┐
 │         Browser (User)           │
 │   Bootstrap 5 + vis.js + AJAX   │
 └───────────────┬──────────────────┘
                 │ HTTP
 ┌───────────────▼──────────────────┐
 │       Flask Application          │
 │   REST API + Jinja2 Templates    │
 ├──────────────────────────────────┤
 │  GraphUtils      OpenAIHelper    │
 │  (AGE queries)   (NL → Cypher)  │
 └──────┬──────────────────┬────────┘
        │                  │
        ▼                  ▼
 ┌──────────────┐  ┌───────────────┐
 │ PostgreSQL   │  │ Azure OpenAI  │
 │ + Apache AGE │  │ (GPT-4o)      │
 └──────────────┘  └───────────────┘
```

**Key design choices:**
- Apache AGE adds graph capabilities **inside PostgreSQL** — no separate graph DB needed
- OpenCypher dialect for graph queries
- Azure OpenAI translates natural language to Cypher in real time

---

## Slide 4: Core Features

### What Can Users Do?

| Area | Capabilities |
|------|-------------|
| **Graph Management** | Create multiple independent graphs, switch between them |
| **Node Operations** | Create nodes with labels (Person, City, Company) and typed properties (name, age, salary) |
| **Edge Operations** | Create directed relationships (KNOWS, Highway, WORKS_AT) with properties (km, since, salary) |
| **Visualization** | Interactive vis.js graph with drag, zoom, color-coded labels, adjustable node limits (10-200) |
| **AI Queries** | Type English questions → get Cypher → edit if needed → execute → view as table or graph |
| **Anomaly Detection** | Detect isolated nodes, over-connected hubs, and missing connections |

---

## Slide 5: Demo — Graph Visualization

### Interactive Graph Rendering

The visualization page uses **vis.js** to render the graph in real time:

- **Color-coded** nodes and edges by label/type
- **Drag & drop** nodes to rearrange layout
- **Zoom & pan** to explore large graphs
- **Hover** for property details
- **Adjustable limit slider** (10 to 200 nodes)
- **Dynamic legend** showing all label types and their colors

When a graph is loaded, the system:
1. Fetches up to 200 nodes via `/api/graph-data`
2. Parses AGE's `agtype` format into JSON
3. Assigns colors per label using a hash function
4. Renders nodes and edges as a force-directed network

---

## Slide 6: Demo — Natural Language Queries

### Ask Questions in English

**User types:** *"Find all people older than 40 who live in New York"*

**Behind the scenes:**
1. The app sends the question + graph schema to Azure OpenAI
2. GPT-4o returns a complete AGE SQL query:
   ```sql
   SELECT * FROM cypher('social_network', $$
       MATCH (p:Person)
       WHERE p.age > 40 AND p.city = 'New York'
       RETURN p
   $$) AS (person agtype);
   ```
3. The user can **review and edit** the query before running it
4. Results appear in **table view** or **graph view**

**More example queries:**
- "Show the shortest path between Chicago and Miami"
- "Who practices Soccer and works in Technology?"
- "Find coworkers who are also friends"
- "Count how many people practice each sport"

---

## Slide 7: Smart Property Handling

### Automatic Type Detection

When creating nodes or edges, the app automatically detects property types:

```json
{
  "name": "Alice",       → stored as string: 'Alice'
  "age": 30,             → stored as integer: 30
  "salary": 75000.50,    → stored as float: 75000.50
  "active": true         → stored as boolean: true
}
```

**Why this matters:**
- Numeric comparisons work correctly (`WHERE n.age > 25`)
- No need for type casting in queries
- Boolean filters work as expected

---

## Slide 8: Demo Data — Two Ready-Made Scenarios

### Road Network (25 US cities)
```bash
python create_road_graph.py
```
- 25 City nodes (New York, LA, Chicago, Miami...)
- Highway and Normal road edges with `km` and `time` properties
- 2-4 connections per city for realistic topology

### Social Network (100 people, 10 sports, 10 companies)
```bash
python create_social_network.py
```
- 100 Person nodes with name, age, city
- 10 Sport nodes, 10 Company nodes
- Relationships: PRACTICE, LIKE, WORKS_AT, FRIENDS, COWORKER
- Rich properties: skill_level, salary, closeness, collaboration_score

Both can be dropped and recreated with `recreate_*.py` scripts.

---

## Slide 9: Anomaly Detection

### Automatic Graph Health Analysis

The anomaly detection system identifies:

| Anomaly Type | What It Finds | Why It Matters |
|-------------|---------------|----------------|
| **Isolated Nodes** | Nodes with zero connections | Data quality issues, missing relationships |
| **High-Degree Nodes** | Nodes with 10+ connections | Potential bottlenecks or hubs |
| **Low-Degree Nodes** | Nodes with very few connections | Under-represented entities |
| **Missing Connections** | Expected but absent relationships | Incomplete data modeling |

Each anomaly type runs a dedicated Cypher query and returns structured results with severity levels.

---

## Slide 10: API Reference

### RESTful JSON API

The application exposes a complete API for programmatic access:

**Graph Management:**
- `GET /api/graphs` — List all graphs
- `POST /api/graphs` — Create a new graph
- `POST /api/graphs/select` — Switch active graph

**Nodes:**
- `GET /api/nodes?label=Person` — Get nodes (optional label filter)
- `POST /api/nodes` — Create a node
- `PUT /api/nodes/<id>` — Update a node
- `DELETE /api/nodes/<id>` — Delete a node

**Edges:**
- `GET /api/edges?label=KNOWS` — Get edges (optional label filter)
- `POST /api/edges` — Create an edge
- `PUT /api/edges/<id>` — Update an edge
- `DELETE /api/edges/<id>` — Delete an edge

**Advanced:**
- `GET /api/graph-data` — Full graph for visualization (max 200 nodes)
- `GET /api/anomalies/detect` — Run anomaly detection
- `POST /api/natural-query/translate` — NL to Cypher translation
- `POST /api/natural-query/execute` — Execute Cypher query

---

## Slide 11: Project Structure

```
grapgenric/
├── app.py                      # Flask app: routes + API endpoints
├── config.py                   # Environment-based configuration
├── requirements.txt            # Python dependencies
├── database/
│   └── init_graph.py           # AGE extension initialization
├── utils/
│   ├── graph_utils.py          # Core graph operations (CRUD, queries, anomalies)
│   └── openai_helper.py        # Azure OpenAI NL-to-Cypher translation
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Layout with Bootstrap 5 navbar
│   ├── index.html              # Home: graph selection + creation
│   ├── nodes.html              # Node management with pagination
│   ├── edges.html              # Edge management with pagination
│   ├── graph.html              # vis.js interactive visualization
│   ├── query.html              # NL query with dual view (table/graph)
│   └── anomalies.html          # Anomaly detection dashboard
├── static/
│   ├── css/style.css           # Custom styles
│   └── js/main.js              # Client-side JavaScript
├── create_road_graph.py        # Road network demo data generator
├── create_social_network.py    # Social network demo data generator
├── recreate_road_graph.py      # Drop + recreate road graph
├── recreate_social_network.py  # Drop + recreate social network
└── create_graph_indexes.py     # Automated index creation
```

---

## Slide 12: Technology Stack

| Component | Technology | Version / Notes |
|-----------|-----------|-----------------|
| **Web Framework** | Flask | Lightweight, Jinja2 templating |
| **Database** | PostgreSQL 12+ | Relational + graph in one engine |
| **Graph Extension** | Apache AGE | OpenCypher on PostgreSQL |
| **ORM / Connector** | SQLAlchemy + psycopg2 | Raw SQL via `exec_driver_sql` for AGE compatibility |
| **AI** | Azure OpenAI | GPT-4o, JSON mode, temperature 0.3 |
| **Frontend** | Bootstrap 5 | Responsive layout, cards, forms |
| **Graph Rendering** | vis.js | Force-directed network visualization |
| **Configuration** | python-dotenv | `.env` file for credentials |

---

## Slide 13: How to Run

### Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env with your database URL and (optionally) Azure OpenAI keys
#    DATABASE_URL=postgresql://user:pass@host:port/db
#    AZURE_OPENAI_ENDPOINT=https://...
#    AZURE_OPENAI_API_KEY=...

# 4. Initialize the AGE extension
python database/init_graph.py

# 5. (Optional) Load demo data
python create_road_graph.py
python create_social_network.py

# 6. Start the application
python app.py
# → Open http://localhost:5000
```

---

## Slide 14: Key Takeaways

### Summary

1. **Apache AGE** brings graph capabilities to PostgreSQL — no need for a separate graph database
2. **Natural language queries** powered by Azure OpenAI make graph data accessible to non-technical users
3. **Interactive visualization** with vis.js turns abstract data into explorable networks
4. **Full CRUD operations** through both a web UI and a REST API
5. **Demo data generators** let you explore the application immediately
6. **Anomaly detection** provides automated insights into graph structure and data quality

### Potential Extensions
- User authentication and role-based access control
- Graph import/export (GraphML, CSV)
- Scheduled anomaly reports
- Additional AI capabilities (graph summarization, recommendation)
- Deployment to Azure App Service with managed PostgreSQL

---

*End of Presentation*
