"""
Interface Conseiller La Poste — Dashboard IA (Thème clair eKonsilio-style)
app/ui/streamlit_app.py
streamlit run app/ui/streamlit_app.py
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="La Poste · Espace Conseiller",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
/* Streamlit injects its own left offset — override it */
section.main > div { padding-left: 0 !important; padding-right: 0 !important; padding-top: 0 !important; }
[data-testid="stAppViewContainer"] > section { padding: 0 !important; }

/* ── Shell ─────────────────────────────────────────────────────────────── */
.shell { display: flex; min-height: 100vh; background: #F4F6FA; }

/* ── Sidebar ────────────────────────────────────────────────────────────── */
.nav {
    width: 56px;
    background: #1C1C2E;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 18px 0;
    gap: 6px;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 1000;
}
/* Push ALL streamlit content right of the nav */
[data-testid="stAppViewContainer"] {
    padding-left: 56px !important;
}
[data-testid="stHeader"] { padding-left: 56px !important; }
.nav-logo {
    width: 34px; height: 34px;
    background: #FFFFFF18;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    margin-bottom: 14px;
    border: 1px solid #ffffff22;
}
.nav-item {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    cursor: pointer;
    color: #6B7A99;
    transition: all 0.15s;
}
.nav-item.active { background: #2E2E4A; color: #FFFFFF; }
.nav-item:hover:not(.active) { background: #25253A; color: #aaa; }
.nav-bottom { margin-top: auto; }
.nav-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6C63FF, #48B0F7);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; color: #fff;
    margin-top: 14px;
}

/* ── Topbar ─────────────────────────────────────────────────────────────── */
.topbar {
    height: 62px;
    background: #FFFFFF;
    border-bottom: 1px solid #E8ECF4;
    display: flex;
    align-items: center;
    padding: 0 28px;
    gap: 20px;
    position: sticky;
    top: 0;
    z-index: 50;
    box-shadow: 0 1px 0 #E8ECF4;
}
.topbar-greeting { flex: 1; }
.topbar-greeting-name { font-size: 1rem; font-weight: 700; color: #1C1C2E; }
.topbar-greeting-sub  { font-size: 0.75rem; color: #9AA3B5; font-weight: 400; margin-top: 1px; }

.topbar-tabs { display: flex; gap: 0; }
.topbar-tab {
    padding: 6px 14px;
    font-size: 0.78rem; font-weight: 500;
    color: #9AA3B5;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    white-space: nowrap;
    display: flex; align-items: center; gap: 6px;
}
.topbar-tab.active { color: #1C1C2E; border-bottom-color: #1C1C2E; }

.topbar-right { display: flex; align-items: center; gap: 10px; margin-left: auto; }
.topbar-agent-label { font-size: 0.72rem; color: #9AA3B5; }
.agent-toggle {
    display: flex; background: #F0F2F8; border-radius: 8px; padding: 3px;
}
.agent-toggle-btn {
    padding: 4px 12px;
    font-size: 0.72rem; font-weight: 600;
    border-radius: 6px; cursor: pointer;
    color: #9AA3B5;
}
.agent-toggle-btn.active { background: #fff; color: #1C1C2E; box-shadow: 0 1px 3px #0001; }

/* ── Page ───────────────────────────────────────────────────────────────── */
.page { padding: 28px; }

/* ── KPI Row ────────────────────────────────────────────────────────────── */
.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8ECF4;
    border-radius: 14px;
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.kpi-label { font-size: 0.72rem; color: #9AA3B5; font-weight: 500; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.kpi-value { font-size: 2rem; font-weight: 700; color: #1C1C2E; line-height: 1; }
.kpi-sub   { font-size: 0.73rem; color: #B0B8CC; margin-top: 4px; }
.kpi-up   { color: #22C55E !important; }
.kpi-down { color: #EF4444 !important; }

/* KPI 3-column time stats */
.kpi-time-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.kpi-time-card {
    background: #FFFFFF;
    border: 1px solid #E8ECF4;
    border-radius: 14px;
    padding: 18px 20px;
}
.kpi-time-label { font-size: 0.72rem; color: #9AA3B5; font-weight: 500; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.kpi-time-value { font-size: 1.65rem; font-weight: 700; color: #1C1C2E; }

/* ── Agents panel (right rail) ──────────────────────────────────────────── */
.agents-panel {
    width: 220px;
    background: #FFFFFF;
    border: 1px solid #E8ECF4;
    border-radius: 14px;
    padding: 14px;
    flex-shrink: 0;
}
.agents-title { font-size: 0.7rem; font-weight: 600; color: #9AA3B5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
.agent-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid #F0F2F8;
}
.agent-row:last-child { border-bottom: none; }
.agent-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: #E8ECF4;
    flex-shrink: 0;
    overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: #6B7A99;
}
.agent-name { font-size: 0.77rem; font-weight: 500; color: #1C1C2E; flex: 1; }
.agent-count { font-size: 0.75rem; font-weight: 600; color: #9AA3B5; }
.dot-green  { width: 7px; height: 7px; border-radius: 50%; background: #22C55E; flex-shrink: 0; }
.dot-red    { width: 7px; height: 7px; border-radius: 50%; background: #EF4444; flex-shrink: 0; }

/* ── Section title ──────────────────────────────────────────────────────── */
.section-title { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #B0B8CC; margin: 0 0 12px; }

/* ── Demand table ───────────────────────────────────────────────────────── */
.demand-table { background: #FFFFFF; border: 1px solid #E8ECF4; border-radius: 14px; overflow: hidden; margin-bottom: 4px; }
.demand-header {
    display: grid;
    grid-template-columns: 2fr 1.6fr 1fr 1fr 1fr 70px;
    padding: 10px 20px;
    border-bottom: 1px solid #F0F2F8;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #B0B8CC;
}
.demand-row {
    display: grid;
    grid-template-columns: 2fr 1.6fr 1fr 1fr 1fr 70px;
    padding: 13px 20px;
    border-bottom: 1px solid #F7F8FC;
    align-items: center;
    cursor: pointer;
    transition: background 0.12s;
}
.demand-row:hover { background: #F7F8FC; }
.demand-row:last-child { border-bottom: none; }
.d-from { font-size: 0.83rem; font-weight: 600; color: #1C1C2E; }
.d-sub  { font-size: 0.71rem; color: #B0B8CC; margin-top: 2px; }
.d-cat  { font-size: 0.76rem; color: #6B7A99; }
.d-time { font-size: 0.73rem; color: #B0B8CC; font-family: 'DM Mono', monospace; }

/* ── Badges ─────────────────────────────────────────────────────────────── */
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 20px; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.03em; }
.badge-orange { background: #FFF4E0; color: #D97706; border: 1px solid #FDDBA0; }
.badge-red    { background: #FEF0F0; color: #EF4444; border: 1px solid #FCCACA; }
.badge-green  { background: #EDFAF3; color: #16A34A; border: 1px solid #A7F3C7; }
.badge-blue   { background: #EFF6FF; color: #3B82F6; border: 1px solid #BFDBFE; }
.badge-purple { background: #F5F3FF; color: #7C3AED; border: 1px solid #DDD6FE; }
.badge-grey   { background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }

.chan { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 6px; font-size: 0.7rem; font-weight: 500; background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }

/* ── Detail panel ───────────────────────────────────────────────────────── */
.detail-panel { background: #FFFFFF; border: 1px solid #E8ECF4; border-radius: 14px; margin-bottom: 14px; overflow: hidden; }
.dp-header { padding: 14px 18px 12px; border-bottom: 1px solid #F0F2F8; }
.dp-name { font-size: 0.85rem; font-weight: 600; color: #1C1C2E; }
.dp-meta { font-size: 0.7rem; color: #B0B8CC; margin-top: 2px; }
.dp-body { padding: 14px 18px; }

.msg-bubble {
    background: #F7F8FC;
    border: 1px solid #E8ECF4;
    border-left: 3px solid #6C63FF;
    border-radius: 0 8px 8px 0;
    padding: 12px 14px;
    font-size: 0.82rem; color: #4B5A72; line-height: 1.65;
    margin-bottom: 10px; white-space: pre-wrap;
}

.info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #F0F2F8; font-size: 0.79rem; }
.info-row:last-child { border-bottom: none; }
.info-key { color: #9AA3B5; }
.info-val { color: #1C1C2E; font-weight: 500; text-align: right; max-width: 60%; }

.conf-bar-wrap { background: #F0F2F8; border-radius: 6px; height: 4px; overflow: hidden; }
.conf-bar-fill { height: 4px; border-radius: 6px; }

.audit-item { display: flex; gap: 8px; align-items: flex-start; padding: 5px 0; border-bottom: 1px solid #F0F2F8; font-size: 0.72rem; }
.audit-item:last-child { border-bottom: none; }
.audit-dot { width: 6px; height: 6px; border-radius: 50%; background: #6C63FF; margin-top: 4px; flex-shrink: 0; }
.audit-txt { color: #9AA3B5; font-family: 'DM Mono', monospace; line-height: 1.4; }

.esc-banner { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 10px 14px; font-size: 0.8rem; color: #D97706; margin-bottom: 14px; }
.esc-banner.critical { background: #FEF2F2; border-color: #FECACA; color: #EF4444; }

.draft-label { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #B0B8CC; margin-bottom: 6px; }

textarea {
    background: #F7F8FC !important;
    color: #1C1C2E !important;
    border: 1px solid #E8ECF4 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 7px 14px !important;
    transition: all 0.15s !important;
    border: 1px solid #E8ECF4 !important;
    background: #FFFFFF !important;
    color: #1C1C2E !important;
}
.stButton > button[kind="primary"] {
    background: #1C1C2E !important;
    color: #FFFFFF !important;
    border-color: #1C1C2E !important;
}
.stButton > button:hover {
    background: #F7F8FC !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2E2E4A !important;
}

/* hide streamlit row buttons decoration */
div[data-testid="stHorizontalBlock"] { gap: 8px; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #E0E4EE; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
EVENTS_FILES = {
    "evt_001":         "data/events/email_claim/event_001.json",
    "evt_002_simple":  "data/events/email_claim/event_002_simple.json",
    "evt_003_critical":"data/events/email_claim/event_003_critical.json",
    "evt_004_general": "data/events/email_general/event_004_general.json",
    "evt_005_ticket":  "data/events/forms/event_005_ticket.json",
    "evt_006_call":    "data/events/calls/event_006_call.json",
    "evt_007_info":    "data/events/email_general/event_007_info.json",
}

MOCK_DEMANDS = [
    {"id":"evt_001",         "from_name":"Nadia Martin",  "from_email":"nadia.martin@email.fr",  "subject":"Réclamation – colis non reçu",       "channel":"email_claim",   "category":"perte de colis",           "priority":"high",     "status":"en attente","segment":"standard","date":"17/05","time":"10:00","escalate":False,"ticket":True, "confidence":0.85},
    {"id":"evt_003_critical","from_name":"Sophie Leroy",  "from_email":"sophie.leroy@email.fr",  "subject":"Mise en demeure – colis perdu",       "channel":"email_claim",   "category":"perte de colis",           "priority":"critical", "status":"escalade",  "segment":"standard","date":"17/05","time":"10:30","escalate":True, "escalate_to":"direction","ticket":True,"confidence":0.85},
    {"id":"evt_006_call",    "from_name":"Sophie Leroy",  "from_email":"sophie.leroy@email.fr",  "subject":"Appel – colis perdu urgent",          "channel":"call",          "category":"suivi de colis",           "priority":"high",     "status":"en attente","segment":"standard","date":"17/05","time":"11:30","escalate":False,"ticket":True, "confidence":0.85},
    {"id":"evt_005_ticket",  "from_name":"Nadia Martin",  "from_email":"nadia.martin@email.fr",  "subject":"Formulaire réclamation colis",         "channel":"form",          "category":"perte de colis",           "priority":"normal",   "status":"en attente","segment":"standard","date":"17/05","time":"11:15","escalate":False,"ticket":True, "confidence":0.85},
    {"id":"evt_002_simple",  "from_name":"Karim Benali",  "from_email":"karim.benali@email.fr",  "subject":"Question délai livraison",            "channel":"email_general", "category":"demande de renseignement", "priority":"low",      "status":"traité",   "segment":"premium", "date":"16/05","time":"10:15","escalate":False,"ticket":False,"confidence":0.85},
    {"id":"evt_004_general", "from_name":"Karim Benali",  "from_email":"karim.benali@email.fr",  "subject":"Question délai livraison",            "channel":"email_general", "category":"demande de renseignement", "priority":"low",      "status":"traité",   "segment":"premium", "date":"16/05","time":"11:00","escalate":False,"ticket":False,"confidence":0.85},
    {"id":"evt_007_info",    "from_name":"Karim Benali",  "from_email":"karim.benali@email.fr",  "subject":"Demande d'information horaires",      "channel":"email_general", "category":"demande de renseignement", "priority":"low",      "status":"traité",   "segment":"premium", "date":"15/05","time":"11:45","escalate":False,"ticket":False,"confidence":0.85},
]

CHANNEL_ICON  = {"email_claim":"","email_general":"","form":"","call":""}
CHANNEL_LABEL = {"email_claim":"Email réclamation","email_general":"Email général","form":"Formulaire","call":"Appel"}
PRIORITY_BADGE = {"critical":("badge-red","Critique"),"high":("badge-orange","Haute"),"normal":("badge-blue","Normale"),"low":("badge-grey","Basse")}
STATUS_BADGE   = {"en attente":("badge-orange","En attente"),"escalade":("badge-red","Escalade"),"traité":("badge-green","Traité"),"en cours":("badge-blue","En cours")}

MOCK_AGENTS = [
    {"name": "Alice Morel",    "dot": "dot-green", "count": 1},
    {"name": "Théo Vannier",   "dot": "dot-green", "count": 3},
    {"name": "Lucie Bernard",  "dot": "dot-green", "count": 2},
    {"name": "Marc Dupont",    "dot": "dot-red",   "count": 7},
    {"name": "Julie Fontaine", "dot": "dot-red",   "count": 5},
]

def load_event(eid):
    path = ROOT / EVENTS_FILES.get(eid, "")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def run_graph(event):
    from app.graph.workflow import graph
    initial = {
        "event_id": event.get("event_id","evt_ui"), "timestamp": event.get("timestamp", datetime.now().isoformat()),
        "channel": event.get("channel","email_general"), "current_step": "start",
        "customer_email": event.get("customer_email",""), "subject": event.get("subject",""), "body": event.get("body",""),
        "customer_context": None, "customer_history": None,
        "should_create_ticket": False, "ticket_creation_reason": "",
        "rag_documents": [], "rag_sources": [], "draft_response": None, "request_subject": "",
        "should_escalate": False, "escalate_reason": "", "escalate_to": None,
        "audit_log": [], "errors": [],
    }
    return graph.invoke(initial)

def fmt_step(step):
    ts   = step.get("timestamp","")[-8:]
    name = step.get("step","?")
    extra = ""
    if "decision" in step:        extra = " → oui" if step["decision"] else " → non"
    if "customer_found" in step:  extra = " → trouvé" if step["customer_found"] else " → inconnu"
    if "documents_retrieved" in step: extra = f" → {step['documents_retrieved']} doc(s)"
    if "escalate" in step:        extra = " → escalade" if step["escalate"] else " → ok"
    return f"[{ts}] {name}{extra}"

# ══════════════════════════════════════════════════════════════════════════════
# SESSION
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [("selected_id",None),("wf_results",{}),("action_taken",{}),("edited_drafts",{})]:
    if k not in st.session_state: st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# NAV SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="nav">
    <div class="nav-logo">📬</div>
    <div class="nav-item active" title="Dashboard">🏠</div>
    <div class="nav-item" title="Demandes">📥</div>
    <div class="nav-item" title="Clients">👥</div>
    <div class="nav-item" title="Statistiques">📊</div>
    <div class="nav-item" title="Rapports">📈</div>
    <div class="nav-item" title="Paramètres">⚙️</div>
    <div class="nav-bottom">
        <div class="nav-avatar">F&C</div>
    </div>
</div>
""", unsafe_allow_html=True)

