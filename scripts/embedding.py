import os
from openai import OpenAI
from pinecone import Pinecone
import csv
import uuid
import time


# Load API keys and environment variables pick from os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")    
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_HOST=os.getenv("PINECONE_HOST")
# Check if all required environment variables are set
if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME]):
    raise ValueError("Missing required environment variables")

print("Environment variables loaded successfully.")
# Initialize OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)
# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

print("OpenAI and Pinecone initialized.")

# Connect to the existing index
index = pc.Index(PINECONE_INDEX_NAME)

print(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")

def create_embedding(text):
    """Create an embedding for the given text using OpenAI's API."""
    print(f"Creating embedding for text: {text[:50]}...")  # Print first 50 characters
    
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    print("Embedding created successfully.")
    return response.data[0].embedding

def process_csv(input_file, output_file):
    """Process the input CSV file, create embeddings, and save results."""
    print(f"Starting to process CSV file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as csvfile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        fieldnames = ['id', 'article_name', 'article_content']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        vectors_to_upsert = []
        for row in reader:
            try:
                article_name = row['Article Name']
                article_content = row['Article Content']

                print(f"Processing article: {article_name}")

                # Generate embedding
                embedding = create_embedding(article_content)

                # Generate a unique ID
                unique_id = str(uuid.uuid4())

                print(f"Generated unique ID: {unique_id}")

                # Prepare vector for upsert
                vector = {
                    "id": unique_id,
                    "values": embedding,
                    "metadata": {"article_name": article_name}
                }
                vectors_to_upsert.append(vector)

                # Write results to output CSV (without the embedding)
                writer.writerow({
                    'id': unique_id,
                    'article_name': article_name,
                    'article_content': article_content
                })

                print(f"Processed: {article_name}")

                # Upsert in batches of 100 vectors
                if len(vectors_to_upsert) >= 100:
                    index.upsert(vectors=vectors_to_upsert)
                    print(f"Upserted batch of {len(vectors_to_upsert)} vectors")
                    vectors_to_upsert = []

            except Exception as e:
                print(f"Error processing row: {e}")

        # Upsert any remaining vectors
        if vectors_to_upsert:
            index.upsert(vectors=vectors_to_upsert)
            print(f"Upserted final batch of {len(vectors_to_upsert)} vectors")

def main():
    input_file = 'data.csv'  # Replace with your input CSV file name
    output_file = 'embeddings_results.csv'

    print(f"Starting main process with input file: {input_file}")

    try:
        process_csv(input_file, output_file)
        print(f"Embeddings inserted and results saved in {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    print("Script execution completed.")