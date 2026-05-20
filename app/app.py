"""
EchoChamber Studio — app.py
===========================
A simulation of discursive bubbles using Romanian political comments.
Each "agent" responds from the perspective of its own political community.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & SETUP
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import json
import html
from pathlib import Path
import gradio as gr
import yaml
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, APIError, AuthenticationError
 
# Allow app/app.py to import from core/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
 
# Team configuration
from core.config import (
    PROVIDER_PRINCIPAL,
    MODEL_PRINCIPAL,
    PROVIDER_FALLBACK,
    MODEL_FALLBACK,
    TEMPERATURE,
)

from core.agent import generate_agent_response
from core.graph import run_thread

# ==================================================
# 2. PROVIDERS AND API KEYS
# ==================================================
 
load_dotenv(PROJECT_ROOT / ".env")
 
BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter": "https://openrouter.ai/api/v1"
}
 
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY")
}
 
def make_client(provider):
    return OpenAI(
        api_key=API_KEYS[provider],
        base_url=BASE_URLS[provider]
    )
 
# ==================================================
# 3. MODEL CALL
# ==================================================
 
def ask(provider, model, prompt, system=None, temperature=0.7, json_schema=None):
    client = make_client(provider)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
 
    extra_args = {}
    if json_schema:
        extra_args["response_format"] = {
            "type": "json_schema",
            "json_schema": json_schema
        }
 
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **extra_args
        )
        text = response.choices[0].message.content.strip()
        if json_schema:
            return json.loads(text)
        return text
    except RateLimitError:
        return f"[Eroare: quota/rate limit pentru modelul {model}.]"
    except AuthenticationError:
        return "[Eroare: API key invalida sau lipsa. Verifica .env.]"
    except APIError as e:
        return f"[Eroare API: {e}]"
    except Exception as e:
        return f"[Eroare: {type(e).__name__} — {e}]"
 
# ==================================================
# 4. APP LOGIC
# ==================================================
 
def chat(prompt):
    if not prompt.strip():
        return "Scrie un prompt mai intai."
    answer = ask(
        provider=PROVIDER_PRINCIPAL,
        model=MODEL_PRINCIPAL,
        prompt=prompt,
        temperature=TEMPERATURE
    )
    if isinstance(answer, str) and answer.startswith("[Eroare"):
        answer = ask(
            provider=PROVIDER_FALLBACK,
            model=MODEL_FALLBACK,
            prompt=prompt,
            temperature=TEMPERATURE
        )
    return answer

# REZUMAT INTELIGENT (folosit si la Chat si la Articole)
def genereaza_rezumat(text):
    if not text or not text.strip() or text.startswith("[Eroare"):
        return "Nu exista un text valid pentru a fi rezumat."
    
    system_prompt = "Esti un asistent inteligent. Sarcina ta este sa rezumi textul primit intr-o singura propozitie scurta, pastrand ideea principala."
    user_prompt = f"Rezuma acest text:\n\n{text}"
    
    rezumat = ask(
        provider=PROVIDER_PRINCIPAL,
        model=MODEL_PRINCIPAL,
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3
    )
    
    return f"📌 Rezumat: {rezumat}"

# FUNCTIE NOUA: Extragerea textului dintr-un URL
def extrage_text_din_link(url):
    if not url or not url.startswith("http"):
        return "Te rog sa introduci un URL valid care incepe cu http:// sau https://"
    
    try:
        # Mascam request-ul ca si cum ar veni de pe un browser real pentru a nu fi blocati de site
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extragem cu prioritate paragrafele (pentru a evita meniurile site-ului)
        paragrafe = soup.find_all('p')
        text_extras = "\n\n".join([p.get_text(strip=True) for p in paragrafe if p.get_text(strip=True)])
        
        # Daca nu gaseste paragrafe, facem un fallback pe tot textul
        if len(text_extras) < 100:
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            text_extras = soup.get_text(separator=' ', strip=True)
            
        if not text_extras.strip():
            return "Nu s-a putut extrage continut text din acest link."
            
        # Limitam textul la primele 15.000 caractere pentru a nu depasi limita modelului la rezumat
        return text_extras[:15000]
        
    except requests.exceptions.RequestException as e:
        return f"[Eroare de retea la accesarea linkului: Verifica daca adresa e scrisa corect si publica]\nDetalii: {e}"
    except Exception as e:
        return f"[Eroare la procesarea paginii: {e}]"

def load_agent_choices():
    roles_path = PROJECT_ROOT / "assets" / "roles" / "roles.yaml"
    if not roles_path.exists():
        return []
    with open(roles_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    roles = data["agents"] if "agents" in data else data
    return list(roles.keys())

def rag_agent_response(agent_slug, stimulus, provider, k):
    if not agent_slug:
        return "Nu exista agenti in assets/roles/roles.yaml.", ""
    if not stimulus.strip():
        return "Scrie un text politic pentru agent.", ""
    try:
        result = generate_agent_response(
            agent_slug=agent_slug,
            stimulus=stimulus,
            provider=provider,
            k=int(k),
            temperature=0.3,
            roles_path=str(PROJECT_ROOT / "assets" / "roles" / "roles.yaml"), 
        )
        return result["response"], result["rag_text"]
    except Exception as e:
        return f"[Eroare Agent RAG: {type(e).__name__} — {e}]", ""

def render_thread_html(messages):
    cards = []
    for msg in messages:
        agent = html.escape(str(msg.get("agent", "")))
        handle = html.escape(str(msg.get("handle", msg.get("slug", ""))))
        text = html.escape(str(msg.get("text", "")))
        turn = msg.get("turn", "")

        cards.append(
            f"""
        <div style='border-left:3px solid #e05a35; padding:.7rem 1rem; margin:.3rem 0; background:#16161a; border-radius: 4px;'>
            <div style='font-size:.75rem; color:#e05a35; text-transform:uppercase; font-weight: bold;'>{agent}</div>
            <div style='font-size:.7rem; color:#888'>{handle} · #{turn}</div>
            <p style='color:#c0bcb6; margin-top: 5px;'>{text}</p>
        </div>
        """
        )
    return "\n".join(cards)

def run_multi_agent_thread(
    stimulus, provider, total_turns, use_anti_sistem, use_anti_suveranist, 
    use_conspirationist, use_personalist_salvator, use_pro_european
):
    active_slugs = []
    if use_anti_sistem: active_slugs.append("anti_sistem")
    if use_anti_suveranist: active_slugs.append("anti_suveranist")
    if use_conspirationist: active_slugs.append("conspirationist")
    if use_personalist_salvator: active_slugs.append("personalist_salvator")
    if use_pro_european: active_slugs.append("pro_european")

    if not stimulus.strip(): return "Scrie un text politic mai intai."
    if not active_slugs: return "Selecteaza cel putin un agent."

    try:
        messages = run_thread(
            stimulus=stimulus,
            active_slugs=active_slugs,
            total_turns=int(total_turns),
            provider=provider,
            k=3,
        )
        return render_thread_html(messages)
    except Exception as e:
        return f"[Eroare Multi-agent Thread: {type(e).__name__} — {e}]"


# ==================================================
# 6. GRADIO UI - REDESIGN PRO
# ==================================================
 
toggle_theme_js = """
(btn_text) => {
    const body = document.querySelector('body');
    body.classList.toggle('dark');
    if (body.classList.contains('dark')) { return "☀️"; } 
    else { return "🌙"; }
}
"""

css_personalizat = """
#buton_tema {
    background: transparent !important; border: none !important; box-shadow: none !important; 
    font-size: 35px !important; min-width: auto !important; padding: 0 !important; cursor: pointer;
}
#buton_tema:hover { transform: scale(1.1); background: transparent !important; }
"""

agent_choices = load_agent_choices()

with gr.Blocks(title="EchoChamber Studio", theme=gr.themes.Soft(primary_hue="indigo"), css=css_personalizat) as demo:
    # --- HEADER ---
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown("# 🎙️ EchoChamber Studio")
            gr.Markdown("Simulare de bule discursive folosind comentarii politice si agenti LLM/RAG.")
        with gr.Column(scale=1, min_width=50):
            theme_btn = gr.Button("🌙", elem_id="buton_tema")
            
    theme_btn.click(None, inputs=[theme_btn], outputs=[theme_btn], js=toggle_theme_js)

    with gr.Tabs():
        # --- TAB 1: Chat simplu ---
        with gr.Tab("💬 Chat Simplu"):
            with gr.Row():
                with gr.Column(scale=1):
                    prompt_box = gr.Textbox(label="Prompt", value="Explica in 2 propozitii ce este un LLM.", lines=5)
                    chat_button = gr.Button("Trimite Prompt", variant="primary")
                with gr.Column(scale=2):
                    chat_output = gr.Textbox(label="Raspuns Principal", lines=5)
                    rezumat_button = gr.Button("✨ Genereaza Rezumatul Raspunsului", variant="secondary")
                    rezumat_output = gr.Textbox(label="Rezumat Inteligent", lines=2)
            
            chat_button.click(fn=chat, inputs=prompt_box, outputs=chat_output)
            rezumat_button.click(fn=genereaza_rezumat, inputs=chat_output, outputs=rezumat_output)

        # --- TAB NOU: Analiza Articol (Web Scraper + LLM) ---
        with gr.Tab("📰 Analiza Articol"):
            with gr.Row():
                with gr.Column(scale=1):
                    url_input = gr.Textbox(label="Link catre Articol", placeholder="https://www.g4media.ro/...", lines=2)
                    extrage_button = gr.Button("⬇️ Extrage Textul Articolului", variant="primary")
                    rezuma_articol_button = gr.Button("✨ Genereaza Rezumat Articol", variant="secondary")
                
                with gr.Column(scale=2):
                    articol_output = gr.Textbox(label="Textul Extras", lines=8)
                    rezumat_articol_output = gr.Textbox(label="Rezumat Articol", lines=3)
            
            extrage_button.click(fn=extrage_text_din_link, inputs=url_input, outputs=articol_output)
            # Conectam textul extras la aceeasi functie de generare rezumat pe care o foloseste Chat-ul!
            rezuma_articol_button.click(fn=genereaza_rezumat, inputs=articol_output, outputs=rezumat_articol_output)

        # --- TAB 3: Agent RAG ---
        with gr.Tab("🤖 Agent RAG"):
            with gr.Row():
                with gr.Column(scale=1):
                    agent_dropdown = gr.Dropdown(choices=agent_choices, value=agent_choices[0] if agent_choices else None, label="Alege Agentul")
                    with gr.Row():
                        provider_dropdown = gr.Dropdown(choices=["gemini", "deepseek"], value="gemini", label="Provider")
                        k_slider = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Documente extrase (k)")
                    stimulus_box = gr.Textbox(label="Text politic nou", value="CCR a decis anularea alegerilor dupa suspiciuni privind influente externe.", lines=3)
                    agent_button = gr.Button("Genereaza raspuns RAG", variant="primary")
                
                with gr.Column(scale=2):
                    agent_response_box = gr.Textbox(label="Raspuns agent", lines=7)
                    with gr.Accordion("🔍 Vezi Contextul Recuperat (RAG)", open=False):
                        context_box = gr.Textbox(show_label=False, lines=6)
            
            agent_button.click(fn=rag_agent_response, inputs=[agent_dropdown, stimulus_box, provider_dropdown, k_slider], outputs=[agent_response_box, context_box])

        # --- TAB 4: Multi-agent thread ---
        with gr.Tab("🕸️ Multi-Agent Thread"):
            with gr.Row():
                with gr.Column(scale=1):
                    thread_stimulus = gr.Textbox(label="Text politic initial", value="CCR a decis anularea alegerilor dupa suspiciuni privind influente externe.", lines=3)
                    with gr.Row():
                        thread_provider = gr.Dropdown(choices=["gemini", "deepseek"], value="gemini", label="Provider")
                        thread_turns = gr.Slider(minimum=2, maximum=8, value=4, step=1, label="Numar interventii")
                    
                    with gr.Group():
                        gr.Markdown("### ⚙️ Agenti Participanti")
                        use_anti_sistem = gr.Checkbox(value=True, label="Anti-sistem")
                        use_anti_suveranist = gr.Checkbox(value=True, label="Anti-suveranist")
                        use_conspirationist = gr.Checkbox(value=True, label="Conspirationist")
                        use_personalist_salvator = gr.Checkbox(value=True, label="Personalist Salvator")
                        use_pro_european = gr.Checkbox(value=True, label="Pro-european")
                    
                    thread_button = gr.Button("🔥 Porneste Dezbaterea", variant="primary")
                
                with gr.Column(scale=2):
                    thread_output = gr.HTML(label="Thread generat")

            thread_button.click(
                fn=run_multi_agent_thread,
                inputs=[thread_stimulus, thread_provider, thread_turns, use_anti_sistem, use_anti_suveranist, use_conspirationist, use_personalist_salvator, use_pro_european],
                outputs=thread_output,
            )
 
# ==================================================
# 7. LAUNCH
# ==================================================
 
if __name__ == "__main__":
    demo.launch()