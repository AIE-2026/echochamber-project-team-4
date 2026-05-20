# EchoChamber Studio

EchoChamber Studio is a prototype AI application that simulates how different discursive agents respond to the same political or social news article.

---

## Project overview

EchoChamber Studio explores how large language models can simulate different discursive perspectives when analyzing the same input text. The system allows users to input a news article or social text and observe how different agent “voices” interpret and respond to it.

The application can:
- load or use a political or social news article (via URL or text input);
- summarize the input content;
- generate a response from a single selected agent;
- compare responses across multiple agents;
- simulate a short multi-agent debate based on the same input.

The goal is to provide a controlled environment for studying variation in language, framing, and interpretation.

---

## Why this project matters

The project explores how AI agents can be used to study discursive framing, polarization, narrative variation, and the limits of automated interpretation in political communication.

It does not measure real public opinion, but instead simulates how different interpretive positions can shape responses to the same informational input.

---

## Project Structure

```
echochamber/
├── notebooks/              
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
│   └── app.py              # Gradio application 
└── reports/                # Final report and ethics checklist templates
```
## Main workflow

### Single agent mode

```text
news/text → selected agent role → retrieved similar comments → LLM → simulated response
```

### Multi-agent debate

```text
news/text → selected agents → conversation state → multi-agent thread
```

### Workflow explanation

- The input text is the central object of analysis.
- Retrieved comments provide contextual discourse, not factual validation.
- Agent roles define tone, perspective, and response constraints.

---

## Repository structure

```text
app/                 Gradio user interface
core/                backend logic for agents, retrieval and multi-agent debate
assets/roles/        YAML definitions for simulated agents
assets/vectorstores/ FAISS indexes used for retrieval
data/bubbles/        comment corpora grouped by agent/bubble
notebooks/           development notebooks and individual work
docs/                ethics, limitations and project documentation
outputs/             optional generated outputs
```

---

## How to run locally

### Windows PowerShell

```powershell
git pull
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m app.app
```

The application runs locally by default.

---

## Environment variables

Create a local `.env` file based on `.env.example`.

Do not commit `.env` or API keys.
API keys and sensitive data must never be committed.

Example configuration:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite

DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-chat

OPENROUTER_API_KEY=...
OPENROUTER_MODEL=...
```

---

## Application features

- **Chat** – interact directly with a selected model
- **Summary** – summarize input articles or text
- **Agent** – generate a response from a selected discursive agent
- **All agents** – compare multiple agent perspectives on the same input
- **Debate** – run a short multi-agent conversation

---

## Agents

Defined in `assets/roles/roles.yaml`:

- `personalist_salvator`
- `anti_sistem`
- `conspirationist`
- `pro_european`
- `anti_suveranist`

Each agent is defined by a role, voice, worldview and response rules. The agents are simulated discursive roles, not real people or real social groups.

---

## Technical components

```text
core/retriever.py    searches FAISS vectorstores for relevant comments
core/agent.py        combines role, context, and LLM response
core/graph.py        manages multi-agent conversation flow
app/app.py           Gradio interface for the application
```

---

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

- **Team name: TEAM 4**
- **Members and agents:**
  - Member 1 → Agent: Macovei Teodora → personalist-salvator
  - Member 2 → Agent: Iacob Toni → anti-sistem
  - Member 3 → Agent: Vitok Patrick → anti-suveranist
  - Member 4 → Agent: Ciutu Carmen → conspirationist
  - Member 5 → Agent: Somlea Monica → pro-european

## Ethics checklist

EchoChamber is a teaching and research prototype. Its agents are simulated discursive roles, they are not real people or any representatives of real social groups.

Generated outputs may contain bias, unsupported or false claims, and must be interpreted critically through pure human reasoning and review.

See docs\ethics_checklist.md for the complete ethics note and limitations.

## Known issues & Limitations

- Some news websites block article extraction.
- Agent responses can be repetitive or overly generic.
- Debate logic is simplified and not fully conversationally stable.
- Performance depends heavily on model provider and dataset quality.
- The application is currently a local-only prototype.

---

## License / usage note

This project is a research and educational prototype. Outputs should be reviewed by humans before interpretation or reuse.