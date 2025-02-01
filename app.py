from flask import Flask, render_template, send_file, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from pyvis.network import Network
import os
import openai
import db
import re
from urllib.parse import urlparse, unquote
import json
import tempfile


# Initialize Flask app
app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = ""

@app.route('/')
def dashboard():
    return render_template('dashboard2.html')

    # # Load example data
    # excel_file = "news_excerpts_parsed.xlsx"  # Replace with the actual file name
    # try:
    #     df = pd.read_excel(excel_file)  # Assuming the file has a column named 'Text'
    # except Exception as e:
    #     return f"Error loading Excel file: {str(e)}"

    # # Extract the text data from the 'Text' column
    # if 'Text' not in df.columns:
    #     return "The Excel file must contain a column named 'Text'."
    # all_texts = df['Text'].dropna().tolist()

    # # Extract relationships from the text data using GPT
    # all_relationships = []
    # for text in all_texts:
    #     relationships = query_gpt_relationship_extraction(text)
    #     all_relationships.extend(relationships)

    # # Generate the network graph
    # graph_path = os.path.join("templates", "pyvis_graph.html")
    # create_custom_pyvis_network(all_relationships, graph_path)

    # # Pass the graph path to the dashboard template
    # return render_template('pyvis_graph.html', graph_path="pyvis_graph.html")


# Function to query GPT for entities and relationships
def query_gpt_relationship_extraction(text):
    prompt = f"Extract entities and their relationships from the following text:\n{text}\nOutput the result as a list of tuples where each tuple is (subject, relationship, object, is_threat). 'is_threat' should be True if the relationship involves cybersecurity threats, malware, breaches, or attacks. Otherwise, return False."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Changed model to gpt-4-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant for extracting entities and relationships."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        result = eval(response['choices'][0]['message']['content'].strip())  # Convert the output string to a Python list of tuples
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error querying GPT: {e}")
        return []

# Function to create a Pyvis network graph
def create_custom_pyvis_network(relationships, output_file):
    net = Network(height='600px', width='100%', directed=True)

    added_nodes = set()
    for subject, verb, obj, is_threat in relationships:
        if subject != obj:  # Ensure no self-referential relationships
            node_color = "red" if is_threat else "lightblue"
            edge_color = "red" if is_threat else "blue"
            if subject not in added_nodes:
                net.add_node(subject, title=subject, color=node_color)
                added_nodes.add(subject)
            if obj not in added_nodes:
                net.add_node(obj, title=obj, color=node_color)
                added_nodes.add(obj)
            net.add_edge(subject, obj, label=verb, font=dict(size=20, color=edge_color))

    # Save the graph as an HTML file
    net.save_graph(output_file)


# TODO extract domain from url, and web page title 

@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = db.get_all_articles()
    return jsonify(articles)

