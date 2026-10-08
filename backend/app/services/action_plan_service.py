import json
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.models.case import Case
from app.models.evidence import EvidenceAnalysis
from app.models.relevance import LegalRelevanceAnalysis
from app.models.missing_document import MissingDocumentRecommendation
from app.models.similar_case import SimilarCase
from app.models.action_plan import ActionPlan
from app.schemas.action_plan import ActionPlanStepResult
from app.services.rag_service import gemini_client

def generate_action_plan(case_id: int, db: Session):
    # 1. Retrieve the Case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    # 2. Gather Evidence
    evidence_analyses = db.query(EvidenceAnalysis).filter(
        EvidenceAnalysis.case_id == case_id,
        EvidenceAnalysis.status == "completed"
    ).all()
    evidence_text = []
    for ev in evidence_analyses:
        if ev.facts:
            claims = ev.facts.get("claims_allegations", [])
            events = ev.facts.get("events", [])
            evidence_text.extend([f"- Claim: {c}" for c in claims])
            evidence_text.extend([f"- Event: {e}" for e in events])

    # 3. Gather Legal Relevance
    relevance_analyses = db.query(LegalRelevanceAnalysis).filter(
        LegalRelevanceAnalysis.case_id == case_id,
        LegalRelevanceAnalysis.status == "completed"
    ).all()
    relevance_text = [
        f"- {r.legal_source}: {r.relevance_explanation}" 
        for r in relevance_analyses if r.legal_source
    ]

    # 4. Gather Missing Documents
    missing_docs = db.query(MissingDocumentRecommendation).filter(
        MissingDocumentRecommendation.case_id == case_id,
        MissingDocumentRecommendation.status == "completed"
    ).all()
    missing_docs_text = [
        f"- {md.document_name} ({md.document_category}): {md.reason}" 
        for md in missing_docs
    ]

    # 5. Gather Similar Cases
    similar_cases = db.query(SimilarCase).filter(
        SimilarCase.case_id == case_id,
        SimilarCase.status == "completed"
    ).all()
    similar_cases_text = [
        f"- {sc.judgment_title} ({sc.court or 'N/A'}, {sc.judgment_year or 'N/A'}): {sc.similarity_explanation}"
        for sc in similar_cases
    ]

    # Compile Full Context
    context_builder = [
        "USER CASE SUMMARY:",
        f"Title: {case.title}",
        f"Domain: {case.legal_domain}",
        f"Description: {case.description}",
        ""
    ]

    if evidence_text:
        context_builder.append("EVIDENCE / FACTS ESTABLISHED:")
        context_builder.extend(evidence_text)
        context_builder.append("")
        
    if relevance_text:
        context_builder.append("RELEVANT LEGAL RULES:")
        context_builder.extend(relevance_text)
        context_builder.append("")
        
    if missing_docs_text:
        context_builder.append("RECOMMENDED/MISSING DOCUMENTS:")
        context_builder.extend(missing_docs_text)
        context_builder.append("")
        
    if similar_cases_text:
        context_builder.append("SIMILAR LEGAL PRECEDENTS:")
        context_builder.extend(similar_cases_text)
        context_builder.append("")

    full_context = "\n".join(context_builder)

    prompt = f"""
You are DigiLaw, an expert Indian legal assistant.
Your task is to synthesize the following case information into a practical, ordered Action Plan for the user.

{full_context}

INSTRUCTIONS:
1. Generate an ordered sequence of action steps (1, 2, 3...) that the user should take.
2. Group the actions conceptually (e.g., Immediate Action, Document Collection, Procedural Step, Escalation).
3. Base your recommendations ONLY on the provided evidence, legal rules, missing documents, and precedents.
4. DO NOT invent laws, sections, courts, authorities, procedures, deadlines, fees, or outcomes.
5. If upstream information (like laws or similar cases) is missing, provide a general, limited action plan (e.g., "Consult a lawyer," "Gather initial facts") and mark it as uncertain.
6. Use cautious language (e.g., "may", "could", "consider verifying"). NEVER guarantee success or present the plan as formal legal advice.
7. Return a valid JSON array of objects strictly matching this schema:

{{
  "action_title": "string",
  "description": "string",
  "priority": "string (Immediate, High, Medium, Low)",
  "sequence_order": integer,
  "action_category": "string",
  "required_documents": "string or null",
  "related_legal_source": "string or null",
  "rationale": "string"
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
            print(f"Gemini model failed for action plan: {model_name}")
            print(str(e))
            last_error = e

    if not response_text and last_error:
        fail_record = ActionPlan(
            case_id=case_id,
            action_title="Error",
            description="Failed to generate action plan.",
            priority="Low",
            sequence_order=1,
            action_category="Error",
            rationale="Gemini generation failed.",
            status="failed",
            error_message="An internal processing error occurred during generation."
        )
        db.add(fail_record)
        db.commit()
        raise RuntimeError("All Gemini models failed for action plan generation.")

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
            
        adapter = TypeAdapter(list[ActionPlanStepResult])
        validated_results = adapter.validate_python(parsed_data)
        
        # Avoid duplicate re-runs by clearing previous action plans for this case
        db.query(ActionPlan).filter(
            ActionPlan.case_id == case_id
        ).delete()
        
        saved_records = []
        for res in validated_results:
            record = ActionPlan(
                case_id=case_id,
                action_title=res.action_title,
                description=res.description,
                priority=res.priority,
                sequence_order=res.sequence_order,
                action_category=res.action_category,
                required_documents=res.required_documents,
                related_legal_source=res.related_legal_source,
                rationale=res.rationale,
                status="completed"
            )
            db.add(record)
            saved_records.append(record)
            
        db.commit()
        for r in saved_records:
            db.refresh(r)
            
        # Return sorted by sequence order just to be safe
        return sorted(saved_records, key=lambda x: x.sequence_order)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Action plan parse error: %s", str(e))
        db.rollback()
        fail_record = ActionPlan(
            case_id=case_id,
            action_title="Error",
            description="Failed to parse JSON for action plan.",
            priority="Low",
            sequence_order=1,
            action_category="Error",
            rationale="JSON Parse Error",
            status="failed",
            error_message="An internal processing error occurred while parsing the output."
        )
        db.add(fail_record)
        db.commit()
        raise ValueError("Failed to parse Gemini output due to an internal error.")

def get_action_plan(case_id: int, db: Session):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")
        
    return db.query(ActionPlan).filter(
        ActionPlan.case_id == case_id
    ).order_by(ActionPlan.sequence_order).all()
