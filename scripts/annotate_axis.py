"""
annotate_axis.py
----------------
Adnotare LLM pe schema didactică EchoChamber C4.

Folosește promptul separat:
    prompts/annotation_prompt.md

Input:
    JSONL cu comentarii curate.

Output:
    JSONL cu adnotări:
    id, text, source_channel, video_title,
    target, stance, tone,
    institutional, legitimare, epistemic, geopolitic, mobilizare,
    justification, confidence

Exemple:
    python scripts/annotate_axis.py ^
        --input data/cleaned/corpus_youtube_sample.jsonl ^
        --output data/annotated/corpus_axis_annotated.jsonl ^
        --provider gemini

    python scripts/annotate_axis.py ^
        --input data/cleaned/corpus_youtube_sample.jsonl ^
        --output data/annotated/corpus_axis_annotated.jsonl ^
        --provider deepseek ^
        --limit 100

Resume:
    Dacă outputul există, sare peste ID-urile deja adnotate.
    Pentru rerun complet, folosește --overwrite.
"""

import os
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm


# ── CONFIG ────────────────────────────────────────────────────────────────────

DEFAULT_PROMPT = "prompts/annotation_prompt.md"

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-2.5-flash-lite"

MAX_RETRIES = 3
SLEEP_BETWEEN_CALLS = 0.5


TARGET_VOCAB = {
    "georgescu", "simion", "aur", "sosoaca",
    "psd", "pnl", "usr", "nicusor_dan", "bolojan", "other_mainstream_actor",
    "guvern", "presedintie", "parlament", "ccr", "alegeri", "justitie", "other_state_institution",
    "ue", "nato", "bruxelles", "other_external_actor",
    "recorder", "g4media", "digi24", "presa_mainstream", "presa_investigativa", "other_media",
    "none",
}

STANCE_VOCAB = {"pro", "anti", "neutru", "ambiguu", "none"}
TONE_VOCAB = {"acuzator", "ironic", "mobilizator", "defensiv", "afectiv", "neutru"}


# ── PATH / ENV ────────────────────────────────────────────────────────────────

def find_root() -> Path:
    root = Path.cwd()
    while not (root / ".env").exists() and root.parent != root:
        root = root.parent
    return root


def load_env() -> Path:
    root = find_root()
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
    return root


def make_client(provider: str) -> tuple[OpenAI, str]:
    provider = provider.lower().strip()

    if provider == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("Lipsește DEEPSEEK_API_KEY în .env")
        return OpenAI(api_key=key, base_url=DEEPSEEK_BASE_URL), DEEPSEEK_MODEL

    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("Lipsește GEMINI_API_KEY în .env")
        return OpenAI(api_key=key, base_url=GEMINI_BASE_URL), GEMINI_MODEL

    raise ValueError("provider trebuie să fie: deepseek sau gemini")


# ── IO ────────────────────────────────────────────────────────────────────────

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_done_ids(path: Path) -> Set[str]:
    done = set()
    if not path.exists():
        return done

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rid = str(row.get("id", "")).strip()
                if rid:
                    done.add(rid)
            except json.JSONDecodeError:
                continue
    return done


# ── PROMPT / JSON ─────────────────────────────────────────────────────────────

def format_comment(row: Dict[str, Any]) -> str:
    return f"""
CANAL:
{row.get("source_channel", "")}

TITLU VIDEO:
{row.get("video_title", "")}

COMENTARIU:
<<< {row.get("text", "")} >>>
""".strip()


def extract_json(text: str) -> Dict[str, Any]:
    clean = text.replace("```json", "").replace("```", "").strip()

    start = clean.find("{")
    end = clean.rfind("}") + 1

    if start == -1 or end <= start:
        raise ValueError("Nu am găsit JSON valid în răspuns.")

    return json.loads(clean[start:end])


def clamp_int(value: Any, allowed: set[int], default: int = 0) -> int:
    try:
        value = int(value)
    except Exception:
        return default
    return value if value in allowed else default


def clamp_float(value: Any, lo: float = 0.0, hi: float = 1.0, default: float = 0.5) -> float:
    try:
        value = float(value)
    except Exception:
        return default
    return max(lo, min(hi, value))


