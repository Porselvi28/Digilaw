import json
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.models.case import Case
from app.models.evidence import EvidenceAnalysis
from app.models.relevance import LegalRelevanceAnalysis
from app.models.similar_case import SimilarCase
from app.schemas.similar_case import SimilarCaseResult
from app.services.rag_service import gemini_client, collection, embedding_model, filter_semantic_results

def generate_similar_cases(case_id: int, db: Session):
    # 1. Validate Case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    # 2. Retrieve evidence facts
    evidence_analyses = db.query(EvidenceAnalysis).filter(
        EvidenceAnalysis.case_id == case_id,
        EvidenceAnalysis.status == "completed"
    ).all()
    
    # 3. Retrieve legal relevance
    relevance_analyses = db.query(LegalRelevanceAnalysis).filter(
        LegalRelevanceAnalysis.case_id == case_id,
        LegalRelevanceAnalysis.status == "completed"
    ).all()

    # 4. Build a meaningful semantic query
    query_parts = [f"Legal Domain: {case.legal_domain}", f"Case Context: {case.description}"]
    
    for ev in evidence_analyses:
        if ev.facts:
            claims = ev.facts.get("claims_allegations", [])
            events = ev.facts.get("events", [])
            for c in claims:
                query_parts.append(f"Claim: {c}")
            for e in events:
                query_parts.append(f"Event: {e}")
                
    for rel in relevance_analyses:
        if rel.legal_source:
            query_parts.append(f"Relevant Law: {rel.legal_source}")

    search_query = "\n".join(query_parts)
    
    if not search_query.strip():
        search_query = case.title

    # 5. Semantic Search in ChromaDB specifically for Judgments
    query_embedding = embedding_model.encode(search_query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"document_type": "Judgment"}
    )
    
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    if not documents:
        return [] # No judgments found in the DB at all

    # 6. Relevance Filtering
    filtered_documents, filtered_metadatas = filter_semantic_results(documents, metadatas, distances)
    
    if not filtered_documents:
        return []

    # 7. Build Context for Gemini
    context_parts = []
    for i, doc in enumerate(filtered_documents):
        meta = filtered_metadatas[i]
        title = meta.get("title", "Unknown")
        year = meta.get("year", "Unknown")
        court = meta.get("court", "Unknown")
        citation = meta.get("source", "Unknown")
        context_parts.append(f"--- JUDGMENT {i+1} ---\nTitle: {title}\nCourt: {court}\nYear: {year}\nCitation: {citation}\nExcerpt: {doc}\n")
        
    judgments_context = "\n".join(context_parts)

    # 8. Prompt Gemini
    prompt = f"""
You are DigiLaw, an expert Indian legal assistant.
Your task is to analyze the user's case and determine how the retrieved authoritative judgments are similar or relevant.

USER CASE SUMMARY:
{search_query}

RETRIEVED JUDGMENTS:
{judgments_context}

INSTRUCTIONS:
1. Explain how each retrieved judgment shares a similar factual or legal pattern with the user's case.
2. Use cautious language (e.g., "may provide useful reference", "discusses a similar pattern"). NEVER claim a judgment guarantees a specific outcome.
3. Clearly distinguish between the user's facts and the judgment's facts.
4. DO NOT invent citations, case names, courts, dates, or legal principles. ONLY use the details provided in the RETRIEVED JUDGMENTS.
5. If a judgment is completely irrelevant despite being retrieved, do not include it in the output array.
6. Provide a small snippet or summary of the most relevant part of the judgment in `relevant_passage`.
7. Output MUST be a valid JSON array of objects following this exact schema:

{{
  "judgment_title": "string",
  "court": "string or null",
  "judgment_year": "string or null",
  "citation": "string or null",
  "similarity_explanation": "string",
  "relevant_passage": "string or null"
}}
"""

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    last_error = None
    response_text = ""

    for model_name in models_to_try:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            response_text = response.text
            break
        except Exception as e:
            print(f"Gemini model failed for similar cases: {model_name}")
            print(str(e))
            last_error = e

    if not response_text and last_error:
        fail_record = SimilarCase(
            case_id=case_id,
            judgment_title="Error",
            similarity_explanation="Failed to generate recommendations.",
            status="failed",
            error_message="An internal processing error occurred during generation."
        )
        db.add(fail_record)
        db.commit()
        raise RuntimeError("All Gemini models failed for similar case generation.")

    # 9. Parse and Save
    json_str = response_text.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()

    try:
        parsed_data = json.loads(json_str)
        if not isinstance(parsed_data, list):
            parsed_data = [parsed_data]
            
        adapter = TypeAdapter(list[SimilarCaseResult])
        validated_results = adapter.validate_python(parsed_data)
        
        # Avoid duplicate re-runs by clearing previous pending/failed/completed cases
        db.query(SimilarCase).filter(
            SimilarCase.case_id == case_id
        ).delete()
        
        saved_records = []
        for i, res in enumerate(validated_results):
            # Attempt to map back to the similarity score if titles match
            score = None
            for idx, meta in enumerate(filtered_metadatas):
                if meta.get("title") == res.judgment_title and idx < len(distances):
                    score = distances[idx]
                    break
                    
            record = SimilarCase(
                case_id=case_id,
                judgment_title=res.judgment_title,
                court=res.court,
                judgment_year=res.judgment_year,
                citation=res.citation,
                similarity_explanation=res.similarity_explanation,
                relevant_passage=res.relevant_passage,
                similarity_score=float(score) if score is not None else None,
                status="completed"
            )
            db.add(record)
            saved_records.append(record)
            
        db.commit()
        for r in saved_records:
            db.refresh(r)
            
        return saved_records

    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Similar case parse error: %s", str(e))
        db.rollback()
        fail_record = SimilarCase(
            case_id=case_id,
            judgment_title="Error",
            similarity_explanation="Failed to parse JSON.",
            status="failed",
            error_message="An internal processing error occurred while parsing the output."
        )
        db.add(fail_record)
        db.commit()
        raise ValueError("Failed to parse Gemini output due to an internal error.")

def get_similar_cases(case_id: int, db: Session):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")
        
    return db.query(SimilarCase).filter(
        SimilarCase.case_id == case_id
    ).all()
