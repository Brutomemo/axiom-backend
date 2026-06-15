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

LOGO_URL = "https://twzzolhitqypdosweqnj.supabase.co/storage/v1/object/public/axiom_backend/imagem_email/logo-email.webp"
SITE_URL = "https://axiomstrategic.com.br"


def build_email_html(nome: str, areas: str, origem: str) -> str:
    is_hp = origem == "human-performance"
    divisao = "Human Performance" if is_hp else "Strategic Intelligence"
    link = f"{SITE_URL}/pages/human-performance.html" if is_hp else SITE_URL
    cta = "Explorar Human Performance" if is_hp else "Explorar Strategic Intelligence"

    if is_hp:
        intro = f"""A sua organização deu um passo importante. Identificar que <strong style="color:#e2e8f0;">pessoas são o centro de qualquer resultado sustentável</strong> é o começo de uma transformação real."""
        contexto = """A AXIOM Human Performance atua na intersecção entre psicologia organizacional, dados comportamentais e estratégia — transformando riscos psicossociais em planos de ação, e ambientes fragmentados em culturas de alto desempenho."""
        ponte = """Mas performance humana não existe isolada. Quando integrada à inteligência estratégica — com dados, automação e tecnologia — os resultados se tornam <strong style="color:#e2e8f0;">mais precisos, mais rápidos e mais duradouros.</strong>"""
    else:
        intro = f"""Dados sem direção são ruído. A sua organização reconheceu que <strong style="color:#e2e8f0;">decisões mais assertivas nascem de informações bem estruturadas</strong> — e isso já é uma vantagem competitiva."""
        contexto = """A AXIOM Strategic Intelligence transforma dados brutos em inteligência operacional: KPIs que refletem a estratégia real do negócio, OKRs que alinham equipes, e aplicações web que colocam a informação certa nas mãos certas."""
        ponte = """E quando a tecnologia encontra o fator humano — com diagnósticos comportamentais, saúde organizacional e desenvolvimento de lideranças — os resultados deixam de ser pontuais e se tornam <strong style="color:#e2e8f0;">sistêmicos e escaláveis.</strong>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AXIOM {divisao}</title>
</head>
<body style="margin:0;padding:0;background:#07080d;font-family:'Segoe UI',Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#07080d;padding:48px 16px;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
style="max-width:600px;width:100%;background:#0d0f18;border-radius:16px;
        border:1px solid #1a2035;overflow:hidden;
        box-shadow:0 0 60px rgba(6,182,212,0.06);">

<!-- HEADER -->
<tr>
    <td style="background:linear-gradient(160deg,#0d0f18 0%,#0f1628 60%,#0a1020 100%);
            padding:48px 48px 36px;text-align:center;
            border-bottom:1px solid #1a2035;position:relative;">
    <img src="{LOGO_URL}" alt="AXIOM {divisao}" width="160"
        style="max-width:160px;height:auto;display:block;margin:0 auto 20px;" />
    <div style="display:inline-block;background:rgba(6,182,212,0.08);
                border:1px solid rgba(6,182,212,0.2);border-radius:20px;
                padding:4px 16px;margin-bottom:0;">
        <span style="color:#06b6d4;font-size:11px;letter-spacing:3px;
                    text-transform:uppercase;font-weight:600;">{divisao}</span>
    </div>
    </td>
</tr>

<!-- SAUDAÇÃO -->
<tr>
    <td style="padding:48px 48px 0;">
    <p style="color:#64748b;font-size:12px;letter-spacing:2px;
                text-transform:uppercase;margin:0 0 12px;">
        Solicitação recebida
    </p>
    <h1 style="color:#f1f5f9;font-size:26px;font-weight:600;
                line-height:1.3;margin:0 0 24px;">
        {nome},<br>
        <span style="color:#06b6d4;">sua jornada começa agora.</span>
    </h1>
    <p style="color:#64748b;font-size:14px;line-height:1.8;margin:0 0 32px;">
        {intro}
    </p>
    </td>
</tr>

<!-- ÁREA DE INTERESSE -->
<tr>
    <td style="padding:0 48px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
        <td style="background:linear-gradient(135deg,#0f1e2e,#0d1520);
                    border:1px solid rgba(6,182,212,0.15);
                    border-left:3px solid #06b6d4;
                    border-radius:0 10px 10px 0;padding:20px 24px;">
            <p style="color:#475569;font-size:11px;letter-spacing:2px;
                    text-transform:uppercase;margin:0 0 8px;">
            Seu interesse
            </p>
            <p style="color:#06b6d4;font-size:15px;font-weight:600;
                    line-height:1.6;margin:0;">
            {areas}
            </p>
        </td>
        </tr>
    </table>
    </td>
</tr>

<!-- SOBRE A AXIOM -->
<tr>
    <td style="padding:0 48px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
            style="background:#0a0c14;border:1px solid #1a2035;
                    border-radius:12px;overflow:hidden;">
        <tr>
        <td style="padding:32px;">
            <p style="color:#94a3b8;font-size:14px;line-height:1.8;margin:0 0 20px;">
            {contexto}
            </p>
            <!-- DIVISOR SUTIL -->
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td style="height:1px;background:linear-gradient(to right,transparent,#1e293b,transparent);
                        padding:0;margin:0 0 20px;display:block;">
                </td>
            </tr>
            </table>
            <p style="color:#64748b;font-size:13px;line-height:1.8;margin:20px 0 0;">
            {ponte}
            </p>
        </td>
        </tr>
    </table>
    </td>
</tr>

<!-- INTEGRAÇÃO DOS DOIS BRAÇOS -->
<tr>
    <td style="padding:0 48px 40px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
        <!-- Strategic Intelligence -->
        <td width="48%" style="background:#0d0f18;border:1px solid #1a2035;
                                border-radius:10px;padding:20px;
                                vertical-align:top;">
            <p style="color:#06b6d4;font-size:10px;letter-spacing:2px;
                    text-transform:uppercase;margin:0 0 8px;font-weight:600;">
            Strategic Intelligence
            </p>
            <p style="color:#64748b;font-size:12px;line-height:1.6;margin:0;">
            Dados, KPIs, OKRs e tecnologia transformados em decisões estratégicas.
            </p>
        </td>
        <!-- Espaço -->
        <td width="4%"></td>
        <!-- Human Performance -->
        <td width="48%" style="background:#0d0f18;border:1px solid #1a2035;
                                border-radius:10px;padding:20px;
                                vertical-align:top;">
            <p style="color:#06b6d4;font-size:10px;letter-spacing:2px;
                    text-transform:uppercase;margin:0 0 8px;font-weight:600;">
            Human Performance
            </p>
            <p style="color:#64748b;font-size:12px;line-height:1.6;margin:0;">
            Diagnóstico, saúde organizacional e liderança orientados por evidências.
            </p>
        </td>
        </tr>
    </table>
    <p style="color:#475569;font-size:12px;text-align:center;
                line-height:1.6;margin:20px 0 0;font-style:italic;">
        "Inteligência estratégica + desempenho humano = resultados sustentáveis."
    </p>
    </td>
</tr>

<!-- PRÓXIMO PASSO -->
<tr>
    <td style="padding:0 48px 40px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
            style="background:linear-gradient(135deg,rgba(6,182,212,0.05),rgba(6,182,212,0.02));
                    border:1px solid rgba(6,182,212,0.1);border-radius:12px;">
        <tr>
        <td style="padding:28px;text-align:center;">
            <p style="color:#94a3b8;font-size:14px;line-height:1.7;margin:0 0 24px;">
            Nossa equipe está analisando seu perfil e entrará em contato
            <strong style="color:#e2e8f0;">em breve</strong> para uma conversa
            sem compromisso — focada nas necessidades reais da sua organização.
            </p>
            <a href="{link}"
            style="display:inline-block;background:#06b6d4;color:#000;
                    font-weight:700;font-size:14px;padding:14px 36px;
                    border-radius:8px;text-decoration:none;
                    letter-spacing:0.5px;">
            {cta} →
            </a>
        </td>
        </tr>
    </table>
    </td>
</tr>

<!-- FOOTER -->
<tr>
    <td style="padding:24px 48px 32px;border-top:1px solid #1a2035;text-align:center;">
    <p style="color:#1e293b;font-size:11px;margin:0 0 6px;letter-spacing:1px;
                text-transform:uppercase;">
        AXIOM · axiomstrategic.com.br
    </p>
    <p style="color:#1e293b;font-size:11px;margin:0;line-height:1.6;">
        Você recebeu este e-mail porque entrou em contato pelo nosso site.<br>
        Suas informações são tratadas com confidencialidade, em conformidade com a LGPD.
    </p>
    </td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>"""

EMAIL_SUBJECTS = {
    "strategic-intelligence": "AXIOM — Sua jornada estratégica começa agora",
    "human-performance": "AXIOM Human Performance — Recebemos sua solicitação",
}


def send_welcome_email(nome: str, email: str, areas: str, origem: str):
    subject = EMAIL_SUBJECTS.get(origem, EMAIL_SUBJECTS["strategic-intelligence"])
    html = build_email_html(nome, areas, origem)
    try:
        resend.Emails.send({
            "from": "AXIOM <onboarding@resend.dev>",
            "to": [email],
            "subject": subject,
            "html": html,
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