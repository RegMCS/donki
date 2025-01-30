import os
import logging
from pyvis.network import Network
from openai import OpenAI
from pathlib import Path
import pdfplumber
import pandas as pd
from dotenv import load_dotenv
import sys
import traceback
import tiktoken

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key='string')

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {".pdf", ".xlsx", ".xls", ".txt"}

    def read_file(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
        if ext in {".xlsx", ".xls"}:
            return self._read_excel(file_path)
        elif ext == ".pdf":
            return self._read_pdf(file_path)
        elif ext == ".txt":
            return self._read_text(file_path)

    def _read_excel(self, file_path: str) -> str:
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return " ".join(
                df.astype(str)
                .apply(lambda row: " ".join(row.dropna()), axis=1)
                .replace(r'[^\x00-\x7F]+', ' ', regex=True)
                .tolist()
            )
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise

    def _read_text(self, file_path: str) -> str:
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Unable to read file with any of the attempted encodings: {encodings}")
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise

    def _read_pdf(self, file_path: str) -> str:
        try:
            texts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text = text.encode('ascii', 'ignore').decode('ascii')
                        texts.append(text.strip())
            return " ".join(texts)
        except Exception as e:
            logger.error(f"Error reading PDF file: {str(e)}")
            raise

def split_text_into_chunks(text: str, chunk_size: int = 3000) -> list:
    """Split text into chunks of specified size."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks

def process_chunk(chunk: str) -> dict:
    """Process a single chunk using OpenAI API."""
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the text and extract entities and relationships. 
                    Format your response as entity-relationship-entity tuples. 
                    For each relationship found, return it in this format:
                    Entity1 -> Entity2 (Relationship)"""
                },
                {
                    "role": "user",
                    "content": f"Extract entities and relationships from this text:\n{chunk}"
                }
            ],
            model="gpt-4",
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error processing chunk: {e}")
        return None

def process_data(text: str) -> list:
    """Process entire text in chunks."""
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    chunks = split_text_into_chunks(text)
    logger.info(f"Split text into {len(chunks)} chunks")

    results = []
    for idx, chunk in enumerate(chunks, 1):
        token_count = len(tokenizer.encode(chunk))
        logger.info(f"Processing chunk {idx}/{len(chunks)} ({token_count} tokens)")
        
        result = process_chunk(chunk)
        if result:
            results.append(result)

    return results

def create_visualization(results: list, output_file: str = "entity_graph.html"):
    """Create and save network visualization."""
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
    net.force_atlas_2based()
    
    entities_added = set()
    
    for result in results:
        try:
            # Split the result into lines
            relationships = result.strip().split('\n')
            
            for rel in relationships:
                if '->' in rel:
                    # Parse relationship line
                    parts = rel.split('->')
                    if len(parts) != 2:
                        continue
                        
                    entity1 = parts[0].strip()
                    # Extract entity2 and relationship from second part
                    entity2_rel = parts[1].strip()
                    if '(' in entity2_rel and ')' in entity2_rel:
                        entity2 = entity2_rel[:entity2_rel.find('(')].strip()
                        relationship = entity2_rel[entity2_rel.find('(')+1:entity2_rel.find(')')].strip()
                    else:
                        entity2 = entity2_rel
                        relationship = "related"

                    # Add nodes if they don't exist
                    for entity in [entity1, entity2]:
                        if entity not in entities_added:
                            net.add_node(entity, title=entity)
                            entities_added.add(entity)

                    # Add edge
                    net.add_edge(entity1, entity2, title=relationship, label=relationship)
                    
        except Exception as e:
            logger.error(f"Error processing result: {e}")
            continue

    net.save_graph(output_file)
    logger.info(f"Graph saved to {output_file}")

def get_color_for_type(entity_type: str) -> str:
    """Return color based on entity type."""
    colors = {
        'PERSON': '#ff7675',
        'ORGANIZATION': '#74b9ff',
        'LOCATION': '#55efc4',
        'DATE': '#ffeaa7',
        'default': '#b2bec3'
    }
    return colors.get(entity_type.upper(), colors['default'])

def main():
    if len(sys.argv) != 2:
        print("Usage: python Gptcall.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    try:
        # Initialize processor and read file
        processor = DocumentProcessor()
        text = processor.read_file(file_path)
        logger.info("File read successfully")

        # Process the text
        results = process_data(text)
        logger.info(f"Processed {len(results)} chunks of text")

        # Create visualization
        output_file = "entity_relationship_graph.html"
        create_visualization(results, output_file)
        print(f"Entity-relationship graph has been saved to {output_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()