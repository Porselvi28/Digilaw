from pathlib import Path

import chromadb


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = (
    BASE_DIR
    / "processed"
    / "chroma_db"
)


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name="digilaw_legal_knowledge"
)


print("=" * 70)
print("JUDGMENT DOCUMENT CHECK")
print("=" * 70)


results = collection.get(
    where={
        "document_type": "Judgment"
    },
    include=[
        "metadatas"
    ]
)


metadatas = results.get(
    "metadatas",
    []
)


seen = set()


for metadata in metadatas:

    document_id = metadata.get(
        "document_id",
        "UNKNOWN"
    )

    title = metadata.get(
        "title",
        "UNKNOWN"
    )

    if document_id in seen:
        continue

    seen.add(document_id)

    print(
        f"\nDocument ID: {document_id}"
    )

    print(
        f"Title: {title}"
    )


print("\n" + "=" * 70)

print(
    f"Judgment documents found: "
    f"{len(seen)}"
)

print("=" * 70)