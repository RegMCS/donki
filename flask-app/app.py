from flask import Flask, render_template
import pandas as pd
import spacy
from pyvis.network import Network
import os

app = Flask(__name__)

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# Function to extract entities and relationships from text
def extract_entities_and_relationships(text):
    doc = nlp(text)
    relationships = []

    for token in doc:
        if token.dep_ in ('nsubj', 'dobj', 'pobj') and token.head.pos_ == 'VERB':
            subject = token.text
            verb = token.head.text
            obj = [child.text for child in token.head.children if child.dep_ == 'dobj']
            obj = obj[0] if obj else None
            if obj:
                relationships.append((subject, verb, obj))

    return relationships

# Function to create a Pyvis network graph
def create_custom_pyvis_network(relationships, output_file):
    net = Network(height='600px', width='100%', directed=False)

    # Add nodes and edges with customizations
    for subject, verb, obj in relationships:
        net.add_node(subject, title=subject)
        net.add_node(obj, title=obj)
        net.add_edge(subject, obj, label=verb, font=dict(size=20, color="blue"))

    # Save the graph as an HTML file
    net.save_graph(output_file)

@app.route('/')
def dashboard():
    # Load example data
    texts = [
        "Alice is friends with Bob.",
        "Charlie works with David.",
        "Alice supervises Charlie.",
        "Bob knows David."
    ]

    # Extract relationships from the text data
    all_relationships = []
    for text in texts:
        relationships = extract_entities_and_relationships(text)
        all_relationships.extend(relationships)

    # Generate the network graph
    graph_path = os.path.join("templates", "pyvis_graph.html")
    create_custom_pyvis_network(all_relationships, graph_path)

    # Pass the graph path to the dashboard template
    return render_template('pyvis_graph.html', graph_path="pyvis_graph.html")

if __name__ == "__main__":
    app.run(debug=True)
