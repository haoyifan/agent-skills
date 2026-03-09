# Levantine Arabic (`ar-levantine`) Rules

Use dialect text for displayed learning content, but keep audio reliability strict.

Audio policy:
1. Try Levantine-capable Arabic locale/voice first if available.
2. If dialect locale is unavailable or synthesis fails, fallback to **MSA Arabic** TTS.
3. Do **not** use transliteration fallback.
4. Validate audio file before send (exists, non-empty; recommended >2KB).
5. Never send empty audio files.

Output policy:
- Chat text remains in requested target style (Levantine for content section).
- Audio may be MSA fallback when dialect synthesis is unavailable.

## Proven fallback implementation (tested)

When built-in TTS returns empty Arabic files, use a standalone HTTP TTS fallback path:

1. Build Arabic `tts_text` (MSA fallback allowed).
2. Generate MP3 via Google Translate TTS endpoint (`client=tw-ob`, `tl=ar`, UTF-8 query text).
3. Save to local file and validate:
   - file exists
   - size > 0 (recommended >2KB)
4. For Telegram delivery, if local-path restrictions apply, copy output into an allowed media directory (e.g., `~/.openclaw/media/outbound/`) before sending.
5. If fallback generation fails validation, report audio failure and do not send broken media.

Notes:
- Keep this as reliability fallback for Arabic only.
- Keep no-transliteration rule: dialect first, then MSA text fallback only.
