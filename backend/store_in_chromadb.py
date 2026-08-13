import json
from pathlib import Path

import chromadb


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHUNKS_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "chunks_with_metadata.json"
)

EMBEDDINGS_FILE = (
    BASE_DIR
    / "processed"
    / "embeddings"
    / "embeddings.json"
)

CHROMA_DIR = (
    BASE_DIR
    / "processed"
    / "chroma_db"
)


# ---------------------------------------------------------
# CREATE CHROMA DATABASE
# ---------------------------------------------------------

print("=" * 70)
print("DIGILAW CHROMADB VECTOR DATABASE")
print("=" * 70)

print("\nInitializing ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

print("ChromaDB initialized.")


# ---------------------------------------------------------
# CREATE COLLECTION
# ---------------------------------------------------------

collection = client.get_or_create_collection(
    name="digilaw_legal_knowledge"
)

print("Collection ready.")


# ---------------------------------------------------------
# LOAD CHUNKS
# ---------------------------------------------------------

print("\nLoading chunks...")

with open(
    CHUNKS_FILE,
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)

print(f"Chunks loaded: {len(chunks)}")


# ---------------------------------------------------------
# LOAD EMBEDDINGS
# ---------------------------------------------------------

print("\nLoading embeddings...")

with open(
    EMBEDDINGS_FILE,
    "r",
    encoding="utf-8"
) as file:

    embedded_chunks = json.load(file)

print(
    f"Embeddings loaded: {len(embedded_chunks)}"
)


# ---------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------

if len(chunks) != len(embedded_chunks):

    raise ValueError(
        "Number of chunks and embeddings do not match."
    )


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

ids = []
documents = []
metadatas = []
vectors = []

for item in embedded_chunks:

    ids.append(
        item["chunk_id"]
    )

    documents.append(
        item["text"]
    )

    metadatas.append(
        item["metadata"]
    )

    vectors.append(
        item["embedding"]
    )


# ---------------------------------------------------------
# ADD TO CHROMADB
# ---------------------------------------------------------

print("\nAdding vectors to ChromaDB...")
print("This may take a little while.")


BATCH_SIZE = 500

for start in range(
    0,
    len(ids),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(ids)
    )

    collection.upsert(
        ids=ids[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
        embeddings=vectors[start:end]
    )

    print(
        f"Stored {end}/{len(ids)} chunks"
    )


# ---------------------------------------------------------
# VERIFY DATABASE
# ---------------------------------------------------------

total = collection.count()


print("\n" + "=" * 70)
print("CHROMADB STORAGE COMPLETE")
print("=" * 70)

print(
    f"\nTotal vectors in database: {total}"
)

print(
    f"Database location: {CHROMA_DIR}"
)

print(
    f"Collection: {collection.name}"
)