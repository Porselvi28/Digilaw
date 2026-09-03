import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


# =========================================================
# PATHS
# =========================================================

# backend/app/services/rag_service.py
# parents[0] = services
# parents[1] = app
# parents[2] = backend
# parents[3] = DigiLaw

BASE_DIR = Path(__file__).resolve().parents[3]

CHROMA_DIR = BASE_DIR / "processed" / "chroma_db"


# =========================================================
# LOAD ENVIRONMENT
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

print("Loading DigiLaw embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# =========================================================
# CHROMADB
# =========================================================

print("Connecting to DigiLaw ChromaDB...")

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

def extract_section_number(query: str):

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

def detect_document(query: str):

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
    section_number: str,
    document_id: str
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
    document_id: str
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

def semantic_search(
    query: str
):

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

    best_distance = distances[0]

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
    # Keep best result if filtering removed everything
    # -----------------------------------------------------

    if not filtered_documents:

        filtered_documents = [
            documents[0]
        ]

        filtered_metadatas = [
            metadatas[0]
        ]

    return (
        filtered_documents,
        filtered_metadatas
    )


# =========================================================
# RETRIEVE CONTEXT
# =========================================================

def retrieve_context(
    query: str
):

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

        documents, metadatas = (
            search_exact_section(
                section_number,
                document_id
            )
        )

        if documents:

            return (
                documents,
                metadatas,
                "exact_section"
            )

    # =====================================================
    # MODE 2: EXACT DOCUMENT / JUDGMENT
    # =====================================================

    if document_id:

        documents, metadatas = (
            search_exact_document(
                document_id
            )
        )

        if documents:

            max_chunks = 8

            documents = documents[
                :max_chunks
            ]

            metadatas = metadatas[
                :max_chunks
            ]

            return (
                documents,
                metadatas,
                "exact_document"
            )

    # =====================================================
    # MODE 3: SEMANTIC SEARCH
    # =====================================================

    (
        documents,
        metadatas,
        distances
    ) = semantic_search(
        query
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
    question: str,
    context: str
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

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    last_error = None

    for model_name in models_to_try:

        try:

            response = (
                gemini_client
                .models
                .generate_content(
                    model=model_name,
                    contents=prompt
                )
            )

            return response.text

        except Exception as error:

            print(
                f"Gemini model failed: "
                f"{model_name}"
            )

            print(
                str(error)
            )

            last_error = error

    if last_error:
        raise last_error

    raise RuntimeError(
        "All Gemini models failed."
    )


# =========================================================
# BUILD SOURCE INFORMATION
# =========================================================

def build_sources(
    metadatas
):

    sources = []

    seen = set()

    for metadata in metadatas:

        source = {
            "title": metadata.get(
                "title",
                "Unknown"
            ),
            "document_type": metadata.get(
                "document_type",
                "Unknown"
            ),
            "section": metadata.get(
                "section",
                "N/A"
            ),
            "source": metadata.get(
                "source",
                "Unknown"
            )
        }

        key = (
            source["title"],
            source["section"],
            source["source"]
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            source
        )

    return sources


# =========================================================
# PUBLIC RAG SERVICE
# =========================================================

def ask_legal_question(
    question: str
):

    question = question.strip()

    if not question:

        raise ValueError(
            "Question cannot be empty."
        )

    # -----------------------------------------------------
    # RETRIEVE
    # -----------------------------------------------------

    (
        documents,
        metadatas,
        retrieval_mode
    ) = retrieve_context(
        question
    )

    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not documents:

        return {
            "question": question,
            "answer": (
                "No relevant legal information "
                "was found in the DigiLaw "
                "knowledge base."
            ),
            "retrieval_mode": retrieval_mode,
            "sources": []
        }

    # -----------------------------------------------------
    # BUILD CONTEXT
    # -----------------------------------------------------

    context = build_context(
        documents,
        metadatas
    )

    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

    answer = generate_answer(
        question,
        context
    )

    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    sources = build_sources(
        metadatas
    )

    # -----------------------------------------------------
    # RETURN API RESPONSE
    # -----------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "retrieval_mode": retrieval_mode,
        "sources": sources
    }