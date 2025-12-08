"""
Flask application for Apache AGE Graph Database Management
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from config import Config
from utils.graph_utils import GraphUtils
from utils.openai_helper import OpenAIHelper

app = Flask(__name__)
app.config.from_object(Config)

# Initialize graph utilities without a specific graph
graph_utils = GraphUtils(Config.DATABASE_URL)

# Initialize OpenAI helper (only if Azure OpenAI is configured)
openai_helper = None
if Config.AZURE_OPENAI_ENDPOINT and Config.AZURE_OPENAI_API_KEY:
    try:
        openai_helper = OpenAIHelper(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_api_key=Config.AZURE_OPENAI_API_KEY,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT,
            azure_api_version=Config.AZURE_OPENAI_API_VERSION,
            graph_utils=graph_utils
        )
    except Exception as e:
        print(f"Warning: Could not initialize Azure OpenAI helper: {e}")

@app.route('/')
def index():
    """Home page"""
    # Check if a graph is selected
    current_graph = session.get('graph_name')
    graphs_result = graph_utils.list_graphs()
    graphs = graphs_result.get('graphs', []) if graphs_result.get('success') else []
    
    return render_template('index.html', current_graph=current_graph, graphs=graphs)

@app.route('/nodes')
def nodes():
    """Page to create and view nodes"""
    current_graph = session.get('graph_name')
    if not current_graph:
        flash('Please select a graph first', 'warning')
        return redirect(url_for('index'))
    return render_template('nodes.html', current_graph=current_graph)

@app.route('/edges')
def edges():
    """Page to create and view edges"""
    current_graph = session.get('graph_name')
    if not current_graph:
        flash('Please select a graph first', 'warning')
        return redirect(url_for('index'))
    # Get all nodes for the dropdown
    graph_utils.set_graph(current_graph)
    nodes_result = graph_utils.get_all_nodes()
    nodes = nodes_result.get('result', []) if nodes_result.get('success') else []
    return render_template('edges.html', nodes=nodes, current_graph=current_graph)

@app.route('/graph')
def graph():
    """Graph visualization page"""
    current_graph = session.get('graph_name')
    if not current_graph:
        flash('Please select a graph first', 'warning')
        return redirect(url_for('index'))
    return render_template('graph.html', current_graph=current_graph)

@app.route('/query')
def query():
    """Natural language query page"""
    current_graph = session.get('graph_name')
    if not current_graph:
        flash('Please select a graph first', 'warning')
        return redirect(url_for('index'))
    return render_template('query.html', current_graph=current_graph)

# API Routes

@app.route('/api/graphs', methods=['GET'])
def api_list_graphs():
    """List all available graphs"""
    result = graph_utils.list_graphs()
    return jsonify(result)

@app.route('/api/graphs', methods=['POST'])
def api_create_graph():
    """Create a new graph"""
    data = request.json
    graph_name = data.get('graph_name')
    
    if not graph_name:
        return jsonify({"error": "graph_name is required"}), 400
    
    result = graph_utils.create_graph(graph_name)
    return jsonify(result)

@app.route('/api/graphs/select', methods=['POST'])
def api_select_graph():
    """Select the active graph"""
    data = request.json
    graph_name = data.get('graph_name')
    
    if not graph_name:
        return jsonify({"error": "graph_name is required"}), 400
    
    # Verify graph exists
    graphs_result = graph_utils.list_graphs()
    if graphs_result.get('success') and graph_name in graphs_result.get('graphs', []):
        session['graph_name'] = graph_name
        graph_utils.set_graph(graph_name)
        return jsonify({"success": True, "message": f"Graph '{graph_name}' selected"})
    else:
        return jsonify({"error": f"Graph '{graph_name}' not found"}), 404

@app.route('/api/nodes', methods=['GET'])
def api_get_nodes():
    """Get all nodes"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    label = request.args.get('label')
    result = graph_utils.get_all_nodes(label)
    return jsonify(result)

