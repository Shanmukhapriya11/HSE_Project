# Safety Audit Copilot

**Evidence-Linked HSE Audit Drafting Prototype — Synthetic Demo Data**

## Purpose

Safety Audit Copilot converts unstructured facility logs into a structured audit draft while preserving a direct link between every generated finding and its exact source sentence. It supports documentation and human review; it is not an autonomous compliance auditor, ISO 45001 certification tool, regulatory determination, or substitute for a qualified HSE auditor.

## Architecture and pipeline

The standalone Streamlit app uses a modular, deterministic pipeline:

`Facility logs → observation extraction → hazard classification → evidence linking → preliminary risk prioritization → missing-information detection → draft findings/CAPA → human HSE review`

The main functions in `app.py` are deliberately small and transparent: `split_log_into_observations()`, `classify_observation()`, `identify_location()`, `classify_finding_type()`, `estimate_risk()`, `identify_missing_information()`, `recommend_follow_up()`, `generate_capa_suggestion()`, and `assemble_audit_report()`.

## Evidence traceability

Each finding retains the exact, unmodified source sentence, the application’s interpretation, and the rule or keywords that triggered it. The system does not generate findings without source evidence. Missing facts become unanswered questions rather than invented answers.

## Preliminary risk scoring

Risk score is `Likelihood × Severity`, with both values from 1–5. Levels are Low (1–4), Medium (5–9), High (10–16), and Critical (17–25). Initial likelihood comes from the finding type and initial severity from a documented category default. Users can edit likelihood and severity; derived scores recalculate. Every automated score is labelled a preliminary rule-based estimate requiring verification.

## Human-in-the-loop review

Qualified personnel must review the extraction, finding type, category, evidence attribution, risk inputs, recommendations and CAPA draft. CAPA ownership and target dates are intentionally blank. The exported DOCX includes limitations and a reviewer sign-off section.

## Limitations

- Keyword matching cannot understand all context, negation, terminology or complex sentence structure.
- Sentence splitting is intentionally simple.
- Category defaults are demonstration rules, not a validated site risk method.
- Generic checklist references are not authoritative ISO 45001 clause text.
- Outputs depend entirely on the submitted logs and cannot establish compliance or causation.

## Install and run

From this `generator` folder:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The application normally opens at `http://localhost:8501`.

## Production direction and evaluation

A governed production system could use retrieval-augmented generation over licensed standards, an approved legal register, and controlled internal procedures. Each retrieved passage would need provenance, access control, versioning and expert validation. Evaluation should measure observation-extraction precision/recall, category and finding-type accuracy, evidence-attribution accuracy, unsupported-claim rate, risk-review agreement, and reviewer acceptance/override rates. Releases would require validation, monitoring, audit trails and formal HSE approval.
