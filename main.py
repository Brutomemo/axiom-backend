import os
import resend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from openai import OpenAI
from anthropic import Anthropic
from supabase import create_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
resend.api_key = os.getenv("RESEND_API_KEY")

SYSTEM_PROMPTS = {
    "strategic-intelligence": (
        "Você é o assistente comercial da AXIOM Strategic Intelligence. "
        "A empresa oferece análise de dados, automação com IA e desenvolvimento de aplicações web. "
        "Seja objetivo, cordial e direcione o usuário para o formulário de diagnóstico quando fizer sentido."
    ),
    "human-performance": (
        "Você é o assistente da AXIOM Human Performance. "
        "A empresa oferece psicologia organizacional, treinamentos e saúde no trabalho, com OKRs e people analytics. "
        "Seja acolhedor, objetivo e direcione o usuário para o formulário de contato quando fizer sentido."
    ),
}

COMPLEX_KEYWORDS = [
    "análise detalhada", "estratégia completa", "passo a passo",
    "diagnóstico", "relatório", "compare", "comparação",
    "explique em detalhes", "plano completo", "processo completo",
]

EMAIL_TEMPLATES = {
    "strategic-intelligence": {
        "subject": "AXIOM — Recebemos sua solicitação de diagnóstico",
        "body": lambda nome, areas: f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0f; color: #e2e8f0; padding: 40px; border-radius: 12px;">
  <div style="text-align: center; margin-bottom: 32px;">
    <h1 style="color: #06b6d4; font-size: 28px; margin: 0;">AXIOM</h1>
    <p style="color: #64748b; margin: 4px 0 0;">Strategic Intelligence</p>
  </div>
  <h2 style="color: #f1f5f9; font-size: 20px;">Olá, {nome}!</h2>
  <p style="color: #94a3b8; line-height: 1.6;">
    Recebemos sua solicitação de diagnóstico estratégico e ficamos felizes com seu interesse.
  </p>
  <p style="color: #94a3b8; line-height: 1.6;">
    Você demonstrou interesse em:
  </p>
  <div style="background: #1e293b; border-left: 3px solid #06b6d4; padding: 16px; border-radius: 4px; margin: 16px 0;">
    <strong style="color: #06b6d4;">{areas}</strong>
  </div>
  <p style="color: #94a3b8; line-height: 1.6;">
    Nossa equipe analisará suas informações e entrará em contato em breve para agendar uma conversa.
  </p>
  <div style="text-align: center; margin: 32px 0;">
    <a href="https://axiom-dusky-delta.vercel.app" 
       style="background: #06b6d4; color: #000; padding: 12px 32px; border-radius: 6px; text-decoration: none; font-weight: bold;">
      Conhecer mais sobre a AXIOM
    </a>
  </div>
  <p style="color: #475569; font-size: 13px; text-align: center; margin-top: 32px;">
    AXIOM Strategic Intelligence · axiomstrategic.com.br
  </p>
</div>
""",
    },
    "human-performance": {
        "subject": "AXIOM Human Performance — Recebemos sua solicitação",
        "body": lambda nome, areas: f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0f; color: #e2e8f0; padding: 40px; border-radius: 12px;">
  <div style="text-align: center; margin-bottom: 32px;">
    <h1 style="color: #06b6d4; font-size: 28px; margin: 0;">AXIOM</h1>
    <p style="color: #64748b; margin: 4px 0 0;">Human Performance</p>
  </div>
  <h2 style="color: #f1f5f9; font-size: 20px;">Olá, {nome}!</h2>
  <p style="color: #94a3b8; line-height: 1.6;">
    Recebemos sua solicitação e ficamos felizes em saber que você busca evoluir a performance humana na sua organização.
  </p>
  <p style="color: #94a3b8; line-height: 1.6;">
    Você demonstrou interesse em:
  </p>
  <div style="background: #1e293b; border-left: 3px solid #06b6d4; padding: 16px; border-radius: 4px; margin: 16px 0;">
    <strong style="color: #06b6d4;">{areas}</strong>
  </div>
  <p style="color: #94a3b8; line-height: 1.6;">
    Nossa equipe de especialistas em psicologia organizacional e performance humana entrará em contato em breve.
  </p>
  <div style="text-align: center; margin: 32px 0;">
    <a href="https://axiom-dusky-delta.vercel.app/pages/human-performance.html" 
       style="background: #06b6d4; color: #000; padding: 12px 32px; border-radius: 6px; text-decoration: none; font-weight: bold;">
      Conhecer Human Performance
    </a>
  </div>
  <p style="color: #475569; font-size: 13px; text-align: center; margin-top: 32px;">
    AXIOM Human Performance · axiomstrategic.com.br
  </p>
</div>
""",
    },
}


