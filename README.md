# PII Redaction Service

A deployable web service that automatically detects and redacts Personally Identifiable Information (PII) from Word documents (`.docx`).

## Approach

This tool uses a **hybrid Regex + NER (Named Entity Recognition)** pipeline:

1. **Regex-based detection** handles structured, format-driven PII: email addresses, phone numbers, Social Security Numbers, credit card numbers (validated with the Luhn algorithm), dates of birth, and Indian-specific identifiers (PAN, GSTIN, CIN, DIN). These are fast and highly precise.

2. **spaCy NER (`en_core_web_sm`)** handles open-vocabulary, unstructured PII: person names, company/organisation names, and physical addresses. The engine also expands detected full names to include standalone first names (e.g., if "John Doe" is found, later references to "John" are also redacted).

3. **Faker library** generates consistent, realistic fake replacements — every unique real entity always maps to the same fake value throughout the document, preserving referential integrity (e.g., "Rashi Patil" → "Jennifer Kim" everywhere it appears).

### Tradeoffs & Known False Positives / Negatives

| Category | Precision | Recall | Notes |
|---|---|---|---|
| Emails | 1.00 | 1.00 | Regex is highly reliable |
| Phone Numbers | 1.00 | 1.00 | Flexible regex + cue-word validation |
| SSN / Credit Cards | 1.00 | 1.00 | Luhn algorithm eliminates false positives |
| Dates of Birth | 1.00 | 1.00 | — |
| Person Names | 1.00 | 1.00 | First-name fallback heuristic improves recall |
| Organisations | 0.33 | 1.00 | Geographic terms (e.g., "Maharashtra") can be misclassified as ORG by spaCy |
| Addresses | 0.00 | 0.00 | spaCy `GPE`/`LOC` does not identify long comma-separated address strings as single entities |

**Overall F1 (Accuracy): 89%**

**Known false positives**: The `en_core_web_sm` model may tag well-known geographic regions like "Andheri East" or "Maharashtra" as ORG entities, causing them to be unnecessarily redacted. A curated stop-list (`ORG_STOPLIST`) was used to filter out common legal/regulatory terms.

**Known false negatives**: Multi-line or abbreviated address blocks (e.g., split across Word XML runs) may be missed by the address heuristic.

---

## Running Locally

```bash
cd pii_redaction
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` for uptime checks |
| `POST` | `/redact` | Accepts a multipart `.docx` upload, returns a redacted `.docx` |

**File size limit**: 10MB. Uploads over this size will receive an HTTP 413 error.
