import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


# =========================================================
# DIGILAW RAG TEST
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "processed" / "chroma_db"


# =========================================================
# LOAD API KEY
# =========================================================

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )


# =========================================================
# GEMINI
# =========================================================

gemini_client = genai.Client(
    api_key=api_key
)


# =========================================================
# EMBEDDING MODEL
# =========================================================

print("=" * 70)
print("DIGILAW RAG TEST")
print("=" * 70)

print("\nLoading embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# =========================================================
# CHROMADB
# =========================================================

print("\nConnecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = chroma_client.get_collection(
    name="digilaw_legal_knowledge"
)

print(
    f"Vectors available: {collection.count()}"
)


# =========================================================
# EXTRACT SECTION NUMBER
# =========================================================

def extract_section_number(query):

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

    query_lower = query.lower()

    # -----------------------------------------------------
    # ACTS
    # -----------------------------------------------------

    if (
        "bharatiya nyaya sanhita" in query_lower
        or re.search(r"\bbns\b", query_lower)
    ):
        return "BHARATIYA_NYAYA_SANHITA_2023"

    if (
        "bharatiya nagarik suraksha sanhita"
        in query_lower
        or re.search(r"\bbnss\b", query_lower)
    ):
        return "BHARATIYA_NAGARIK_SURAKSHA_SANHITA_2023"

    if (
        "bharatiya sakshya adhiniyam"
        in query_lower
        or re.search(r"\bbsa\b", query_lower)
    ):
        return "BHARATIYA_SAKSHYA_ADHINIYAM_2023"

    # -----------------------------------------------------
    # JUDGMENTS
    # -----------------------------------------------------

    if "vishaka" in query_lower:
        return "VISHAKA_V_STATE_OF_RAJASTHAN_1997"

    if "kesavananda bharati" in query_lower:
        return (
            "KESAVANANDA_BHARATI_V_STATE_OF_KERALA_1973"
        )

    if "maneka gandhi" in query_lower:
        return "MANEKA_GANDHI_V_UNION_OF_INDIA_1978"

    if "navtej singh johar" in query_lower:
        return (
            "NAVTEJ_SINGH_JOHAR_V_UNION_OF_INDIA_2018"
        )

    if "puttaswamy" in query_lower:
        return "PUTTASWAMY_V_UNION_OF_INDIA_2017"

    return None


# =========================================================
# EXACT SECTION SEARCH
# =========================================================

def search_exact_section(
    section_number,
    document_id
):

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

    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    return documents, metadatas


# =========================================================
# EXACT DOCUMENT SEARCH
# =========================================================

def search_exact_document(
    document_id
):

    results = collection.get(
        where={
            "document_id": document_id
        },
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    return documents, metadatas


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def semantic_search(query):

    query_embedding = (
        embedding_model
        .encode(query)
        .tolist()
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=5
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    return (
        documents,
        metadatas,
        distances
    )


# =========================================================
# RELEVANCE FILTER
# =========================================================

def filter_semantic_results(
    documents,
    metadatas,
    distances
):

    if not documents:
        return [], []

    print("\nSemantic distances:")

    for i, distance in enumerate(distances):

        title = metadatas[i].get(
            "title",
            "Unknown"
        )

        section = metadatas[i].get(
            "section",
            "N/A"
        )

        print(
            f"{i + 1}. "
            f"distance={distance:.4f} | "
            f"{title} | "
            f"Section={section}"
        )

    # -----------------------------------------------------
    # Smaller Chroma distance = more similar.
    #
    # We use a relative threshold rather than assuming
    # that every legal question has the same distance.
    # -----------------------------------------------------

    best_distance = distances[0]

    # Keep candidates that are reasonably close to the
    # best result.
    relative_threshold = 0.20

    filtered_documents = []
    filtered_metadatas = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if (
            distance
            <= best_distance + relative_threshold
        ):

            filtered_documents.append(
                document
            )

            filtered_metadatas.append(
                metadata
            )

    # -----------------------------------------------------
    # If filtering became too aggressive, keep the best
    # result rather than returning nothing.
    # -----------------------------------------------------

    if not filtered_documents:

        filtered_documents = [
            documents[0]
        ]

        filtered_metadatas = [
            metadatas[0]
        ]

    print(
        f"\nRelevant chunks after filtering: "
        f"{len(filtered_documents)}"
    )

    return (
        filtered_documents,
        filtered_metadatas
    )


# =========================================================
# RETRIEVE CONTEXT
# =========================================================

def retrieve_context(query):

    section_number = extract_section_number(
        query
    )

    document_id = detect_document(
        query
    )

    # =====================================================
    # MODE 1: EXACT ACT + SECTION
    # =====================================================

    if section_number and document_id:

        print(
            f"\nDetected section: {section_number}"
        )

        print(
            f"Detected document: {document_id}"
        )

        documents, metadatas = (
            search_exact_section(
                section_number,
                document_id
            )
        )

        if documents:

            print(
                "\nExact legal section found."
            )

            return (
                documents,
                metadatas,
                "exact_section"
            )

        print(
            "\nExact section not found."
        )

    # =====================================================
    # MODE 2: EXACT DOCUMENT / JUDGMENT
    # =====================================================

    if document_id:

        print(
            f"\nDetected document: {document_id}"
        )

        documents, metadatas = (
            search_exact_document(
                document_id
            )
        )

        if documents:

            print(
                "\nExact document found."
            )

            # Limit context sent to Gemini.
            max_chunks = 8

            documents = documents[:max_chunks]
            metadatas = metadatas[:max_chunks]

            return (
                documents,
                metadatas,
                "exact_document"
            )

        print(
            "\nDocument not found."
        )

    # =====================================================
    # MODE 3: SEMANTIC SEARCH
    # =====================================================

    print(
        "\nUsing semantic search..."
    )

    (
        documents,
        metadatas,
        distances
    ) = semantic_search(query)

    print(
        f"Retrieved {len(documents)} "
        f"semantic candidates."
    )

    (
        filtered_documents,
        filtered_metadatas
    ) = filter_semantic_results(
        documents,
        metadatas,
        distances
    )

    return (
        filtered_documents,
        filtered_metadatas,
        "semantic_filtered"
    )


# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(
    documents,
    metadatas
):

    context_parts = []

    for i, document in enumerate(
        documents
    ):

        metadata = metadatas[i]

        title = metadata.get(
            "title",
            "Unknown"
        )

        section = metadata.get(
            "section",
            "N/A"
        )

        source = metadata.get(
            "source",
            "Unknown"
        )

        document_type = metadata.get(
            "document_type",
            "Unknown"
        )

        context_parts.append(
            f"""
SOURCE {i + 1}

Title: {title}
Document Type: {document_type}
Section: {section}
Source: {source}

Legal Text:
{document}
"""
        )

    return "\n".join(
        context_parts
    )


# =========================================================
# GENERATE ANSWER WITH GEMINI
# =========================================================

def generate_answer(
    question,
    context
):

    prompt = f"""
You are DigiLaw, an Indian legal information
assistant.

Answer the user's question ONLY using the
legal information provided in the CONTEXT.

STRICT RULES:

1. Do not invent laws, sections, punishments,
   procedures, judgments, dates, or legal facts.

2. Do not rely on general knowledge when the
   required information is not present in the
   supplied context.

3. If the context does not contain enough
   information, say:

"The available DigiLaw documents do not
contain enough information to answer this
question."

4. Mention the relevant Act, section,
   judgment, or government procedure when
   available.

5. Explain the answer clearly and simply.

6. Do not create sources that are not present
   in the context.

7. This system provides legal information,
   not personalized legal advice.

CONTEXT:

{context}

USER QUESTION:

{question}

Provide a concise answer based only on
the supplied legal context.
"""

    # =====================================================
    # MODEL FALLBACK
    # =====================================================

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    last_error = None

    for model_name in models_to_try:

        try:

            print(
                f"\nTrying Gemini model: "
                f"{model_name}"
            )

            response = (
                gemini_client
                .models
                .generate_content(
                    model=model_name,
                    contents=prompt
                )
            )

            print(
                f"Successfully used: "
                f"{model_name}"
            )

            return response.text

        except Exception as error:

            print(
                f"\nModel {model_name} failed:"
            )

            print(
                str(error)
            )

            last_error = error

    print(
        "\nAll Gemini models failed."
    )

    raise last_error


# =========================================================
# DISPLAY SOURCES
# =========================================================

def display_sources(
    metadatas
):

    print(
        "\n" + "=" * 70
    )

    print(
        "SOURCES USED"
    )

    print(
        "=" * 70
    )

    seen = set()

    for metadata in metadatas:

        title = metadata.get(
            "title",
            "Unknown"
        )

        section = metadata.get(
            "section",
            "N/A"
        )

        source = metadata.get(
            "source",
            "Unknown"
        )

        document_type = metadata.get(
            "document_type",
            "Unknown"
        )

        key = (
            title,
            section,
            source
        )

        if key in seen:
            continue

        seen.add(key)

        print(
            f"\nTitle: {title}"
        )

        print(
            f"Document Type: "
            f"{document_type}"
        )

        print(
            f"Section: {section}"
        )

        print(
            f"Source: {source}"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    question = input(
        "\nEnter your legal question: "
    )

    print(
        "\nSearching DigiLaw knowledge base..."
    )

    (
        documents,
        metadatas,
        retrieval_mode
    ) = retrieve_context(
        question
    )

    if not documents:

        print(
            "\nNo relevant legal information found."
        )

        return

    print(
        f"\nRetrieval mode: "
        f"{retrieval_mode}"
    )

    print(
        f"Retrieved {len(documents)} "
        f"legal chunks."
    )

    # -----------------------------------------------------
    # BUILD CONTEXT
    # -----------------------------------------------------

    context = build_context(
        documents,
        metadatas
    )

    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    print(
        "\nSending retrieved context to Gemini..."
    )

    answer = generate_answer(
        question,
        context
    )

    # -----------------------------------------------------
    # ANSWER
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "DIGILAW ANSWER"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{answer}"
    )

    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    display_sources(
        metadatas
    )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "RAG TEST COMPLETE"
    )

    print(
        "=" * 70
    )


# =========================================================
# PROGRAM ENTRY
# =========================================================

if __name__ == "__main__":

    main() 