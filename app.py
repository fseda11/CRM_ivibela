import streamlit as st
import pandas as pd
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ivibe CRM — ATD 2026", page_icon="⚡", layout="wide")


# ── Secrets ────────────────────────────────────────────────────────────────────

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

GROQ_API_KEY = get_secret("GROQ_API_KEY")
LOGIN_USER   = get_secret("LOGIN_USER")
LOGIN_PASS   = get_secret("LOGIN_PASS")
GROQ_MODEL   = "llama-3.3-70b-versatile"


# ── Login ──────────────────────────────────────────────────────────────────────

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚡ ivibe CRM")
    st.subheader("Acesso restrito")
    st.divider()
    col, _ = st.columns([1, 2])
    with col:
        user = st.text_input("Usuario")
        pwd  = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if user == LOGIN_USER and pwd == LOGIN_PASS:
                st.session_state.logged_in = True
                st.session_state.pagina = "CRM"
                st.rerun()
            else:
                st.error("Usuario ou senha incorretos.")
    st.stop()


# ── Dados ──────────────────────────────────────────────────────────────────────

COUNTRY_NORMALIZE = {
    "BR": "Brazil",
    "US": "United States",
    "CA": "United States",
    "CL": "United States",
}

@st.cache_data
def load_leads():
    path = os.path.join(os.path.dirname(__file__), "leads_data.json")
    with open(path, encoding="utf-8") as f:
        df = pd.DataFrame(json.load(f))
    df["pais"] = df["pais"].replace(COUNTRY_NORMALIZE)
    return df

df = load_leads()


# ── Geração de email (sempre em inglês) ───────────────────────────────────────

def gerar_email(lead):
    prompt = f"""You are a B2B sales expert for ivibe, a corporate learning and engagement platform.

Write a short, personalized follow-up email to {lead.get('nome','')}, who is {lead.get('cargo') or 'a professional'} at {lead.get('empresa') or 'their company'} ({lead.get('pais', '')}).

About this person:
- Professional background: {lead.get('resumo', '')}
- Note from our ATD conversation: {lead.get('notes', 'none')}

Rules:
- Write in English
- Max 5 sentences in the body
- Reference something specific about the person or their company
- If there is a conversation note, use it as the main hook
- End with a clear CTA (e.g. 15-min call)
- Use this exact format:

Subject: [subject line]

[email body]

Best,
ivibe Team

Output only the email, nothing else."""

    client = Groq(api_key=GROQ_API_KEY)
    r = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7,
    )
    return r.choices[0].message.content


# ── Helpers ────────────────────────────────────────────────────────────────────

def badge(score):
    if score >= 7: return "HOT"
    if score >= 3: return "Morno"
    return "Frio"

def emoji(score):
    if score >= 7: return "🔥"
    if score >= 3: return "⚡"
    return "❄️"


