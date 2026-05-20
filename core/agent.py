# core/agent.py
# ==============
# The Agent class. Each agent:
#   1. Reads its persona from roles.yaml (via config.py)
#   2. Retrieves similar comments from its corpus (RAG via retriever.py)
#   3. Calls the LLM with its system prompt + retrieved context + stimulus
#
# Students: you don't need to modify this file.
# Your work is in assets/roles/roles.yaml — that's where you define the persona.
from pathlib import Path
import argparse
import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
 
from core.retriever import Retriever
 
 
 # exemplu  python -m core.agent --agent anti_sistem --text "CCR a decis anularea alegerilor după suspiciuni privind influențe externe." --provider gemini --k 5
load_dotenv()
 
MODELS = {
    "gemini": {
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        "api_key": os.getenv("GEMINI_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "deepseek": {
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com/v1",
    },
}
 
 
def load_role(agent_slug, roles_path="assets/roles/roles.yaml"):
    path = Path(roles_path)
 
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
 
    roles = data["agents"] if "agents" in data else data
 
    if agent_slug not in roles:
        raise ValueError(f"Agent not found: {agent_slug}")
 
    return roles[agent_slug]
 
 
def make_llm(provider="gemini", temperature=0.3):
    config = MODELS[provider]
 
    if not config["api_key"]:
        raise ValueError(f"Missing API key for provider: {provider}")
 
    return ChatOpenAI(
        model=config["model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
        temperature=temperature,
    )
 
 
def build_prompt(stimulus, rag_text):
    return f"""
[STIMULUS]
{stimulus}
 
[COMENTARII SIMILARE]
{rag_text}
""".strip()
 
 
def generate_agent_response(
    agent_slug,
    stimulus,
    provider="gemini",
    k=5,
    temperature=0.3,
    roles_path="assets/roles/roles.yaml",
):
    role = load_role(agent_slug, roles_path)
    retriever = Retriever(agent_slug)
 
    chunks = retriever.search(stimulus, k=k)
    rag_text = retriever.format_for_prompt(chunks)
 
    prompt = build_prompt(stimulus, rag_text)
 
    llm = make_llm(provider, temperature)
 
    messages = [
        SystemMessage(content=role["system"]),
        HumanMessage(content=prompt),
    ]
 
    response = llm.invoke(messages)
 
    return {
        "agent_slug": agent_slug,
        "agent_name": role.get("name", agent_slug),
        "stimulus": stimulus,
        "response": response.content.strip(),
        "rag_chunks": chunks,
        "rag_text": rag_text,
        "prompt": prompt,
        "provider": provider,
        "model": MODELS[provider]["model"],
        "temperature": temperature,
        "k": k,
    }
 
 
def main():
    parser = argparse.ArgumentParser()
 
    parser.add_argument("--agent", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--provider", default="gemini", choices=["gemini", "deepseek"])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--roles", default="assets/roles/roles.yaml")
 
    args = parser.parse_args()
 
    result = generate_agent_response(
        agent_slug=args.agent,
        stimulus=args.text,
        provider=args.provider,
        k=args.k,
        temperature=args.temperature,
        roles_path=args.roles,
    )
 
    print("\n=== AGENT ===")
    print(result["agent_name"])
 
    print("\n=== STIMULUS ===")
    print(result["stimulus"])
 
    print("\n=== CONTEXT RECUPERAT ===")
    print(result["rag_text"])
 
    print("\n=== RĂSPUNS ===")
    print(result["response"])
 
 
if __name__ == "__main__":
    main()