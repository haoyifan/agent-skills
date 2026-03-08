#!/usr/bin/env python3
"""Preview and ingest vocab cards into Anki via AnkiConnect.

CSV columns:
- Front (required)
- Back (required)
- example (optional)
- sound_text (optional; defaults to Front)
- sound_lang (optional; defaults to --default-lang)
- pos (optional; e.g., noun/verb/adjective)
- back_image_url (optional; required when pos=noun)

Usage examples:
  # Preview only (no writes)
  python3 scripts/anki_vocab_pipeline.py --csv preview.csv --deck "Русский::TEST_HyperTTS_Sandbox"

  # Add cards + sync
  python3 scripts/anki_vocab_pipeline.py --csv preview.csv --deck "Русский::TEST_HyperTTS_Sandbox" --add --sync
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ANKI_URL = "http://127.0.0.1:8765"
UA = "Mozilla/5.0"
HYPERTTS_ADDON_ID = "111623432"
REQUIRED_FIELDS = {"Front", "Back", "example", "sound"}


@dataclass
class Row:
    front: str
    back: str
    example: str
    sound_text: str
    sound_lang: str
    pos: str
    back_image_url: str


def anki_invoke(action: str, params: dict[str, Any] | None = None) -> Any:
    payload = {"action": action, "version": 6, "params": params or {}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ANKI_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("error"):
        raise RuntimeError(body["error"])
    return body.get("result")


def fetch_google_tts_bytes(text: str, lang: str) -> bytes:
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl={lang}&client=tw-ob"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def load_rows(csv_path: Path, default_lang: str) -> list[Row]:
    rows: list[Row] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"Front", "Back"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

        for i, r in enumerate(reader, start=2):
            front = (r.get("Front") or "").strip()
            back = (r.get("Back") or "").strip()
            if not front or not back:
                raise ValueError(f"Row {i}: Front/Back cannot be empty")
            example = (r.get("example") or "").strip()
            sound_text = (r.get("sound_text") or front).strip()
            sound_lang = (r.get("sound_lang") or default_lang).strip()
            pos = (r.get("pos") or "").strip().lower()
            back_image_url = (r.get("back_image_url") or "").strip()

            if pos == "noun" and not back_image_url:
                raise ValueError(f"Row {i}: nouns must include back_image_url")

            rows.append(Row(front, back, example, sound_text, sound_lang, pos, back_image_url))
    return rows


def verify_hypertts_googletranslate(auto_fix: bool = False) -> dict[str, Any]:
    """Check HyperTTS is installed and GoogleTranslate free service is enabled.

    Returns a status object for reporting.
    """
    config_path = Path.home() / ".local" / "share" / "Anki2" / "addons21" / HYPERTTS_ADDON_ID / "config.json"
    if not config_path.exists():
        raise RuntimeError(
            f"HyperTTS not found at {config_path}. Install add-on {HYPERTTS_ADDON_ID} first."
        )

    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid HyperTTS config JSON: {e}") from e

    configuration = cfg.setdefault("configuration", {})
    enabled_map = configuration.setdefault("service_enabled", {})
    google_enabled = bool(enabled_map.get("GoogleTranslate"))

    if not google_enabled and auto_fix:
        enabled_map["GoogleTranslate"] = True
        service_cfg = configuration.setdefault("service_config", {})
        service_cfg.setdefault("GoogleTranslate", {}).setdefault("throttle_seconds", 0)
        config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        google_enabled = True

    if not google_enabled:
        raise RuntimeError(
            "HyperTTS is installed but GoogleTranslate service is not enabled in config.json (use --fix-hypertts-config)"
        )

    return {
        "configPath": str(config_path),
        "googleTranslateEnabled": google_enabled,
    }


def verify_model_fields(model: str) -> list[str]:
    fields = anki_invoke("modelFieldNames", {"modelName": model})
    missing = sorted(REQUIRED_FIELDS - set(fields))
    if missing:
        raise RuntimeError(
            f"Model '{model}' missing required fields: {missing}. Required: {sorted(REQUIRED_FIELDS)}"
        )
    return fields


GRAMMAR_LABEL_RE = re.compile(
    r"^(noun|verb|adjective|adverb|abbreviation|set phrase|sentence pattern|proper noun|plural noun phrase|noun phrase|verb phrase|past phrase|perfect infinitive phrase)([, ].*)?$",
    re.IGNORECASE,
)


def strip_grammar_labels(back_html: str) -> str:
    # Normalize and remove descriptor-only lines such as "noun, masculine".
    parts = [p.strip() for p in back_html.split("<br>")]
    kept = [p for p in parts if p and not GRAMMAR_LABEL_RE.match(p)]
    if not kept:
        return back_html.strip()
    return "<br>".join(kept)


def render_back(row: Row) -> str:
    clean_back = strip_grammar_labels(row.back)
    if row.pos == "noun" and row.back_image_url:
        return f"{clean_back}<br><br><img src=\"{row.back_image_url}\" alt=\"{row.front}\" width=\"260\">"
    return clean_back


def localize_back_images(back_html: str, key_prefix: str) -> str:
    pattern = re.compile(r'<img\s+[^>]*src="(https?://[^"]+)"[^>]*>', re.IGNORECASE)

    def repl(match: re.Match[str]) -> str:
        url = match.group(1)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
            if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                ext = ".jpg"
            fname = f"{key_prefix}_{int(time.time()*1000)}{ext}"
            anki_invoke("storeMediaFile", {"filename": fname, "data": base64.b64encode(data).decode("ascii")})
            return match.group(0).replace(url, fname)
        except Exception:
            return match.group(0)

    return pattern.sub(repl, back_html)


def note_payload(deck: str, model: str, row: Row, sound_filename: str | None, allow_duplicates: bool) -> dict[str, Any]:
    sound_value = f"[sound:{sound_filename}]" if sound_filename else ""
    return {
        "deckName": deck,
        "modelName": model,
        "fields": {
            "Front": row.front,
            "Back": render_back(row),
            "example": row.example,
            "sound": sound_value,
        },
        "options": {"allowDuplicate": allow_duplicates},
    }


def _preview_rows(rows: list[Row]) -> list[list[str]]:
    out = [["Front", "Back", "example", "sound_text", "sound_lang", "pos", "back_image_url"]]
    for r in rows:
        out.append([r.front, r.back, r.example, r.sound_text, r.sound_lang, r.pos, r.back_image_url])
    return out


def print_preview(rows: list[Row]) -> None:
    writer = csv.writer(sys.stdout)
    for row in _preview_rows(rows):
        writer.writerow(row)


def write_preview_csv(rows: list[Row], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in _preview_rows(rows):
            writer.writerow(row)


def dominant_lang(rows: list[Row], fallback: str) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r.sound_lang] = counts.get(r.sound_lang, 0) + 1
    if not counts:
        return fallback
    return max(counts.items(), key=lambda kv: kv[1])[0]


def propose_decks(existing_decks: list[str], lang_code: str) -> dict[str, Any]:
    lang_hints = {
        "ru": ["рус", "russian", "ru"],
        "es": ["españ", "spanish", "es"],
        "de": ["deutsch", "german", "de"],
        "ko": ["한국", "korean", "ko"],
        "fr": ["french", "français", "fr"],
        "pt": ["portugu", "pt"],
        "ar": ["عربي", "arabic", "ar"],
    }
    hints = lang_hints.get(lang_code, [lang_code])

    scored: list[tuple[int, str]] = []
    for d in existing_decks:
        dl = d.lower()
        score = 0
        for h in hints:
            if h in dl:
                score += 3
        if "test" in dl or "sandbox" in dl:
            score -= 1
        scored.append((score, d))

    scored.sort(key=lambda x: (-x[0], x[1]))
    top = [d for s, d in scored if s > 0][:5]

    if top:
        return {
            "language": lang_code,
            "recommendedDeck": top[0],
            "alternatives": top[1:3],
            "newDeckSuggested": None,
            "reason": "Matched existing deck names by language hints.",
        }

    suggested = f"{lang_code.upper()}" if len(lang_code) <= 3 else f"Language::{lang_code}"
    return {
        "language": lang_code,
        "recommendedDeck": None,
        "alternatives": [],
        "newDeckSuggested": suggested,
        "reason": "No strong existing deck match found.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Input CSV path")
    p.add_argument("--deck", help="Target deck name (optional in preview mode)")
    p.add_argument("--model", default="Basic and Reverse", help="Anki note type")
    p.add_argument("--default-lang", default="ru", help="Default TTS language (e.g. ru, es)")
    p.add_argument("--add", action="store_true", help="Actually add notes (default is preview-only)")
    p.add_argument("--sync", action="store_true", help="Run Anki sync after add")
    p.add_argument("--allow-duplicates", action="store_true", help="Allow duplicate notes")
    p.add_argument("--fix-hypertts-config", action="store_true", help="Auto-enable HyperTTS GoogleTranslate config if disabled")
    p.add_argument("--preview-out", help="Optional path to also write preview CSV file for user review")
    args = p.parse_args()

    rows = load_rows(Path(args.csv), args.default_lang)

    # Connectivity check
    version = anki_invoke("version")
    if not version:
        raise RuntimeError("AnkiConnect is not reachable")

    # HyperTTS + model preflight
    hypertts_status = verify_hypertts_googletranslate(auto_fix=args.fix_hypertts_config)
    model_fields = verify_model_fields(args.model)

    lang = dominant_lang(rows, args.default_lang)
    decks = anki_invoke("deckNames") or []
    deck_plan = propose_decks(decks, lang)

    selected_deck = args.deck or deck_plan.get("recommendedDeck") or deck_plan.get("newDeckSuggested")
    if args.add and not args.deck:
        raise RuntimeError("--deck is required when using --add. Approve a proposed deck first.")

    # Use explicit deck for duplicate checks in preview; avoid creating proposal decks implicitly.
    check_deck = args.deck if args.deck else (selected_deck if args.add else None)

    # Ensure deck exists only when needed for actual add/check path.
    if check_deck:
        anki_invoke("createDeck", {"deck": check_deck})

    # Duplicate check preview (only if we have an explicit check deck)
    can_add = [True] * len(rows)
    if check_deck:
        candidate_notes = [
            note_payload(check_deck, args.model, r, sound_filename=None, allow_duplicates=args.allow_duplicates)
            for r in rows
        ]
        can_add = anki_invoke("canAddNotes", {"notes": candidate_notes})

    print("# PREFLIGHT")
    print(json.dumps({
        "hypertts": hypertts_status,
        "model": args.model,
        "modelFields": model_fields,
        "defaultLang": args.default_lang,
        "detectedLanguage": lang,
        "deckProposal": deck_plan,
        "selectedDeck": selected_deck,
    }, ensure_ascii=False))

    print("\n# PREVIEW")
    print_preview(rows)
    if args.preview_out:
        preview_path = Path(args.preview_out)
        write_preview_csv(rows, preview_path)
        print("\n# PREVIEW_FILE")
        print(json.dumps({"path": str(preview_path.resolve())}, ensure_ascii=False))
    print("\n# CHECK")
    print(json.dumps({"total": len(rows), "addable": int(sum(1 for x in can_add if x)), "blocked": int(sum(1 for x in can_add if not x))}, ensure_ascii=False))

    if not args.add:
        return 0

    if not selected_deck:
        raise RuntimeError("No deck selected. Pass --deck after approving a proposed deck.")

    notes_to_add: list[dict[str, Any]] = []
    for i, row in enumerate(rows, start=1):
        if not args.allow_duplicates and not can_add[i - 1]:
            continue

        mp3 = fetch_google_tts_bytes(row.sound_text, row.sound_lang)
        fname = f"vocab_{int(time.time())}_{i}.mp3"
        anki_invoke(
            "storeMediaFile",
            {"filename": fname, "data": base64.b64encode(mp3).decode("ascii")},
        )
        note = note_payload(selected_deck, args.model, row, sound_filename=fname, allow_duplicates=args.allow_duplicates)
        note["fields"]["Back"] = localize_back_images(note["fields"]["Back"], f"img_{i}")
        notes_to_add.append(note)

    result = anki_invoke("addNotes", {"notes": notes_to_add}) if notes_to_add else []
    if args.sync:
        anki_invoke("sync")

    print("\n# RESULT")
    print(json.dumps({"deck": selected_deck, "requested": len(rows), "attempted": len(notes_to_add), "added": sum(1 for x in result if x), "ids": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
