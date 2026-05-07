# scripts/clean_youtube.py
"""
Curățare simplă pentru corpusul YouTube oferit de profesor.
Rulează din root-ul proiectului:
python scripts/clean_youtube.py --input data/raw/corpus_youtube_large_raw.jsonl --output data/cleaned/corpus_youtube_large_clean.jsonl
"""
# 1. Biblioteci
import json
import re
import argparse
from pathlib import Path
# 2. Argumente din terminal
parser = argparse.ArgumentParser()
parser.add_argument("--input", default="data/provided/corpus_youtube_large_raw.jsonl")
parser.add_argument("--output", default="data/cleaned/corpus_youtube_large_clean.jsonl")
parser.add_argument("--min-chars", type=int, default=60)
parser.add_argument("--min-alpha", type=float, default=0.5)
args = parser.parse_args()
# 3. Căi fișiere
input_file = Path(args.input)
output_file = Path(args.output)
output_file.parent.mkdir(parents=True, exist_ok=True)
# 4. Curățare text
def clean_text(text):
    text = re.sub(r"http\S+", "", text)      # elimină linkuri
    text = re.sub(r"\s+", " ", text)         # normalizează spațiile
    return text.strip()
# 5. Proporția de litere din text
def alpha_ratio(text):
    if len(text) == 0:
        return 0
    letters = sum(char.isalpha() for char in text)
    return letters / len(text)
# 6. Citire, curățare, filtrare, deduplicare
cleaned_comments = []
seen_texts = set()
raw_count = 0
with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        raw_count += 1
        comment = json.loads(line)
        raw_text = comment.get("text_raw", "")
        text = clean_text(raw_text)
        # eliminăm comentariile prea scurte
        if len(text) < args.min_chars:
            continue
        # eliminăm comentariile cu prea puține litere
        if alpha_ratio(text) < args.min_alpha:
            continue
        # eliminăm duplicatele după textul curățat
        text_key = text.lower()
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)
        # păstrăm textul original și adăugăm textul curățat
        comment["text"] = text
        comment["lang"] = "ro"
        cleaned_comments.append(comment)
# 7. Salvare JSONL
with output_file.open("w", encoding="utf-8") as f:
    for comment in cleaned_comments:
        f.write(json.dumps(comment, ensure_ascii=False) + "\n")
# 8. Raport final
print("Fișier brut:", input_file)
print("Fișier curățat:", output_file)
print("Comentarii brute:", raw_count)
print("Comentarii curate:", len(cleaned_comments))
print("Eliminate:", raw_count - len(cleaned_comments))