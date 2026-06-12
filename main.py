import os
import re
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


class LeadRequest(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    empresa: str | None = None
    mensagem: str | None = None
    interesse: list[str] | None = None
    origem: str = "strategic-intelligence"

@app.post("/api/lead")
def lead(payload: LeadRequest):
    try:
        result = supabase.table("leads").insert({
            "nome": payload.nome,
            "email": payload.email,
            "telefone": payload.telefone,
            "empresa": payload.empresa,
            "mensagem": payload.mensagem,
            "area_interesse": ", ".join(payload.interesse) if payload.interesse else None,
            "origem": payload.origem,
            "status": "novo",
        }).execute()
        lead_id = result.data[0]["id"] if result.data else None
        return {"success": True, "lead_id": lead_id}
    except Exception as e:
        print(f"[ERRO Supabase leads]: {e}")
        return {"success": False}


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
    primary = handlers[level]

    try:
        return primary(system_prompt, message)
    except Exception:
        # fallback de erro -> sempre Groq
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