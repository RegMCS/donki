import spacy
from transformers import pipeline

def spacynlp_process(input_text):
    """
    Takes in `input_text` to be parsed by SpaCY NLP.
    Returns a list
    """

    # Load spaCy's transformer-based model
    nlp = spacy.load("en_core_web_trf")
    text = input_text
    
    # Process the text with spaCy
    doc = nlp(text)

    # Create a list to store extracted relationships
    relationships = []

    # Use Hugging Face's transformers NER pipeline for named entity recognition
    nlp_ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
 
    # Extract named entities and their labels
    named_entities = nlp_ner(text)

    # Iterate through the sentences in the document
    for sent in doc.sents:
        # Iterate through the named entities (people, organizations etc.) in the sentence
        for ent in sent.ents:
            # Check if the entity has a known label and is a person or organization
            if ent.label_ in ["PERSON", "ORG"]:
                # Extract the relationship
                for token in sent:
                    if token.dep_ in ["attr", "nsubj", "dobj"]:
                        relationships.append((ent.text, token.text))

    return relationships

def spacynlp_process2(input_text):

    relationships = []

    # Load the spaCy model
    nlp = spacy.load("en_core_web_sm")
    text = input_text

    # Process the text with spaCy pipeline
    doc = nlp(text)

    # Step 1: Extract all nouns (both singular and plural)
    nouns = [token for token in doc if token.pos_ in ['NOUN', 'PROPN']]

    # Print the identified nouns
    print("Identified Nouns:")
    for noun in nouns:
        print(noun.text)

    # Step 2: Extract relationships between nouns
    print("\nRelationships between Nouns:")

    # We will use dependency parsing to extract relationships
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:  # We are interested in nouns and proper nouns
            # Check if the noun has a syntactic relationship (like a subject, object, or preposition)
            if token.dep_ in ['nsubj', 'dobj', 'prep']:
                # Extract the related noun (subject-object-preposition)
                related_noun = None
                if token.dep_ == 'nsubj':  # Subject noun
                    related_noun = token
                    # Find the object (dobj) related to the verb
                    for child in token.head.children:
                        if child.dep_ == 'dobj':
                            print(f"Relationship: {related_noun.text} -> {token.head.text} -> {child.text}")
                            relationships.append((related_noun.text, token.head.text, child.text))
                elif token.dep_ == 'dobj':  # Object noun
                    related_noun = token
                    print(f"Relationship: {token.head.text} -> {related_noun.text}")
                    relationships.append((token.head.text, related_noun.text))
                elif token.dep_ == 'prep':  # Preposition and its object
                    related_noun = token
                    for child in token.children:
                        if child.pos_ == 'NOUN':
                            print(f"Relationship: {token.head.text} -> {related_noun.text} -> {child.text}")
                            relationships.append((token.head.text, related_noun.text, child.text))
    
    return relationships

def main():
    sample_text = """Starbucks violated federal labor law when it increased wages and offered new perks and benefits only to non-union employees, a National Labor Relations Board judge found Thursday.

The decision is the latest in a series of NLRB rulings finding that Starbucks has violated labor law in its efforts to stop unions from forming in its coffee shops.

“The issue at the heart of this case is whether, under current Board law, [Starbucks] was entitled to explicitly reward employees,” for not participating in union activity, “while falsely telling its workers that the federal labor law forced it to take this action,” wrote administrative law judge Mara-Louise Anzalone. “It was not."""

    print(spacynlp_process2(sample_text))


if __name__ == "__main__":
    main()



