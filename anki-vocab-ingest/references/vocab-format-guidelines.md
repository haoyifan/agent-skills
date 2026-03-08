# Vocab formatting guidelines

Use these defaults unless user overrides.

## Field mapping
- `Front`: lemma/base form.
- `Back`: English meaning only. Do not append POS/grammar label lines (e.g., noun/verb/adjective notes).
- For nouns, append an image (`<img ...>`) using `back_image_url`.
- `example`: one concise target-language sentence.
- `sound`: `[sound:*.mp3]` generated from `sound_text`.

## Lemma normalization
- Verb: infinitive (unconjugated).
- Noun: singular nominative.
- Adjective: masculine singular.
- Multiword expression: canonical phrase (e.g., `крайний случай`).

## Extra grammar block in `Back`
Always separate meaning and extra block with one blank line.
Use one item per line.

### Verb
- Add conjugation lines in present/future:
  - я ...
  - ты ...
  - он/она ...
  - мы ...
  - вы ...
  - они ...

### Noun
- Add plural line.
- Include an image in `Back` along with translation.
- Relevance requirement: image should directly represent the noun meaning (object/person/place/concept) and avoid unrelated stock photos.
- Selection process: review candidate images and evaluate up to 20 options before choosing one.
- Use CSV `back_image_url` and render as HTML image in `Back`.

### Adjective
- Add feminine, neuter, plural lines.

## Rendering rule
If target note template collapses `\n` line breaks, use `<br>` and `<br><br>` in `Back`.

## Language support
- Russian TTS code: `ru`
- Spanish TTS code: `es`
- Allow per-row override using `sound_lang` column.