@app.route('/api/nodes', methods=['POST'])
def api_create_node():
    """Create a new node"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    data = request.json
    label = data.get('label')
    properties = data.get('properties', {})
    
    if not label:
        return jsonify({"error": "Label is required"}), 400
    
    result = graph_utils.create_node(label, properties)
    return jsonify(result)

@app.route('/api/edges', methods=['GET'])
def api_get_edges():
    """Get all edges"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    label = request.args.get('label')
    result = graph_utils.get_all_edges(label)
    return jsonify(result)

@app.route('/api/edges', methods=['POST'])
def api_create_edge():
    """Create a new edge"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    data = request.json
    from_node_id = data.get('from_node_id')
    to_node_id = data.get('to_node_id')
    label = data.get('label')
    properties = data.get('properties', {})
    
    if not all([from_node_id, to_node_id, label]):
        return jsonify({"error": "from_node_id, to_node_id, and label are required"}), 400
    
    result = graph_utils.create_edge(from_node_id, to_node_id, label, properties)
    return jsonify(result)

@app.route('/api/nodes/<int:node_id>', methods=['PUT'])
def api_update_node(node_id):
    """Update a node"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    data = request.json
    properties = data.get('properties', {})
    
    if not properties:
        return jsonify({"error": "Properties are required"}), 400
    
    result = graph_utils.update_node(node_id, properties)
    return jsonify(result)

@app.route('/api/nodes/<int:node_id>', methods=['DELETE'])
def api_delete_node(node_id):
    """Delete a node"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    result = graph_utils.delete_node(node_id)
    return jsonify(result)

@app.route('/api/edges/<int:edge_id>', methods=['PUT'])
def api_update_edge(edge_id):
    """Update an edge"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    data = request.json
    properties = data.get('properties', {})
    
    if not properties:
        return jsonify({"error": "Properties are required"}), 400
    
    result = graph_utils.update_edge(edge_id, properties)
    return jsonify(result)

@app.route('/api/edges/<int:edge_id>', methods=['DELETE'])
def api_delete_edge(edge_id):
    """Delete an edge"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    result = graph_utils.delete_edge(edge_id)
    return jsonify(result)

@app.route('/api/graph-data')
def api_graph_data():
    """Get all graph data for visualization"""
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    result = graph_utils.get_graph_data()
    return jsonify(result)

@app.route('/api/natural-query/translate', methods=['POST'])
def api_translate_query():
    """Translate natural language to Cypher"""
    if not openai_helper:
        return jsonify({"error": "Azure OpenAI is not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env"}), 400
    
    data = request.json
    natural_query = data.get('query')
    
    if not natural_query:
        return jsonify({"error": "query is required"}), 400
    
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    # Get graph schema for context
    graph_utils.set_graph(current_graph)
    schema = openai_helper.get_graph_schema_summary()
    
    # Translate query (pass graph name so AI can include it in the query)
    result = openai_helper.natural_language_to_cypher(natural_query, schema, current_graph)
    return jsonify(result)

@app.route('/api/natural-query/execute', methods=['POST'])
def api_execute_cypher():
    """Execute a Cypher query"""
    data = request.json
    cypher_query = data.get('cypher')
    
    if not cypher_query:
        return jsonify({"error": "cypher is required"}), 400
    
    current_graph = session.get('graph_name')
    if not current_graph:
        return jsonify({"error": "No graph selected"}), 400
    
    graph_utils.set_graph(current_graph)
    
    # Check if query already includes SELECT wrapper (complete AGE SQL)
    if cypher_query.strip().upper().startswith('SELECT'):
        # Query is already complete, execute as-is
        result = graph_utils.execute_cypher(cypher_query)
    else:
        # Legacy format - just Cypher, wrap it
        wrapped_query = f"""
        SELECT * FROM cypher('{current_graph}', $$
            {cypher_query}
        $$) as (result agtype);
        """
        result = graph_utils.execute_cypher(wrapped_query)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
