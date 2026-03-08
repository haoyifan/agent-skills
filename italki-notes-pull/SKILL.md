---
name: italki-notes-pull
description: Pull lesson notes from italki teacher conversations only. Use when asked to extract note lines/vocab from a specific italki lesson/date/teacher chat. This skill only captures and returns raw notes (plus optional deduped line list) and does not generate translations, examples, or Anki fields.
---

# italki Notes Pull

Use this skill to extract teacher-provided notes from italki chat/lesson conversations.

## Scope (strict)

- Do: navigate italki, open the target teacher conversation, pull visible note lines, and return/export raw notes.
- Do: optionally provide a cleaned/deduped plain list of note lines.
- Do not: generate translations, examples, grammar metadata, images, or Anki card fields.
- Do not: add cards to Anki from this skill.

For translation/card generation, hand off to `anki-vocab-ingest` after extraction.

## Workflow

1. Confirm target
   - Teacher name
   - Date window or lesson id
   - Whether to pull only latest block or all currently accessible conversation notes

2. Open source in italki
   - Prefer direct lesson URL when available (`/lesson/<id>`).
   - If note body is not on lesson page, open teacher avatar/conversation thread.

3. Extract notes
   - Capture teacher note-like lines (short vocab/phrases/sentences used in lesson context).
   - Keep original language and original wording.
   - Exclude obvious system/event lines (e.g., “Lesson starts in 30 mins”, scheduling metadata).

4. Clean output
   - Preserve original order.
   - Remove exact duplicates.
   - Keep punctuation/diacritics.

5. Deliver results
   - Return:
     - `RAW_NOTES` (verbatim block)
     - `CLEAN_NOTES` (one-per-line list)
   - Save to workspace artifact when useful:
     - `reports/italki-notes-<teacher>-<yyyy-mm-dd>.txt`

6. Handoff (optional)
   - If user asks to continue: pass `CLEAN_NOTES` into `anki-vocab-ingest` for review-first card generation.

## Output format

Use this structure in chat:

- `TEACHER:`
- `SOURCE:` lesson URL or conversation URL
- `DATE_SCOPE:`
- `RAW_NOTES:`
- `CLEAN_NOTES:`
- `COUNT:`

## Reliability notes

- Browser relay can attach to the wrong tab; verify active URL before extraction.
- If extraction is blocked/stuck, capture a screenshot artifact and report blocker clearly.
- Prefer visible evidence over guessing.
