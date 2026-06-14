import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_and_chunk_documents

def build_vector_store(data_folder="data"):
    """
    Embeds all chunks and stores them in ChromaDB.
    """
    print("Loading chunks...")
    chunks = load_and_chunk_documents(data_folder)
    print(f"Loaded {len(chunks)} chunks")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Embedding chunks (this may take a minute)...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Storing in ChromaDB...")
    client = chromadb.PersistentClient(path="chroma_db")

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("dorm_reviews")
    except:
        pass

    collection = client.create_collection("dorm_reviews")

    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source": chunk["source"],
                "dorm_name": chunk["dorm_name"]
            }
            for chunk in chunks
        ],
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    print(f"\nDone! {len(chunks)} chunks stored in ChromaDB.")
    return collection


def retrieve(query, k=5):
    """
    Takes a query string and returns the top-k most relevant chunks.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("dorm_reviews")

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "dorm_name": results["metadatas"][0][i]["dorm_name"],
            "distance": results["distances"][0][i]
        })

    return chunks


if __name__ == "__main__":
    # Step 1: Build the vector store
    build_vector_store()

    # Step 2: Test retrieval with 3 queries
    test_queries = [
        "Which dorms have air conditioning?",
        "What dorm is best for making friends as a first year?",
        "What are the complaints about Musselman Hall?"
    ]

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        results = retrieve(query, k=3)
        for r in results:
            print(f"[{r['dorm_name']}] (distance: {r['distance']:.3f})")
            print(f"{r['text'][:200]}")
            print()