import json
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.evidence import EvidenceAnalysis
from app.models.relevance import LegalRelevanceAnalysis
from app.schemas.relevance import LegalRelevanceResult
from app.services.rag_service import gemini_client, retrieve_context, build_context
import pydantic

def analyze_legal_relevance(case_id: int, db: Session) -> list[LegalRelevanceAnalysis]:
    """
    Analyzes the legal relevance of evidence facts extracted for a case.
    """
    # 1. Fetch case and its completed evidence analyses
    db_case = db.query(Case).filter(Case.id == case_id).first()
    if not db_case:
        raise ValueError(f"Case with ID {case_id} not found.")

    evidence_records = db.query(EvidenceAnalysis).filter(
        EvidenceAnalysis.case_id == case_id,
        EvidenceAnalysis.status == "completed"
    ).all()

    if not evidence_records:
        raise ValueError("No completed evidence analyses found for this case. Run evidence analysis first.")

    # Clear previous legal relevance records for this case to ensure idempotency
    db.query(LegalRelevanceAnalysis).filter(LegalRelevanceAnalysis.case_id == case_id).delete()
    db.commit()

    results = []

    for evidence in evidence_records:
        facts_dict = evidence.facts
        if not facts_dict:
            continue
            
        # Extract important facts: Claims/Allegations and Events are usually most legally relevant
        important_facts = []
        if "claims_allegations" in facts_dict and isinstance(facts_dict["claims_allegations"], list):
            important_facts.extend(facts_dict["claims_allegations"])
        if "events" in facts_dict and isinstance(facts_dict["events"], list):
            important_facts.extend(facts_dict["events"])

        for fact in important_facts:
            # Skip empty or very short facts
            if not fact or len(fact.strip()) < 10:
                continue

            # Create pending relevance record
            relevance_record = LegalRelevanceAnalysis(
                case_id=case_id,
                evidence_id=evidence.id,
                fact_reference=fact,
                status="pending"
            )
            db.add(relevance_record)
            db.commit()
            db.refresh(relevance_record)

            try:
                # Retrieve legal context using existing RAG infrastructure
                documents, metadatas, retrieval_mode = retrieve_context(fact)
                
                if not documents:
                    relevance_record.status = "completed"
                    relevance_record.relevance_explanation = "No relevant legal information was found in the knowledge base for this fact."
                    db.commit()
                    db.refresh(relevance_record)
                    results.append(relevance_record)
                    continue

                context_text = build_context(documents, metadatas)

                # Prompt Gemini
                prompt = f"""
You are an expert Indian legal assistant. Analyze the following evidence fact against the provided legal context.
Determine if and how the legal context applies to the fact.

STRICT RULES:
1. Do NOT invent laws, sections, or judgments.
2. Rely ONLY on the provided legal context.
3. If the context is insufficient or irrelevant, explicitly state that the available legal context is insufficient.
4. DO NOT say the evidence definitely proves a legal claim. Use cautious wording such as "may be relevant", "potentially relates to", or "based on the retrieved material".
5. Distinguish the fact from your legal interpretation.

EVIDENCE FACT:
{fact}

LEGAL CONTEXT:
{context_text}

Return the result as STRICT, VALID JSON matching this exact schema:
{{
  "legal_source": "string (e.g., Act name, Judgment title, or 'None found')",
  "act_judgment_info": "string (Specific section or rule)",
  "relevance_explanation": "string (Explanation of the potential relationship)",
  "relevance_score": integer (1 to 10 indicating potential relevance, or null)
}}
"""
                models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
                response_text = None
                last_error = None
                
                for model_name in models_to_try:
                    try:
                        response = gemini_client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        response_text = response.text
                        break
                    except Exception as e:
                        print(f"Gemini model failed: {model_name} - {str(e)}")
                        last_error = e
                
                if not response_text:
                    raise Exception(f"All Gemini models failed. Last error: {str(last_error)}")

                # Clean and parse JSON
                raw_json = response_text.strip()
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:]
                if raw_json.startswith("```"):
                    raw_json = raw_json[3:]
                if raw_json.endswith("```"):
                    raw_json = raw_json[:-3]
                raw_json = raw_json.strip()

                parsed_data = json.loads(raw_json)
                validated_data = LegalRelevanceResult(**parsed_data)

                # Update the record
                relevance_record.legal_source = validated_data.legal_source
                
                # We can append act_judgment_info to legal_source or keep it in explanation if we want,
                # but let's format it nicely into legal_source if it exists
                if validated_data.act_judgment_info and validated_data.act_judgment_info.lower() not in ["none", "n/a", "none found"]:
                    relevance_record.legal_source = f"{validated_data.legal_source} - {validated_data.act_judgment_info}"
                
                relevance_record.relevance_explanation = validated_data.relevance_explanation
                relevance_record.relevance_score = validated_data.relevance_score
                relevance_record.status = "completed"

            except pydantic.ValidationError as e:
                relevance_record.status = "failed"
                relevance_record.error_message = "AI returned invalid format."
            except json.JSONDecodeError as e:
                relevance_record.status = "failed"
                relevance_record.error_message = "AI returned malformed JSON."
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("Relevance analysis failed: %s", str(e))
                relevance_record.status = "failed"
                relevance_record.error_message = "Analysis failed due to an internal error."

            db.commit()
            db.refresh(relevance_record)
            results.append(relevance_record)

    return results
