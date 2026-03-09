---
name: langpack-delivery
description: Generate and deliver daily language packs (article + translation notes + passage audio) to messaging channels. Use for Russian/Spanish packs and generalized multilingual packs. Includes locale-aware TTS rules, reporting fields, and safe message delivery workflow.
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
- `target_chat` (default user chat)
- `date` (default today in user timezone)
- optional `locale_policy` (fixed locale or random from approved locale list)

## Locale-aware audio rules (mandatory)

1. Always use locale(s) compatible with `target_lang`.
2. Never reuse Russian locale for non-Russian content.
3. For language variants, choose locale from an approved set.
   - Example Spanish set: `es-ES`, `es-MX`, `es-US`
4. If randomization is enabled, report the chosen locale in output.

## Delivery workflow

1. Generate pack text content.
2. Write report files in workspace reports folder:
   - `langpack-<lang>-YYYY-MM-DD.txt`
   - `langpack-<lang>-latest.txt`
3. Generate passage audio using locale-aware TTS.
4. Send text message first.
5. Send audio second.
   - If media-path restrictions block file send, use attachment `buffer` fallback.
6. Return explicit status block.

## Required status output

Always return these fields:

- `WROTE_FILES:`
- `SENT_TO_TELEGRAM:` (or channel equivalent)
- `AUDIO_SENT_TO_TELEGRAM:` (or channel equivalent)
- `LOCALE_USED:`

If audio fails, return `AUDIO_FAILED:` with exact reason.

## Reliability policy

- Validate TTS result is non-empty before send.
- If primary TTS fails/empty, use fallback TTS path and retry send.
- Keep text delivery independent from audio delivery (audio failure must not block text).

## Notes

- Skill is language-agnostic and should work for RU/ES/DE/FR/KO/etc.
- Keep output concise and operational.