def validate_annotation(raw: Dict[str, Any]) -> Dict[str, Any]:
    target = str(raw.get("target", "none")).strip().lower()
    stance = str(raw.get("stance", "none")).strip().lower()
    tone = str(raw.get("tone", "neutru")).strip().lower()

    if target not in TARGET_VOCAB:
        target = "none"

    if stance not in STANCE_VOCAB:
        stance = "none"

    if target == "none":
        stance = "none"

    if tone not in TONE_VOCAB:
        tone = "neutru"

    return {
        "target": target,
        "stance": stance,
        "tone": tone,
        "institutional": clamp_int(raw.get("institutional", 0), {-2, -1, 0, 1, 2}),
        "legitimare": clamp_int(raw.get("legitimare", 0), {-2, -1, 0, 1, 2}),
        "epistemic": clamp_int(raw.get("epistemic", 0), {-2, -1, 0, 1, 2}),
        "geopolitic": clamp_int(raw.get("geopolitic", 0), {-2, -1, 0, 1, 2}),
        "mobilizare": clamp_int(raw.get("mobilizare", 0), {0, 1, 2}),
        "justification": str(raw.get("justification", "")).strip(),
        "confidence": clamp_float(raw.get("confidence", 0.5)),
    }


# ── API ───────────────────────────────────────────────────────────────────────

def annotate_one(
    client: OpenAI,
    model: str,
    system_prompt: str,
    row: Dict[str, Any],
    max_tokens: int = 700,
) -> Dict[str, Any]:
    user_prompt = format_comment(row)

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            raw_text = response.choices[0].message.content
            raw_json = extract_json(raw_text)
            annotation = validate_annotation(raw_json)

            return {
                "id": row.get("id", ""),
                "source_channel": row.get("source_channel", ""),
                "channel_family": row.get("channel_family", ""),
                "video_title": row.get("video_title", ""),
                "text": row.get("text", ""),
                **annotation,
                "fallback": False,
            }

        except Exception as e:
            last_error = e
            time.sleep(1.5 * attempt)

    return {
        "id": row.get("id", ""),
        "source_channel": row.get("source_channel", ""),
        "channel_family": row.get("channel_family", ""),
        "video_title": row.get("video_title", ""),
        "text": row.get("text", ""),
        "target": "none",
        "stance": "none",
        "tone": "neutru",
        "institutional": 0,
        "legitimare": 0,
        "epistemic": 0,
        "geopolitic": 0,
        "mobilizare": 0,
        "justification": f"Fallback: {last_error}",
        "confidence": 0.0,
        "fallback": True,
    }


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="data/cleaned/corpus_youtube_sample.jsonl",
        help="Fișier JSONL cu comentarii curate.",
    )

    parser.add_argument(
        "--output",
        default="data/annotated/corpus_axis_annotated.jsonl",
        help="Fișier JSONL de output.",
    )

    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Fișierul Markdown cu promptul de adnotare.",
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "deepseek"],
        default="gemini",
        help="Provider LLM.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Număr maxim de comentarii de adnotat.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Șterge outputul existent și rulează de la zero.",
    )

    args = parser.parse_args()

    root = load_env()
    print("Root:", root)

    input_path = root / args.input
    output_path = root / args.output
    prompt_path = root / args.prompt

    if not input_path.exists():
        raise FileNotFoundError(f"Nu există input: {input_path}")

    if not prompt_path.exists():
        raise FileNotFoundError(f"Nu există prompt: {prompt_path}")

    if args.overwrite and output_path.exists():
        output_path.unlink()
        print("Overwrite: outputul existent a fost șters.")

    system_prompt = prompt_path.read_text(encoding="utf-8")
    client, model = make_client(args.provider)

    rows = read_jsonl(input_path)

    if args.limit is not None:
        rows = rows[: args.limit]

    done_ids = read_done_ids(output_path)
    pending = [
        row for row in rows
        if str(row.get("id", "")).strip() not in done_ids
    ]

    print("Provider:", args.provider)
    print("Model:", model)
    print("Input:", input_path)
    print("Prompt:", prompt_path)
    print("Output:", output_path)
    print("Total rows:", len(rows))
    print("Already done:", len(done_ids))
    print("Pending:", len(pending))

    if not pending:
        print("Totul este deja adnotat.")
        return

    for row in tqdm(pending, desc="Annotating", unit="comment"):
        annotated = annotate_one(
            client=client,
            model=model,
            system_prompt=system_prompt,
            row=row,
        )
        append_jsonl(output_path, annotated)
        time.sleep(SLEEP_BETWEEN_CALLS)

    print("Gata:", output_path)


if __name__ == "__main__":
    main()