def send_welcome_email(nome: str, email: str, areas: str, origem: str):
    template = EMAIL_TEMPLATES.get(origem, EMAIL_TEMPLATES["strategic-intelligence"])
    try:
        resend.Emails.send({
            "from": "AXIOM <onboarding@resend.dev>",
            "to": [email],
            "subject": template["subject"],
            "html": template["body"](nome, areas),
        })
        print(f"[EMAIL] Enviado para {email}")
    except Exception as e:
        print(f"[ERRO EMAIL]: {e}")


class LeadRequest(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    empresa: str | None = None
    mensagem: str | None = None
    interesse: list[str] | None = None
    servicos: list[str] | None = None
    origem: str = "strategic-intelligence"
    session_id: str | None = None


@app.post("/api/lead")
def lead(payload: LeadRequest):
    areas = payload.interesse or payload.servicos or []
    areas_str = ", ".join(areas) if areas else None
    try:
        result = supabase.table("leads").insert({
            "nome": payload.nome,
            "email": payload.email,
            "telefone": payload.telefone,
            "empresa": payload.empresa,
            "mensagem": payload.mensagem,
            "area_interesse": areas_str,
            "origem": payload.origem,
            "status": "novo",
        }).execute()
        lead_id = result.data[0]["id"] if result.data else None

        if lead_id and payload.session_id:
            try:
                supabase.table("chat_history") \
                    .update({"lead_id": lead_id}) \
                    .eq("session_id", payload.session_id) \
                    .execute()
            except Exception as e:
                print(f"[ERRO Supabase vincular lead_id]: {e}")

        if payload.email and payload.nome:
            send_welcome_email(
                nome=payload.nome,
                email=payload.email,
                areas=areas_str or "serviços AXIOM",
                origem=payload.origem,
            )

        return {"success": True, "lead_id": lead_id}
    except Exception as e:
        print(f"[ERRO Supabase leads]: {e}")
        return {"success": False, "error": str(e)}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    origem: str = "strategic-intelligence"


def classify_complexity(message: str) -> str:
    text = message.lower()
    word_count = len(message.split())
    if any(keyword in text for keyword in COMPLEX_KEYWORDS):
        return "complex"
    if word_count > 40:
        return "complex"
    if word_count <= 12:
        return "simple"
    return "medium"


def call_groq(system_prompt: str, message: str) -> tuple[str, str]:
    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content, "llama-3.1-8b-instant"


def call_openai(system_prompt: str, message: str) -> tuple[str, str]:
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content, "gpt-4o-mini"


def call_anthropic(system_prompt: str, message: str) -> tuple[str, str]:
    completion = anthropic_client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    return completion.content[0].text, "claude-3-5-haiku-20241022"


def get_reply(message: str, level: str, system_prompt: str) -> tuple[str, str]:
    handlers = {
        "simple": call_groq,
        "medium": call_openai,
        "complex": call_anthropic,
    }
    try:
        return handlers[level](system_prompt, message)
    except Exception:
        try:
            return call_groq(system_prompt, message)
        except Exception:
            return (
                "Desculpe, não consegui processar sua mensagem agora. Tente novamente em instantes.",
                "fallback",
            )


@app.get("/")
def root():
    return {"status": "ok", "message": "AXIOM backend funcionando"}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    system_prompt = SYSTEM_PROMPTS.get(payload.origem, SYSTEM_PROMPTS["strategic-intelligence"])
    level = classify_complexity(payload.message)
    reply, model_used = get_reply(payload.message, level, system_prompt)
    try:
        supabase.table("chat_history").insert({
            "session_id": payload.session_id,
            "user_message": payload.message,
            "assistant_message": reply,
            "model": model_used,
            "tokens_used": None,
            "origem": payload.origem,
        }).execute()
    except Exception as e:
        print(f"[ERRO Supabase chat_history]: {e}")
    return {"reply": reply}