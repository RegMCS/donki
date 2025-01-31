from flask import Flask, render_template, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from pyvis.network import Network
import os
import openai
import db

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
    prompt = f"Extract entities and their relationships from the following text:\n{text}\nOutput the result as a list of tuples where each tuple is (subject, relationship, object)."

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

    threat_keywords = ["attack", "threat", "security", "breach", "vulnerable"]

    added_nodes = set()
    for subject, verb, obj in relationships:
        if subject != obj:  # Ensure no self-referential relationships
            if subject not in added_nodes:
                color = "red" if any(keyword in subject.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(subject, title=subject, color=color)
                added_nodes.add(subject)
            if obj not in added_nodes:
                color = "red" if any(keyword in obj.lower() for keyword in threat_keywords) else "lightblue"
                net.add_node(obj, title=obj, color=color)
                added_nodes.add(obj)
            edge_color = "red" if any(keyword in verb.lower() for keyword in threat_keywords) else "blue"
            net.add_edge(subject, obj, label=verb, font=dict(size=20, color=edge_color))

    # Save the graph as an HTML file
    net.save_graph(output_file)


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
                # cursor.execute("SELECT articlename FROM ARTICLES;") # Ideal scenario
                cursor.execute("SELECT articlename FROM ARTICLES WHERE articlename IS NOT NULL;") # MVP
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




if __name__ == "__main__":
    app.run(debug=True)
