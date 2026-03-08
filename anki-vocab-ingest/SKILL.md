---
name: anki-vocab-ingest
description: Create review-first vocab batches for Anki (CSV preview → approval → add) with lemma normalization, structured fields, language-specific audio, and sync. Use for vocab from text, images, or lesson notes in any language (especially Russian/Spanish).
---

# Anki Vocab Ingest

Use this skill to run a strict **preview → approve → add** pipeline.

## Workflow

1. Collect source vocab (text, lesson notes, OCR from image).
2. Normalize each item into lemma/base form for `Front`.
3. Generate `Back` with:
   - English meaning
   - blank line
   - extra grammar lines (one per line)
   - if the card is a noun, include a picture in `Back` (image of your choice) in addition to the translation
4. Generate one concise `example` sentence.
5. Run preflight checks:
   - HyperTTS add-on installed
   - HyperTTS `GoogleTranslate` (free) enabled
   - target note model has `Front`, `Back`, `example`, `sound`
6. Inspect existing Anki decks and propose the best target deck for the batch.
   - If no good match exists, propose a new deck name.
7. Build a CSV preview and save it as a `.csv` file.
   - In chat surfaces (Telegram/WhatsApp/etc.), send the CSV as a file attachment to the user for review (do not only paste inline text).
   - Also include the local file path as fallback.
8. Add cards only after explicit approval of content and deck.
9. Generate audio with row-level language (`sound_lang`) and populate `sound`, then sync.

Never skip step 5 unless user explicitly asks to bypass preview.

## CSV schema

Required columns:
- `Front`
- `Back`

Optional columns:
- `example`
- `sound_text` (defaults to `Front`)
- `sound_lang` (defaults to CLI `--default-lang`)
- `pos` (e.g., `noun`, `verb`, `adjective`)
- `back_image_url` (required if `pos=noun`; rendered in `Back`)

## Script

Use `scripts/anki_vocab_pipeline.py`.

### Preview only (with automatic deck proposal)

```bash
python3 scripts/anki_vocab_pipeline.py \
  --csv ./preview.csv \
  --preview-out ./preview.out.csv
```

Always share `--preview-out` file with the user for approval before any add/sync.

### Add + sync (deck must be explicit after approval)

```bash
python3 scripts/anki_vocab_pipeline.py \
  --csv ./preview.csv \
  --deck "Русский::TEST_HyperTTS_Sandbox" \
  --add --sync
```

### Common options

- `--model "Basic and Reverse"`
- `--default-lang ru` (or `es`)
- `--allow-duplicates`
- `--fix-hypertts-config` (auto-enable HyperTTS GoogleTranslate if disabled)

## Language behavior

- Keep workflow language-agnostic.
- Use `sound_lang` per row for mixed-language batches.
- Never assume one language for all cards (e.g., do not use `ru` for Spanish rows).
- For Russian/Spanish defaults and formatting rules, read `references/vocab-format-guidelines.md`.

## Safety checks

- Verify AnkiConnect is reachable before processing.
- Run duplicate check (`canAddNotes`) during preview.
- If duplicates are blocked, report counts in preview summary.
- Do not write notes until user approval is explicit.
