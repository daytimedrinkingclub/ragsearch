import os
from openai import OpenAI
from pinecone import Pinecone


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
PINECONE_HOST = os.environ.get("PINECONE_HOST")

# Set up OpenAI and Pinecone
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def create_embedding(text):
    """Create an embedding for the given text using OpenAI's API."""
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    return response.data[0].embedding

def search_pinecone(query, top_k=5):
    """Search Pinecone index with the query embedding and return top results."""
    query_embedding = create_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.matches

def main():
    while True:
        query = input("Enter your search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        print(f"\nSearching for: '{query}'")
        results = search_pinecone(query)

        if not results:
            print("No results found.")
        else:
            print("\nTop 3 results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. ID: {result.id}")
                print(f"   Score: {result.score:.4f}")
                if result.metadata:
                    print(f"   Article Name: {result.metadata.get('article_name', 'N/A')}")
                print()

if __name__ == "__main__":
    main()