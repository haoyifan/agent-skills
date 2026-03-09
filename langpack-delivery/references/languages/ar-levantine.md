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
