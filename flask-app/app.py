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
    net = Network(height='600px', width='100%', directed=True)

    threat_keywords = ["attack", "threat", "security", "breach", "vulnerable"]

    involved_entities = set()
    for subject, verb, obj in relationships:
        involved_entities.add(subject)
        involved_entities.add(obj)

    added_nodes = set()
    for subject, verb, obj in relationships:
        if subject != obj:  # Ensure no self-referential relationships
            if subject not in added_nodes:
                color = "red" if any(keyword in subject.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(subject, title=subject, color=color)
                added_nodes.add(subject)
            if obj not in added_nodes:
                color = "red" if any(keyword in subject.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(obj, title=obj,color=color)
                added_nodes.add(obj)
            edge_color = "red" if any(keyword in verb.lower() for keyword in threat_keywords) else "blue"
            net.add_edge(subject, obj, label=verb, font=dict(size=20, color=edge_color))

    # Add nodes and edges with customizations
    # for subject, verb, obj in relationships:
    #     if subject != obj:
    #         net.add_node(subject, title=subject)
    #         net.add_node(obj, title=obj)
    #         net.add_edge(subject, obj, label=verb, font=dict(size=20, color="blue"))

    # Save the graph as an HTML file
    net.save_graph(output_file)

@app.route('/')
def dashboard():
    # Load example data
    excel_file = "news_excerpts_parsed.xlsx"  # Replace with the actual file name
    try:
        df = pd.read_excel(excel_file)  # Assuming the file has a column named 'Text'
    except Exception as e:
        return f"Error loading Excel file: {str(e)}"

    # Extract the text data from the 'Text' column
    if 'Text' not in df.columns:
        return "The Excel file must contain a column named 'Text'."
    all_texts = df['Text'].dropna().tolist()

    # Extract relationships from the text data
    all_relationships = []
    for text in all_texts:
        relationships = extract_entities_and_relationships(text)
        all_relationships.extend(relationships)

    # Generate the network graph
    graph_path = os.path.join("templates", "pyvis_graph.html")
    create_custom_pyvis_network(all_relationships, graph_path)

    # Pass the graph path to the dashboard template
    return render_template('pyvis_graph.html', graph_path="pyvis_graph.html")

if __name__ == "__main__":
    app.run(debug=True)
