import openai
import create_graph


openai.api_key = ""


def parse_article(article, uri):
    """
    Based on the article, using a model (ChatGPT), generate:

    - Summary of the Article
    - Credibility of the Article
    - Generate a list of tuples for relationships identified in the Article, where each tuple has 3 elements:
        - 1st element is the subject
        - 2nd element is the relationship
        - 3rd element is the object

    With the generated list, it will create a graph for it

    Returns the summary and credibility of the article

    """

    # Generate Summary of article
    # summary = query_gpt_summary(article)


    # Generate Credibility of article
    # credibility = query_gpt_credibility(article)

    # Generate relationship identified in article
    # relationship = query_gpt_relationship_extraction(article)

    # Generate graph
    # create_graph.generate_graph(relationship, uri)
    # create_graph.create_custom_pyvis_network(relationship, uri)

    # Return
    # return (summary, credibility) 




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






def main():
    pass


if __name__ == "__main__":
    main()