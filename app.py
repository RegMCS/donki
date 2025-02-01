from flask import Flask, render_template, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from pyvis.network import Network
import os
import openai
import db
import re
from urllib.parse import urlparse, unquote

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



if __name__ == "__main__":
    app.run(debug=True)
