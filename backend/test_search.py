import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = (
    BASE_DIR
    / "processed"
    / "chroma_db"
)


# =========================================================
# LOAD EMBEDDING MODEL
# =========================================================

print("=" * 70)
print("DIGILAW HYBRID LEGAL SEARCH")
print("=" * 70)

print("\nLoading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# =========================================================
# CONNECT TO CHROMADB
# =========================================================

print("\nConnecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name="digilaw_legal_knowledge"
)

print(
    f"Vectors available: {collection.count()}"
)


# =========================================================
# EXTRACT SECTION NUMBER
# =========================================================

def extract_section_number(query):
    """
    Detect section numbers such as:

    Section 316
    section 103
    Sec. 316
    sec 316
    """

    patterns = [
        r"\bsection\s+(\d+[A-Za-z]?)\b",
        r"\bsec\.?\s+(\d+[A-Za-z]?)\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# DETECT DOCUMENT
# =========================================================

def detect_document(query):
    """
    Detect which legal Act the user is referring to.
    """

    query_lower = query.lower()

    # -----------------------------------------------------
    # BNS
    # -----------------------------------------------------

    if (
        "bharatiya nyaya sanhita"
        in query_lower
        or re.search(r"\bbns\b", query_lower)
    ):

        return "BHARATIYA_NYAYA_SANHITA_2023"

    # -----------------------------------------------------
    # BNSS
    # -----------------------------------------------------

    if (
        "bharatiya nagarik suraksha sanhita"
        in query_lower
        or re.search(r"\bbnss\b", query_lower)
    ):

        return (
            "BHARATIYA_NAGARIK_SURAKSHA_SANHITA_2023"
        )

    # -----------------------------------------------------
    # BSA
    # -----------------------------------------------------

    if (
        "bharatiya sakshya adhiniyam"
        in query_lower
        or re.search(r"\bbsa\b", query_lower)
    ):

        return (
            "BHARATIYA_SAKSHYA_ADHINIYAM_2023"
        )

    return None


# =========================================================
# EXACT SECTION SEARCH
# =========================================================

def exact_section_search(
    section_number,
    document_id
):
    """
    Search ChromaDB using metadata.

    This is much more reliable than semantic similarity
    when the user explicitly asks for a legal section.
    """

    filters = {
        "$and": [
            {
                "section": section_number
            },
            {
                "document_id": document_id
            }
        ]
    }

    results = collection.get(
        where=filters,
        include=[
            "documents",
            "metadatas"
        ]
    )

    return results


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def semantic_search(query):
    """
    Semantic search for natural-language legal questions.
    """

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=5
    )

    return results


# =========================================================
# DISPLAY EXACT RESULTS
# =========================================================

def display_exact_results(results):

    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    ids = results.get(
        "ids",
        []
    )

    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not documents:

        print(
            "\nNo exact section found."
        )

        return False

    print(
        "\n" + "=" * 70
    )

    print(
        "EXACT LEGAL SECTION MATCH"
    )

    print(
        "=" * 70
    )

    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    for i in range(
        len(documents)
    ):

        print(
            "\n" + "-" * 70
        )

        print(
            f"RESULT {i + 1}"
        )

        # Chunk ID
        if ids:

            print(
                f"\nChunk ID:\n{ids[i]}"
            )

        # Metadata
        if metadatas:

            print(
                f"\nMetadata:\n{metadatas[i]}"
            )

        # Text
        print(
            f"\nText:\n{documents[i]}"
        )

    return True


# =========================================================
# DISPLAY SEMANTIC RESULTS
# =========================================================

def display_semantic_results(results):

    print(
        "\n" + "=" * 70
    )

    print(
        "TOP SEMANTIC RESULTS"
    )

    print(
        "=" * 70
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    ids = results["ids"][0]

    # -----------------------------------------------------
    # DISPLAY TOP RESULTS
    # -----------------------------------------------------

    for i in range(
        len(documents)
    ):

        print(
            "\n" + "-" * 70
        )

        print(
            f"RESULT {i + 1}"
        )

        print(
            f"\nChunk ID:\n{ids[i]}"
        )

        print(
            f"\nSimilarity distance:\n"
            f"{distances[i]}"
        )

        print(
            f"\nMetadata:\n"
            f"{metadatas[i]}"
        )

        print(
            f"\nText:\n"
            f"{documents[i]}"
        )


# =========================================================
# MAIN SEARCH
# =========================================================

def main():

    query = input(
        "\nEnter your legal question: "
    )

    print(
        f"\nSearching for: {query}"
    )

    # -----------------------------------------------------
    # DETECT SECTION
    # -----------------------------------------------------

    section_number = (
        extract_section_number(query)
    )

    # -----------------------------------------------------
    # DETECT ACT
    # -----------------------------------------------------

    document_id = detect_document(
        query
    )

    # -----------------------------------------------------
    # EXACT SEARCH
    # -----------------------------------------------------

    if (
        section_number
        and document_id
    ):

        print(
            f"\nDetected section: "
            f"{section_number}"
        )

        print(
            f"Detected document: "
            f"{document_id}"
        )

        results = exact_section_search(
            section_number,
            document_id
        )

        found = display_exact_results(
            results
        )

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not found:

            print(
                "\nExact section was not found."
            )

            print(
                "Falling back to semantic search..."
            )

            results = semantic_search(
                query
            )

            display_semantic_results(
                results
            )

    # -----------------------------------------------------
    # SEMANTIC SEARCH
    # -----------------------------------------------------

    else:

        print(
            "\nNo exact Act + section reference detected."
        )

        print(
            "Using semantic search..."
        )

        results = semantic_search(
            query
        )

        display_semantic_results(
            results
        )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "SEARCH COMPLETE"
    )

    print(
        "=" * 70
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()