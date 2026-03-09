---
name: langpack-delivery
description: Generate and deliver daily language packs (article + translation notes + passage audio) to messaging channels for language immersion.
---

# Langpack Delivery

Use this skill to produce a daily language pack for any target language and deliver it reliably.

## Scope

- Generate one text pack per language/day.
- Generate one passage audio per language/day.
- Send text + audio to target chat/channel.
- Report explicit status fields.

Do not perform Anki card generation here. Hand off extracted vocab to `anki-vocab-ingest` when requested.

## Inputs

- `target_lang` (e.g., `ru`, `es`, `de`, `fr`, `ko`)
- `target_level` (required proficiency target: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`)
- `target_chat` (default user chat)
- `date` (default today in user timezone)
- optional `locale_policy` (fixed locale or random from approved locale list)

## Level-based generation rules (mandatory)

Generate content to match `target_level` difficulty.

- **A1–A2**: short sentences, high-frequency vocabulary, minimal idioms, clear literal phrasing.
- **B1**: everyday + work/study themes, some connectors, moderate sentence length.
- **B2**: richer argumentation, abstract themes, wider synonym range, natural idioms in moderation.
- **C1–C2**: dense authentic style, nuanced register, complex syntax, advanced discourse markers.

For every pack include:
1. Main text/article at the target level (target language only).
2. Plain English translation of the whole text (natural paragraph form).
3. Potentially new / common vocabulary and translation from the text.
4. Passage selected from the same text for audio, also level-aligned.

Translation style rule:
- Do **not** send line-by-line bilingual pairs in chat.
- Do **not** repeat each target-language sentence next to an English sentence.
- Send one clean target-language section, then one plain English translation section.

When uncertain, bias slightly easier rather than too hard.

## Locale-aware audio rules (mandatory)

1. Always use locale(s) compatible with `target_lang`.
2. Never reuse locale from an unrelated language.
3. Validate generated audio before send (`exists`, non-empty; recommended >2KB).
4. If synthesis fails, fallback within the same language family.
5. Never send known-empty audio files.

## Language-specific rules loading (mandatory)

Keep `SKILL.md` language-agnostic.

When processing language-specific behavior (accent selection, dialect handling, locale fallback), read:
- `references/language-rules.md`

Load only the section that matches the active `target_lang`.
Do not load unrelated language sections.

## Content variety rules (mandatory)

Do not generate the same style every day. Rotate both **format** and **topic** while preserving `target_level`.

### Format rotation examples

Use a varied mix across runs, such as:
- Authentic conversation / dialogue
- Short article / explainer
- Interview Q&A
- Personal story / diary entry
- News brief / current events summary
- Opinion + counterpoint
- Practical guide (how-to)

### Topic rotation examples

Rotate across broad domains, such as:
- Daily life / relationships
- Work / study / productivity
- Culture / history / society
- Technology / internet trends
- Health / habits / psychology
- Travel / food / city life
- Economy / environment / public policy

Avoid repeating nearly identical format-topic pairs on consecutive days unless the user asks.

## Delivery workflow

1. Generate pack text content.
2. Write report files in workspace reports folder:
   - `langpack-<lang>-YYYY-MM-DD.txt`
   - `langpack-<lang>-latest.txt`
3. Generate passage audio using locale-aware TTS.
4. Send text message first using this **chat-facing content contract**:
   - Include only: (a) target-language text, (b) plain English translation, (c) optional vocab list.
   - Exclude internal metadata/status from chat text (`WROTE_FILES`, `SENT_TO_TELEGRAM`, `AUDIO_SENT_TO_TELEGRAM`, `LOCALE_USED`, `LEVEL_USED`, etc.).
   - Exclude pedagogy/meta labels like `A1 focus` in chat text.
5. Send audio second.
   - If media-path restrictions block file send, use attachment `buffer` fallback.
6. Return explicit status block (internal agent reply, not user-facing pack text).

## Required status output

Always return these fields:

- `WROTE_FILES:`
- `SENT_TO_TELEGRAM:` (or channel equivalent)
- `AUDIO_SENT_TO_TELEGRAM:` (or channel equivalent)
- `LOCALE_USED:`
- `LEVEL_USED:`
- `FORMAT_USED:`
- `TOPIC_USED:`
- `AUDIO_VARIANT_USED:` (e.g., `primary-locale` | `fallback-locale`)

If audio fails, return `AUDIO_FAILED:` with exact reason.

## Reliability policy

- Validate TTS result is non-empty before send.
- For robust delivery, enforce local validation gates (`exists`, non-empty size; ideally >2KB).
- If primary TTS fails/empty, use fallback locale/provider path and retry send.
- Keep text delivery independent from audio delivery (audio failure must not block text).
- Never send a known-empty audio file to Telegram.

## Notes

- Skill is language-agnostic and should work for RU/ES/DE/FR/KO/etc.
- Keep output concise and operational.