# ── Sidebar: navegação ─────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚡ ivibe CRM")
    st.caption("ATD 2026")
    st.divider()

    if "pagina" not in st.session_state:
        st.session_state.pagina = "CRM"

    if st.button("📋  CRM — Leads", use_container_width=True):
        st.session_state.pagina = "CRM"
    if st.button("📊  Relatorios", use_container_width=True):
        st.session_state.pagina = "Relatorios"

    st.divider()

    hot  = len(df[df["score"] >= 7])
    warm = len(df[(df["score"] >= 3) & (df["score"] < 7)])
    cold = len(df[df["score"] < 3])

    st.write(f"🔥 {hot} HOT")
    st.write(f"⚡ {warm} Mornos")
    st.write(f"❄️ {cold} Frios")
    st.divider()
    st.caption("Modelo: Llama 3.3 70B via Groq")
    st.divider()
    if st.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: CRM
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.pagina == "CRM":

    st.title("⚡ ivibe CRM — ATD 2026")
    st.caption("Evento ATD 2026 · 17-18 de maio")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de leads", len(df))
    c2.metric("HOT - abordar hoje", hot)
    c3.metric("Morno - esta semana", warm)
    c4.metric("Frio - nutrir", cold)
    st.divider()

    f1, f2, f3 = st.columns([2, 2, 4])
    with f1:
        filtro_prio = st.selectbox("Prioridade", ["Todos", "HOT", "Morno", "Frio"])
    with f2:
        paises = ["Todos"] + sorted(df["pais"].dropna().unique().tolist())
        filtro_pais = st.selectbox("Pais", paises)
    with f3:
        busca = st.text_input("Buscar por nome, empresa, cargo...", placeholder="ex: Kaiser, Brazil, Director...")

    res = df.copy()
    if filtro_prio == "HOT":
        res = res[res["score"] >= 7]
    elif filtro_prio == "Morno":
        res = res[(res["score"] >= 3) & (res["score"] < 7)]
    elif filtro_prio == "Frio":
        res = res[res["score"] < 3]
    if filtro_pais != "Todos":
        res = res[res["pais"] == filtro_pais]
    if busca:
        mask = res.apply(lambda r: busca.lower() in " ".join([
            str(r.get("nome","")), str(r.get("empresa","")),
            str(r.get("cargo","")), str(r.get("pais","")), str(r.get("notes",""))
        ]).lower(), axis=1)
        res = res[mask]

    st.caption(f"{len(res)} leads encontrados")

    if "emails" not in st.session_state:
        st.session_state.emails = {}

    for i, (_, row) in enumerate(res.iterrows()):
        lead = row.to_dict()
        uid  = f"{i}_{str(lead.get('email',''))[:30]}"

        nome    = lead.get("nome", "")
        cargo   = lead.get("cargo", "") or ""
        empresa = lead.get("empresa", "") or ""
        pais    = lead.get("pais", "") or ""
        score   = lead.get("score", 0)

        label = f"{emoji(score)} {badge(score)}  |  {nome}  |  {empresa}  |  {pais}"

        with st.expander(label):
            col_info, col_links = st.columns([3, 1])

            with col_info:
                if lead.get("notes"):
                    st.info(f"Nota do evento: {lead['notes']}")
                if cargo:
                    st.write(f"**Cargo:** {cargo}")
                if lead.get("resumo"):
                    st.write(f"**Perfil:** {lead['resumo']}")
                if lead.get("razoes"):
                    st.write(f"**Score:** {lead['razoes']}")

            with col_links:
                st.write(f"**Score:** {score}/10  {emoji(score)}")
                email_val = lead.get("email", "")
                if email_val and email_val not in ("", "No@email.com"):
                    st.write(f"📧 {email_val}")
                linkedin = lead.get("linkedin", "")
                if linkedin and linkedin not in ("", "Not found", "Nao encontrado"):
                    st.markdown(f"[🔗 LinkedIn]({linkedin})")
                site = lead.get("site", "")
                if site and site not in ("", "Not found", "Nao encontrado"):
                    st.markdown(f"[🌐 Site]({site})")

            st.write("")
            btn_label = "Gerar novo email" if uid in st.session_state.emails else "Gerar email em ingles com IA"
            if st.button(btn_label, key=f"gen_{uid}"):
                with st.spinner("Gerando via Llama 3.3..."):
                    try:
                        st.session_state.emails[uid] = gerar_email(lead)
                    except Exception as e:
                        st.error(f"Erro: {e}")

            if uid in st.session_state.emails:
                st.text_area("Email gerado", value=st.session_state.emails[uid],
                             height=220, key=f"txt_{uid}")
                st.download_button(
                    "Baixar .txt",
                    data=st.session_state.emails[uid],
                    file_name=f"email_{nome.replace(' ','_')}.txt",
                    mime="text/plain",
                    key=f"dl_{uid}",
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA: RELATORIOS
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.pagina == "Relatorios":

    st.title("📊 Relatorios — ATD 2026")
    st.caption("Analise dos 98 leads coletados no evento")
    st.divider()

    # ── Resumo geral ──────────────────────────────────────────────────────────
    st.subheader("Resumo geral")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de leads", len(df))
    c2.metric("HOT", hot)
    c3.metric("Morno", warm)
    c4.metric("Frio", cold)

    st.divider()

    # ── Por pais ──────────────────────────────────────────────────────────────
    st.subheader("Leads por pais")
    pais_count = df["pais"].value_counts().reset_index()
    pais_count.columns = ["Pais", "Quantidade"]
    st.bar_chart(pais_count.set_index("Pais"))

    st.divider()

    # ── Por prioridade ────────────────────────────────────────────────────────
    st.subheader("Distribuicao por prioridade")
    df["Prioridade"] = df["score"].apply(badge)
    prio_count = df["Prioridade"].value_counts().reset_index()
    prio_count.columns = ["Prioridade", "Quantidade"]
    st.bar_chart(prio_count.set_index("Prioridade"))

    st.divider()

    # ── Por cargo (Udef01) ────────────────────────────────────────────────────
    cargo_col = "udef01" if "udef01" in df.columns else None
    if cargo_col:
        st.subheader("Leads por funcao")
        cargo_count = df[cargo_col].dropna().value_counts().head(12).reset_index()
        cargo_count.columns = ["Funcao", "Quantidade"]
        st.bar_chart(cargo_count.set_index("Funcao"))
        st.divider()

    # ── Top leads com notas ───────────────────────────────────────────────────
    st.subheader("Leads com notas de conversa")
    com_notas = df[df["notes"].astype(str).str.len() > 2].sort_values("score", ascending=False)
    for _, r in com_notas.iterrows():
        st.write(f"{emoji(r['score'])} **{r['nome']}** — {r.get('empresa','')} — Score {r['score']}")
        st.caption(f"Nota: {r['notes']}")

    st.divider()

    # ── Tabela completa ───────────────────────────────────────────────────────
    st.subheader("Tabela completa")
    tabela = df[["nome", "cargo", "empresa", "pais", "email", "score", "Prioridade"]].copy()
    tabela = tabela.rename(columns={
        "nome": "Nome", "cargo": "Cargo", "empresa": "Empresa",
        "pais": "Pais", "email": "Email", "score": "Score", "Prioridade": "Prioridade"
    })
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    csv = tabela.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar tabela como CSV", data=csv,
                       file_name="leads_atd2026.csv", mime="text/csv")
