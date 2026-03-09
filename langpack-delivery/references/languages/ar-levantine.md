# Levantine Arabic (`ar-levantine`) Rules

Use dialect text for displayed learning content, but keep audio reliability strict.

## Requirement

ElevenLabs is required as the primary Arabic TTS backend.

- Required key: `ELEVENLABS_API_KEY` (or equivalent configured key path)
- If key is missing, report configuration error explicitly and do not pretend audio was sent.

## Primary Arabic TTS policy (ElevenLabs)

1. Use ElevenLabs API (`/v1/text-to-speech/{voiceId}`) with multilingual model.
   - Recommended model: `eleven_multilingual_v2`
2. Try Levantine-friendly Arabic rendering first (dialectal `display_text` for user, synthesis text tuned for reliability).
3. If dialect synthesis quality/availability is poor, fallback to **MSA Arabic** synthesis text.
4. Do **not** use transliteration fallback.
5. Validate output audio before send:
   - file exists
   - non-empty (recommended >2KB)
6. Never send empty/broken audio files.

Output policy:
- Chat text remains in requested target style (Levantine for content section).
- Audio may be MSA fallback when dialect synthesis is unavailable.

## Secondary fallback (only if ElevenLabs is unavailable at runtime)

If ElevenLabs request fails due transient runtime issues (not permanent key/config error), use Google TTS HTTP fallback as emergency path:

1. Build Arabic `tts_text` (MSA fallback allowed).
2. Generate MP3 via Google Translate TTS endpoint (`client=tw-ob`, `tl=ar`, UTF-8 query text).
3. Save and validate (`exists`, non-empty; recommended >2KB).
4. For Telegram path restrictions, copy file into an allowed media directory (e.g., `~/.openclaw/media/outbound/`) before sending.
5. If fallback also fails validation, report audio failure and stop.
