# EchoChamber Studio

Simulation of discursive bubbles using political comments.
Each agent responds from the perspective of its own political community.

## Project Structure

```
echochamber/
├── notebooks/              # Weekly course notebooks (added during the semester)
├── collector/              # Scripts for collecting comments from YouTube / RSS
├── data/
│   ├── raw/                # Raw collected comments (CSV or JSONL)
│   ├── cleaned/            # Cleaned and standardized corpus
│   └── bubbles/            # One JSONL file per agent after annotation
├── assets/
│   └── roles/              # Agent role cards (roles.yaml) — written by students
├── scripts/
│   ├── clean_corpus.py     # Cleans and standardizes raw data
│   └── build_vectorstore.py # Builds FAISS vector index from data/bubbles/
├── core/                   # Core infrastructure — do not modify
│   ├── agent.py            # Agent class: reads roles.yaml + retrieves from corpus
│   ├── retriever.py        # Semantic search over FAISS index
│   ├── graph.py            # LangGraph agentic debate orchestration
│   └── metrics.py          # Dissimilarity, sentiment, and visualization
├── app/
│   └── app.py              # Gradio application (built incrementally during course)
└── reports/                # Final report and ethics checklist templates
```

## Setup

```bash
git clone <your-repo-url>
cd echochamber
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then add your API key
```

## Team

- **Team name:**
- **Topic / bubble theme:**
- **Members and agents:**
  - Member 1 → Agent:
  - Member 2 → Agent:
  - Member 3 → Agent:
  - Member 4 → Agent:
  - Member 5 → Agent:

## Ethics checklist

EchoChamber is a teaching and research prototype. Its agents are simulated discursive roles, they are not real people or any representatives of real social groups.

Generated outputs may contain bias, unsupported or false claims, and must be interpreted critically through pure human reasoning and review.

See docs\ethics_checklist.md for the complete ethics note and limitations.