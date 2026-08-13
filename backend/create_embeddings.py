from pathlib import Path
import json

from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "chunks_with_metadata.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "processed"
    / "embeddings"
)

OUTPUT_FILE = OUTPUT_DIR / "embeddings.json"


# ---------------------------------------------------------
# CREATE OUTPUT FOLDER
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# LOAD EMBEDDING MODEL
# ---------------------------------------------------------

print("=" * 70)
print("DIGILAW EMBEDDING PIPELINE")
print("=" * 70)

print("\nLoading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# ---------------------------------------------------------
# LOAD CHUNKS
# ---------------------------------------------------------

print("\nLoading legal chunks...")

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)

print(f"Loaded chunks: {len(chunks)}")


# ---------------------------------------------------------
# EXTRACT TEXT
# ---------------------------------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]


# ---------------------------------------------------------
# CREATE EMBEDDINGS
# ---------------------------------------------------------

print("\nCreating embeddings...")
print("This may take some time.")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    batch_size=32
)


# ---------------------------------------------------------
# ADD EMBEDDINGS TO CHUNKS
# ---------------------------------------------------------

embedded_chunks = []

for chunk, embedding in zip(
    chunks,
    embeddings
):

    chunk_with_embedding = {
        "chunk_id": chunk["chunk_id"],
        "text": chunk["text"],
        "metadata": chunk["metadata"],
        "embedding": embedding.tolist()
    }

    embedded_chunks.append(
        chunk_with_embedding
    )


# ---------------------------------------------------------
# SAVE EMBEDDINGS
# ---------------------------------------------------------

print("\nSaving embeddings...")

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        embedded_chunks,
        file,
        ensure_ascii=False
    )


# ---------------------------------------------------------
# FINISHED
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("EMBEDDING COMPLETE")
print("=" * 70)

print(f"\nTotal chunks: {len(embedded_chunks)}")

print(f"Embedding dimensions: {len(embeddings[0])}")

print(f"Saved to:")
print(OUTPUT_FILE)