sel = st.session_state.selected_id

# ══════════════════════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════════════════════
if sel is None:
    st.markdown("""
    <div class="topbar">
        <div class="topbar-greeting">
            <div class="topbar-greeting-name">Bonjour fast &amp;curious</div>
            <div class="topbar-greeting-sub">Statistiques du jour</div>
        </div>
        <div class="topbar-tabs">
            <div class="topbar-tab active">Tous les canaux</div>
            <div class="topbar-tab">Live Chat</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="topbar">
        <div class="topbar-greeting">
            <div class="topbar-greeting-name">Espace Conseiller — La Poste Service Client IA</div>
            <div class="topbar-greeting-sub">Détail de la demande</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page">', unsafe_allow_html=True)

if sel is None:
    total      = len(MOCK_DEMANDS)
    en_attente = sum(1 for d in MOCK_DEMANDS if d["status"] == "en attente")
    escalades  = sum(1 for d in MOCK_DEMANDS if d["escalate"])
    traites    = sum(1 for d in MOCK_DEMANDS if d["status"] == "traité")

    # Layout: main + right agents panel
    col_main, col_agents = st.columns([4, 1], gap="large")

    with col_agents:
        agents_html = "".join(
            f'<div class="agent-row">'
            f'<div class="agent-avatar">{a["name"].split()[0][0]}{a["name"].split()[-1][0]}</div>'
            f'<div class="{a["dot"]}"></div>'
            f'<div class="agent-name">{a["name"].split()[0]}</div>'
            f'<div class="agent-count">{a["count"]}</div>'
            f'</div>'
            for a in MOCK_AGENTS
        )
        st.markdown(f"""
        <div class="agents-panel">
            <div class="agents-title">Conseillers en ligne</div>
            {agents_html}
        </div>
        """, unsafe_allow_html=True)

    with col_main:
        # KPI top row
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">Conversations</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-sub kpi-up">+3 vs hier</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">En attente</div>
                <div class="kpi-value" style="color:#D97706">{en_attente}</div>
                <div class="kpi-sub">Réponse requise</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Taux de traitement</div>
                <div class="kpi-value" style="color:#16A34A">{int(traites/total*100)}%</div>
                <div class="kpi-sub kpi-up">{traites} traitées sur {total}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI time row
        st.markdown(f"""
        <div class="kpi-time-row">
            <div class="kpi-time-card">
                <div class="kpi-time-label">Temps 1ère réponse</div>
                <div class="kpi-time-value">16s</div>
            </div>
            <div class="kpi-time-card">
                <div class="kpi-time-label">Temps de réponse moyen</div>
                <div class="kpi-time-value">18 min</div>
            </div>
            <div class="kpi-time-card">
                <div class="kpi-time-label">Escalades actives</div>
                <div class="kpi-time-value" style="color:#EF4444">{escalades}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<p class="section-title">Toutes les demandes entrantes — {len(MOCK_DEMANDS)} au total</p>', unsafe_allow_html=True)

        st.markdown("""
        <div class="demand-table">
            <div class="demand-header">
                <span>Expéditeur</span>
                <span>Catégorie / Sujet</span>
                <span>Canal</span>
                <span>Priorité</span>
                <span>Statut</span>
                <span>Date</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for d in MOCK_DEMANDS:
            p_cls, p_lbl = PRIORITY_BADGE[d["priority"]]
            s_cls, s_lbl = STATUS_BADGE[d["status"]]
            ci = CHANNEL_ICON.get(d["channel"],"📩")
            cl = CHANNEL_LABEL.get(d["channel"], d["channel"])
            seg_tag = ' <span style="font-size:0.6rem;color:#7C3AED;background:#F5F3FF;border:1px solid #DDD6FE;border-radius:20px;padding:2px 7px;margin-left:5px">PREMIUM</span>' if d["segment"] == "premium" else ""
            esc_tag = ' <span style="color:#EF4444;font-size:0.75rem;font-weight:700">!</span>' if d["escalate"] else ""

            if st.button(
                f"→ {d['from_name']} · {d['subject'][:50]}",
                key=f"btn_{d['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_id = d["id"]
                st.rerun()

            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E8ECF4;border-radius:0;border-top:none;
                        padding:12px 20px;
                        display:grid;grid-template-columns:2fr 1.6fr 1fr 1fr 1fr 70px;
                        align-items:center;
                        margin-top:-44px;pointer-events:none;border-bottom:1px solid #F7F8FC">
                <div>
                    <div class="d-from">{d['from_name']}{seg_tag}{esc_tag}</div>
                    <div class="d-sub">{d['from_email']}</div>
                </div>
                <div>
                    <div class="d-cat">{d['category']}</div>
                    <div class="d-sub">{d['subject'][:42]}{'…' if len(d['subject'])>42 else ''}</div>
                </div>
                <div><span class="chan">{cl}</span></div>
                <div><span class="badge {p_cls}">{p_lbl}</span></div>
                <div><span class="badge {s_cls}">{s_lbl}</span></div>
                <div class="d-time">{d['date']}<br>{d['time']}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DÉTAIL DEMANDE
# ══════════════════════════════════════════════════════════════════════════════
else:
    demand = next((d for d in MOCK_DEMANDS if d["id"] == sel), None)
    if not demand:
        st.session_state.selected_id = None
        st.rerun()

    if st.button("← Retour au dashboard"):
        st.session_state.selected_id = None
        st.rerun()

    if sel not in st.session_state.wf_results:
        ev = load_event(sel)
        if ev:
            with st.spinner("Analyse automatique IA en cours…"):
                try:
                    res = run_graph(ev)
                    st.session_state.wf_results[sel] = res
                    if res.get("draft_response"):
                        st.session_state.edited_drafts[sel] = res["draft_response"].body
                except Exception as e:
                    st.error(f"Erreur workflow : {e}")
                    st.stop()
        else:
            st.error("Événement introuvable.")
            st.stop()

    result = st.session_state.wf_results[sel]
    event  = load_event(sel)
    draft  = result.get("draft_response")
    ctx    = result.get("customer_context")
    hist   = result.get("customer_history") or {}
    audit  = result.get("audit_log", [])
    errors = result.get("errors", [])
    p_cls, p_lbl = PRIORITY_BADGE[demand["priority"]]
    s_cls, s_lbl = STATUS_BADGE[demand["status"]]
    ci = CHANNEL_ICON.get(demand["channel"],"📩")
    cl = CHANNEL_LABEL.get(demand["channel"], demand["channel"])

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:16px 0 18px">
        <div style="font-size:1.05rem;font-weight:700;color:#1C1C2E;flex:1">{demand['subject']}</div>
        <span class="badge {p_cls}">{p_lbl}</span>
        <span class="badge {s_cls}">{s_lbl}</span>
        {"<span class='badge badge-red'>Escalade</span>" if result.get("should_escalate") else ""}
    </div>
    """, unsafe_allow_html=True)

    if result.get("should_escalate"):
        dest   = result.get("escalate_to","superviseur")
        reason = result.get("escalate_reason","")
        cls    = "critical" if dest == "direction" else ""
        st.markdown(f'<div class="esc-banner {cls}"><strong>Escalade → {dest.upper()}</strong> · {reason}</div>', unsafe_allow_html=True)

    col_l, col_m = st.columns([1.1, 1.4], gap="medium")

    with col_l:
        st.markdown(f"""
        <div class="detail-panel">
            <div class="dp-header">
                <div class="dp-name">Message reçu</div>
                <div class="dp-meta">{demand['from_name']} · {demand['time']}</div>
            </div>
            <div class="dp-body">
                <div class="msg-bubble">{event.get('body','')}</div>
                <div style="font-size:0.68rem;color:#D0D5E2">{event.get('event_id','')} · {event.get('timestamp','')[:16].replace('T',' ')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if ctx:
            ic = "#D97706" if ctx.segment == "premium" else "#3B82F6"
            vc = "#EF4444" if ctx.known_issues_count > 2 else "#16A34A"
            st.markdown(f"""
            <div class="detail-panel">
                <div class="dp-header">
                    <div class="dp-name">Fiche client CRM</div>
                    <div class="dp-meta">Dynamics 365</div>
                </div>
                <div class="dp-body">
                    <div style="font-size:0.9rem;font-weight:600;color:#1C1C2E;margin-bottom:8px">{ctx.name} <span class="badge" style="background:#FFF4E0;color:{ic};border:1px solid #FDDBA0;font-size:0.6rem">{ctx.segment.upper()}</span></div>
                    <div class="info-row"><span class="info-key">Email</span><span class="info-val" style="font-size:0.72rem">{ctx.email}</span></div>
                    <div class="info-row"><span class="info-key">Téléphone</span><span class="info-val">{ctx.phone}</span></div>
                    <div class="info-row"><span class="info-key">Ville</span><span class="info-val">{ctx.city}</span></div>
                    <div class="info-row"><span class="info-key">Incidents</span><span class="info-val" style="color:{vc};font-weight:700">{ctx.known_issues_count}</span></div>
                    <div class="info-row"><span class="info-key">Tickets passés</span><span class="info-val">{hist.get('total_tickets','—')} · {hist.get('open_tickets',0)} ouvert(s)</span></div>
                    <div class="info-row"><span class="info-key">Dernier ticket</span><span class="info-val">{hist.get('last_ticket_date','—')}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="detail-panel"><div class="dp-header"><div class="dp-name">Fiche client</div></div><div class="dp-body" style="color:#B0B8CC;font-size:0.8rem">Client non identifié dans CRM</div></div>', unsafe_allow_html=True)

    with col_m:
        req_sub   = result.get("request_subject") or "—"
        sources   = result.get("rag_sources", [])

        st.markdown(f"""
        <div class="detail-panel">
            <div class="dp-header">
                <div class="dp-name">Analyse IA automatique</div>
                <div class="dp-meta">LangGraph · Mistral · RAG</div>
            </div>
            <div class="dp-body">
                <div class="info-row"><span class="info-key">Catégorie</span><span class="info-val" style="color:#6C63FF;font-weight:600">{req_sub}</span></div>
                <div class="info-row"><span class="info-key">Canal</span><span class="info-val">{cl}</span></div>
                <div class="info-row"><span class="info-key">Ticket</span><span class="info-val">{"Créé" if result.get("should_create_ticket") else "Non requis"}</span></div>
                <div class="info-row"><span class="info-key">Sources RAG</span><span class="info-val" style="font-size:0.72rem">{", ".join(sources) if sources else "—"}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="draft-label">Brouillon — modifiable avant envoi</div>', unsafe_allow_html=True)

        action_done = st.session_state.action_taken.get(sel)

        if action_done:
            if action_done == "send":          st.success("Réponse envoyée · Ticket mis à jour")
            elif action_done == "escalate":    st.warning(f"Transmis → **{result.get('escalate_to','superviseur').upper()}**")
            elif action_done == "request_info":st.info("Demande d'infos envoyée au client")
            elif action_done == "reject":      st.error("Brouillon rejeté")
            if st.button("Réinitialiser", key=f"rst_{sel}"):
                st.session_state.action_taken.pop(sel, None)
                st.rerun()
        else:
            if draft:
                edited = st.text_area("Brouillon", value=st.session_state.edited_drafts.get(sel, draft.body),
                                      height=210, label_visibility="collapsed", key=f"draft_{sel}")
                st.session_state.edited_drafts[sel] = edited
                conf = draft.confidence
                cc = "#22C55E" if conf >= 0.8 else "#D97706" if conf >= 0.6 else "#EF4444"
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin:4px 0 14px">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#B0B8CC;font-size:0.8rem;padding:10px 0">Aucun brouillon généré.</div>', unsafe_allow_html=True)

            ba, bb = st.columns(2)
            with ba:
                if st.button("Envoyer",        key=f"send_{sel}", type="primary", use_container_width=True):
                    st.session_state.action_taken[sel] = "send";       st.rerun()
                if st.button("Demander infos", key=f"info_{sel}",  use_container_width=True):
                    st.session_state.action_taken[sel] = "request_info"; st.rerun()
            with bb:
                if st.button("Escalader",      key=f"esc_{sel}",  use_container_width=True):
                    st.session_state.action_taken[sel] = "escalate";   st.rerun()
                if st.button("Rejeter",        key=f"rej_{sel}",  use_container_width=True):
                    st.session_state.action_taken[sel] = "reject";     st.rerun()

        if errors:
            for err in errors:
                st.error(err)

st.markdown('</div>', unsafe_allow_html=True)