@app.route('/api/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = db.get_article_by_id(article_id)
    if article:
        return jsonify(article)
    return jsonify({'error': 'Article not found'}), 404

@app.route('/graphs/<graphName>')
def graph(graphName):
    return send_file(f'./graphs/{graphName}', mimetype='text/html')

@app.route('/getArticleNames')
def getArticleNames():
    connection = db.connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                # This needs to be changed to articlename without LIKE
                cursor.execute("SELECT articlename FROM ARTICLES;") # Ideal scenario
                # cursor.execute("SELECT articlename FROM ARTICLES WHERE articlename IS NOT NULL;") # MVP
                test = cursor.fetchall()
                return jsonify(test)
        finally:
            connection.close()
    return jsonify({"error": "Database connection failed."}), 500
@app.route('/getArticleInfo/<articleName>')
def getArticleInfo(articleName):
    connection = db.connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ARTICLES WHERE articlename = %s;", (articleName,))
                test = cursor.fetchall()
                return jsonify(test)
        finally:
            connection.close()
    return jsonify({"error": "Database connection failed."}), 500
@app.route('/getRelatedArticle/<tag>')
def getRelatedAritcle(tag):
    connection = db.connect_to_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT articlename FROM ARTICLES WHERE tags LIKE '%{0}%' LIMIT 2;".format(tag)) # Only return maximum 2
                test = cursor.fetchall()
                return jsonify(test)
        finally:
            connection.close()
    return jsonify({"error": "Database connection failed."}), 500
def extract_title_from_url(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Split the path into parts and remove empty strings
    path_parts = [p for p in parsed_url.path.split('/') if p]
    
    # For CNN URLs, always take the second-to-last segment if it exists
    # This handles their standard format of .../section/title/index.html
    if 'cnn.com' in url and len(path_parts) >= 2:
        # Get the part before 'index.html'
        title_part = path_parts[-2]
    else:
        # For other URLs, use the previous logic
        if path_parts and path_parts[-1] in ['index.html', 'index.htm', 'index']:
            title_part = path_parts[-2] if len(path_parts) >= 2 else ''
        else:
            title_part = path_parts[-1]
    
    # Convert URL encoding and replace hyphens/underscores with spaces
    if title_part:
        title = unquote(title_part).replace('-', ' ').replace('_', ' ')
        # Clean up: capitalize words and remove extra spaces
        return ' '.join(word.capitalize() for word in title.split())
    
    return ''
@app.route('/api/update-article-names', methods=['POST'])
def update_article_names():
    try:
        # Get all articles without names
        articles = db.get_articles_without_names()
        updated_count = 0
        skipped = 0
        
        for article in articles:
            try:
                link = article['link']
                title = extract_title_from_url(link)
                
                # Update the database if we got a valid title
                if title:
                    if db.update_article_name(article['id'], title):
                        updated_count += 1
                else:
                    skipped += 1
                    print(f"Skipped article {article['id']}: Could not extract meaningful title from {link}")
            except Exception as e:
                print(f"Error processing article {article['id']}: {str(e)}")
                skipped += 1
                continue
        
        return jsonify({
            'success': True,
            'message': f'Updated {updated_count} article names ({skipped} skipped)',
            'total_processed': len(articles),
            'updated': updated_count,
            'skipped': skipped
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/generate_graph', methods=['GET', 'POST'])
def generate_graph():
    search_query = request.args.get('search', '')  # Empty string by default
    threat_keywords = ["extremist", "terrorism", "subversion", "espionage", "sedition", "separatist", "radical", "militant", "violence", "illegal", "threat", "security", "infiltrate", "unrest", "propaganda", "communal", "racial", "religious", "intelligence", "clandestine"]

    try:
        with open('nodes.json', 'r') as nodes_file:
            data = json.load(nodes_file)
    except Exception as e:
        return f"Error loading JSON file: {str(e)}"

    net = Network(height='600px', width='100%', directed=True, bgcolor='#ffffff', font_color='black')
    
    # Network options remain the same
    net.set_options("""
    const options = {
        "nodes": {
            "shape": "dot",
            "size": 25,
            "font": {
                "size": 14,
                "color": "black"
            },
            "borderWidth": 2,
            "shadow": true
        },
        "edges": {
            "color": {
                "color": "#97c2fc",
                "highlight": "#fb7e81"
            },
            "width": 2,
            "shadow": true,
            "smooth": {
                "type": "continuous"
            },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                }
            }
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -80000,
                "springLength": 250,
                "springConstant": 0.001,
                "avoidOverlap": 0.1
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
        }
    }""")

    # If search query is empty, include all nodes
    if not search_query:
        included_nodes = {node['id'] for node in data['nodes']}
        matching_nodes = set()  # No matching nodes when no search
    else:
        # Find matching nodes only when there's a search query
        matching_nodes = {node['id'] for node in data['nodes'] if search_query.lower() in node['label'].lower()}
        included_nodes = set(matching_nodes)
        # Add connected nodes for search results
        for edge in data['edges']:
            if edge['from'] in matching_nodes:
                included_nodes.add(edge['to'])
            elif edge['to'] in matching_nodes:
                included_nodes.add(edge['from'])

    # Find threat nodes (always active)
    threat_nodes = {node['id'] for node in data['nodes'] 
                   if any(keyword in node['label'].lower() for keyword in threat_keywords)}

    # Add nodes
    for node in data['nodes']:
        if node['id'] in included_nodes:
            is_match = node['id'] in matching_nodes
            is_threat = node['id'] in threat_nodes
            
            if is_threat:
                node_color = '#ff4136'  # Red for threat nodes
            elif is_match:
                node_color = '#ffdc00'  # Yellow for search matches
            else:
                node_color = '#97c2fc'  # Default blue
                
            net.add_node(
                node['id'],
                label=node['label'],
                color=node_color,
                size=30 if (is_match or is_threat) else 25,
                borderWidth=3 if (is_match or is_threat) else 2,
                title=node.get('title', ''),
            )

    # Add edges
    for edge in data['edges']:
        if edge['from'] in included_nodes and edge['to'] in included_nodes:
            is_threat_edge = (edge['from'] in threat_nodes or edge['to'] in threat_nodes)
            
            net.add_edge(
                edge['from'], 
                edge['to'],
                label=edge.get('label', ''),
                title=edge.get('title', ''),
                color={'color': '#ff4136' if is_threat_edge else '#97c2fc', 
                       'highlight': '#fb7e81'},
                width=3 if is_threat_edge else 2
            )

    # JavaScript for interaction remains the same
    net.html += """
    <script>
        network.on("click", function(params) {
            network.unselectAll();
            
            if (params.nodes.length > 0) {
                const selectedNode = params.nodes[0];
                const connectedNodes = network.getConnectedNodes(selectedNode);
                const connectedEdges = network.getConnectedEdges(selectedNode);
                
                network.selectNodes([selectedNode, ...connectedNodes]);
                network.selectEdges(connectedEdges);
            }
        });

        network.on("hoverNode", function(params) {
            document.body.style.cursor = 'pointer';
        });

        network.on("blurNode", function(params) {
            document.body.style.cursor = 'default';
        });
    </script>
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        graph_path = temp_file.name
        net.save_graph(graph_path)

    with open(graph_path, 'r') as file:
        graph_html = file.read()

    return render_template('graph.html', graph_html=graph_html, search_query=search_query)


if __name__ == "__main__":
    app.run(debug=True)
