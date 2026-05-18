""" 
Interface Conseiller La Poste — Dashboard IA (Thème clair eKonsilio-style)
app/ui/streamlit_app.py
streamlit run app/ui/streamlit_app.py

DYNAMIC LOADING: demands are read live from data/events/**/*.json
so any file saved by streamlit_upload.py appears instantly.
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
section.main > div { padding-left: 0 !important; padding-right: 0 !important; padding-top: 0 !important; }
[data-testid="stAppViewContainer"] > section { padding: 0 !important; }

.shell { display: flex; min-height: 100vh; background: #F4F6FA; }

.nav {
    width: 56px; background: #1C1C2E;
    display: flex; flex-direction: column; align-items: center;
    padding: 18px 0; gap: 6px;
    position: fixed; top: 0; left: 0; bottom: 0; z-index: 1000;
}
[data-testid="stAppViewContainer"] { padding-left: 56px !important; }
[data-testid="stHeader"] { padding-left: 56px !important; }
.nav-logo {
    width: 34px; height: 34px; background: #FFFFFF18;
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1rem; margin-bottom: 14px; border: 1px solid #ffffff22;
}
.nav-item {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; cursor: pointer; color: #6B7A99; transition: all 0.15s;
}
.nav-item.active { background: #2E2E4A; color: #FFFFFF; }
.nav-item:hover:not(.active) { background: #25253A; color: #aaa; }
.nav-bottom { margin-top: auto; }
.nav-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #6C63FF, #48B0F7);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; color: #fff; margin-top: 14px;
}

.topbar {
    height: 62px; background: #FFFFFF; border-bottom: 1px solid #E8ECF4;
    display: flex; align-items: center; padding: 0 28px; gap: 20px;
    position: sticky; top: 0; z-index: 50; box-shadow: 0 1px 0 #E8ECF4;
}
.topbar-greeting { flex: 1; }
.topbar-greeting-name { font-size: 1rem; font-weight: 700; color: #1C1C2E; }
.topbar-greeting-sub  { font-size: 0.75rem; color: #9AA3B5; font-weight: 400; margin-top: 1px; }
.topbar-tabs { display: flex; gap: 0; }
.topbar-tab {
    padding: 6px 14px; font-size: 0.78rem; font-weight: 500; color: #9AA3B5;
    border-bottom: 2px solid transparent; cursor: pointer; white-space: nowrap;
    display: flex; align-items: center; gap: 6px;
}
.topbar-tab.active { color: #1C1C2E; border-bottom-color: #1C1C2E; }
.topbar-right { display: flex; align-items: center; gap: 10px; margin-left: auto; }

.page { padding: 28px; }

.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.kpi-card {
    background: #FFFFFF; border: 1px solid #E8ECF4; border-radius: 14px;
    padding: 20px 22px; display: flex; flex-direction: column; gap: 2px;
}
.kpi-label { font-size: 0.72rem; color: #9AA3B5; font-weight: 500; margin-bottom: 6px; }
.kpi-value { font-size: 2rem; font-weight: 700; color: #1C1C2E; line-height: 1; }
.kpi-sub   { font-size: 0.73rem; color: #B0B8CC; margin-top: 4px; }
.kpi-up    { color: #22C55E !important; }

.kpi-time-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.kpi-time-card { background: #FFFFFF; border: 1px solid #E8ECF4; border-radius: 14px; padding: 18px 20px; }
.kpi-time-label { font-size: 0.72rem; color: #9AA3B5; font-weight: 500; margin-bottom: 8px; }
.kpi-time-value { font-size: 1.65rem; font-weight: 700; color: #1C1C2E; }

.agents-panel {
    width: 220px; background: #FFFFFF; border: 1px solid #E8ECF4;
    border-radius: 14px; padding: 14px; flex-shrink: 0;
}
.agents-title {
    font-size: 0.7rem; font-weight: 600; color: #9AA3B5;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;
}
.agent-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0; border-bottom: 1px solid #F0F2F8;
}
.agent-row:last-child { border-bottom: none; }
.agent-avatar {
    width: 30px; height: 30px; border-radius: 50%; background: #E8ECF4;
    flex-shrink: 0; display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: #6B7A99;
}
.agent-name  { font-size: 0.77rem; font-weight: 500; color: #1C1C2E; flex: 1; }
.agent-count { font-size: 0.75rem; font-weight: 600; color: #9AA3B5; }
.dot-green { width: 7px; height: 7px; border-radius: 50%; background: #22C55E; flex-shrink: 0; }
.dot-red   { width: 7px; height: 7px; border-radius: 50%; background: #EF4444; flex-shrink: 0; }

.section-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #B0B8CC; margin: 0 0 12px;
}

.new-badge {
    display: inline-block; padding: 2px 7px; border-radius: 20px;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.06em;
    background: #6C63FF; color: #fff; margin-left: 6px;
    vertical-align: middle;
}

.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 20px; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.03em; }
.badge-orange { background: #FFF4E0; color: #D97706; border: 1px solid #FDDBA0; }
.badge-red    { background: #FEF0F0; color: #EF4444; border: 1px solid #FCCACA; }
.badge-green  { background: #EDFAF3; color: #16A34A; border: 1px solid #A7F3C7; }
.badge-blue   { background: #EFF6FF; color: #3B82F6; border: 1px solid #BFDBFE; }
.badge-purple { background: #F5F3FF; color: #7C3AED; border: 1px solid #DDD6FE; }
.badge-grey   { background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }
.chan { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 6px; font-size: 0.7rem; font-weight: 500; background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }

.detail-panel { background: #FFFFFF; border: 1px solid #E8ECF4; border-radius: 14px; margin-bottom: 14px; overflow: hidden; }
.dp-header { padding: 14px 18px 12px; border-bottom: 1px solid #F0F2F8; }
.dp-name { font-size: 0.85rem; font-weight: 600; color: #1C1C2E; }
.dp-meta { font-size: 0.7rem; color: #B0B8CC; margin-top: 2px; }
.dp-body { padding: 14px 18px; }
.msg-bubble {
    background: #F7F8FC; border: 1px solid #E8ECF4; border-left: 3px solid #6C63FF;
    border-radius: 0 8px 8px 0; padding: 12px 14px;
    font-size: 0.82rem; color: #4B5A72; line-height: 1.65; margin-bottom: 10px; white-space: pre-wrap;
}
.info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #F0F2F8; font-size: 0.79rem; }
.info-row:last-child { border-bottom: none; }
.info-key { color: #9AA3B5; }
.info-val { color: #1C1C2E; font-weight: 500; text-align: right; max-width: 60%; }
.esc-banner { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 10px 14px; font-size: 0.8rem; color: #D97706; margin-bottom: 14px; }
.esc-banner.critical { background: #FEF2F2; border-color: #FECACA; color: #EF4444; }
.draft-label { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #B0B8CC; margin-bottom: 6px; }

textarea {
    background: #F7F8FC !important; color: #1C1C2E !important;
    border: 1px solid #E8ECF4 !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.82rem !important;
}
.stButton > button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important; font-weight: 600 !important; padding: 7px 14px !important;
    transition: all 0.15s !important; border: 1px solid #E8ECF4 !important;
    background: #FFFFFF !important; color: #1C1C2E !important;
}
.stButton > button[kind="primary"] { background: #1C1C2E !important; color: #FFFFFF !important; border-color: #1C1C2E !important; }
.stButton > button:hover { background: #F7F8FC !important; }
.stButton > button[kind="primary"]:hover { background: #2E2E4A !important; }
div[data-testid="stHorizontalBlock"] { gap: 8px; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #E0E4EE; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC DEMAND LOADING
# Reads all JSON files from data/events/**/*.json at runtime.
# New files saved by streamlit_upload.py appear automatically.
# ══════════════════════════════════════════════════════════════════════════════

CHANNEL_ICON  = {"email_claim": "✉️", "email_general": "📧", "form": "📋", "call": "📞"}
CHANNEL_LABEL = {"email_claim": "Email réclamation", "email_general": "Email général", "form": "Formulaire", "call": "Appel"}

PRIORITY_BADGE = {
    "critical": ("badge-red",    "Critique"),
    "high":     ("badge-orange", "Haute"),
    "normal":   ("badge-blue",   "Normale"),
    "low":      ("badge-grey",   "Basse"),
}
STATUS_BADGE = {
    "en attente": ("badge-orange", "En attente"),
    "escalade":   ("badge-red",    "Escalade"),
    "traite":     ("badge-green",  "Traité"),
    "en cours":   ("badge-blue",   "En cours"),
}

# IDs that were already present before this session started
# (used to mark newly uploaded files with a "NEW" badge)
_KNOWN_AT_STARTUP = set()


@st.cache_data(ttl=2)          # re-scan disk every 2 seconds
def load_all_demands() -> list[dict]:
    """
    Scans data/events/**/*.json and builds the demand list dynamically.
    Falls back gracefully if a field is missing.
    """
    events_root = ROOT / "data" / "events"
    demands: list[dict] = []

    folder_to_channel = {
        "email_claim":   "email_claim",
        "email_general": "email_general",
        "forms":         "form",
        "calls":         "call",
    }

    for json_file in sorted(events_root.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            raw = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        # Derive channel from folder name if not in JSON
        folder_name = json_file.parent.name
        channel = raw.get("channel") or folder_to_channel.get(folder_name, "email_general")

        # Build a unique id from the file stem
        demand_id = json_file.stem

        # Heuristics for priority / status (override with JSON fields when present)
        priority = raw.get("priority", "normal")
        if raw.get("urgent") or raw.get("is_critical"):
            priority = "critical"

        status = raw.get("status", "en attente")

        # mtime for "new" detection (files modified in last 60s)
        mtime = json_file.stat().st_mtime
        is_new = (datetime.now().timestamp() - mtime) < 60

        demands.append({
            "id":          demand_id,
            "file_path":   str(json_file.relative_to(ROOT)),
            "from_name":   raw.get("customer_name")  or raw.get("from_name") or "Inconnu",
            "from_email":  raw.get("customer_email") or raw.get("from_email") or "",
            "subject":     raw.get("subject", "(sans objet)"),
            "channel":     channel,
            "category":    raw.get("category") or raw.get("intent") or "—",
            "priority":    priority,
            "status":      status,
            "segment":     raw.get("segment", "standard"),
            "escalate":    raw.get("should_escalate", False) or raw.get("escalate", False),
            "escalate_to": raw.get("escalate_to", ""),
            "ticket":      raw.get("should_create_ticket", False) or raw.get("ticket", False),
            "confidence":  raw.get("confidence", 0.0),
            "date":        raw.get("timestamp", "")[:10] or datetime.fromtimestamp(mtime).strftime("%d/%m"),
            "time":        raw.get("timestamp", "")[11:16] or datetime.fromtimestamp(mtime).strftime("%H:%M"),
            "is_new":      is_new,
            "_raw":        raw,
        })

    return demands


def load_event_by_id(demand: dict) -> dict:
    path = ROOT / demand["file_path"]
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return demand.get("_raw", {})


MOCK_AGENTS = [
    {"name": "Alice Morel",    "dot": "dot-green", "count": 1},
    {"name": "Théo Vannier",   "dot": "dot-green", "count": 3},
    {"name": "Lucie Bernard",  "dot": "dot-green", "count": 2},
    {"name": "Marc Dupont",    "dot": "dot-red",   "count": 7},
    {"name": "Julie Fontaine", "dot": "dot-red",   "count": 5},
]


def run_graph(event: dict) -> dict:
    from app.graph.workflow import graph
    initial = {
        "event_id":        event.get("event_id", "evt_ui"),
        "timestamp":       event.get("timestamp", datetime.now().isoformat()),
        "channel":         event.get("channel", "email_general"),
        "current_step":    "start",
        "customer_email":  event.get("customer_email", ""),
        "subject":         event.get("subject", ""),
        "body":            event.get("body", ""),
        "customer_context":  None,
        "customer_history":  None,
        "should_create_ticket":   False,
        "ticket_creation_reason": "",
        "rag_documents":  [],
        "rag_sources":    [],
        "draft_response": None,
        "request_subject": "",
        "should_escalate":  False,
        "escalate_reason":  "",
        "escalate_to":      None,
        "audit_log": [],
        "errors":    [],
    }
    return graph.invoke(initial)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("selected_id",   None),
    ("wf_results",    {}),
    ("action_taken",  {}),
    ("edited_drafts", {}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# NAV
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
    <div class="nav-bottom"><div class="nav-avatar">FC</div></div>
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
            <div class="topbar-greeting-name">Bonjour fast &amp; curious</div>
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

    # ── Load demands live from disk ───────────────────────────────────────────
    demands = load_all_demands()

    total      = len(demands)
    en_attente = sum(1 for d in demands if d["status"] == "en attente")
    escalades  = sum(1 for d in demands if d["escalate"])
    traites    = sum(1 for d in demands if d["status"] in ("traite", "traité"))
    new_count  = sum(1 for d in demands if d["is_new"])

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

        # ── Refresh button ────────────────────────────────────────────────────
        st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
        if st.button("🔄 Rafraîchir", use_container_width=True, key="refresh_btn"):
            load_all_demands.clear()   # bust the @st.cache_data cache
            st.rerun()
        if new_count:
            st.markdown(
                f'<div style="text-align:center;font-size:0.72rem;color:#6C63FF;margin-top:6px">'
                f'✨ {new_count} nouvelle(s) demande(s)</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">Conversations</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-sub kpi-up">+{new_count} depuis dernier refresh</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">En attente</div>
                <div class="kpi-value" style="color:#D97706">{en_attente}</div>
                <div class="kpi-sub">Réponse requise</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Taux de traitement</div>
                <div class="kpi-value" style="color:#16A34A">{int(traites/total*100) if total else 0}%</div>
                <div class="kpi-sub kpi-up">{traites} traitées sur {total}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

        st.markdown(
            f'<p class="section-title">Toutes les demandes — {total} au total'
            f'{"  <span class=\'new-badge\'>NEW +" + str(new_count) + "</span>" if new_count else ""}</p>',
            unsafe_allow_html=True,
        )

        # Header row
        st.markdown("""
        <div style="display:grid;grid-template-columns:2fr 1.6fr 1fr 1fr 1fr 80px;
                    padding:10px 20px;background:#fff;border:1px solid #E8ECF4;
                    border-radius:14px 14px 0 0;
                    font-size:0.65rem;font-weight:600;letter-spacing:0.08em;
                    text-transform:uppercase;color:#B0B8CC;">
            <span>Expéditeur</span>
            <span>Catégorie / Sujet</span>
            <span>Canal</span>
            <span>Priorité</span>
            <span>Statut</span>
            <span>Date</span>
        </div>
        """, unsafe_allow_html=True)

        for i, d in enumerate(demands):
            p_cls, p_lbl = PRIORITY_BADGE.get(d["priority"], ("badge-grey", d["priority"]))
            s_cls, s_lbl = STATUS_BADGE.get(d["status"],   ("badge-grey", d["status"]))
            cl            = CHANNEL_LABEL.get(d["channel"], d["channel"])
            is_last       = (i == len(demands) - 1)
            radius        = "0 0 14px 14px" if is_last else "0"

            new_tag  = '<span class="new-badge">NEW</span>' if d["is_new"] else ""
            seg_tag  = ' <span style="font-size:0.6rem;color:#7C3AED;background:#F5F3FF;border:1px solid #DDD6FE;border-radius:20px;padding:2px 7px;margin-left:5px">PREMIUM</span>' if d["segment"] == "premium" else ""
            esc_tag  = ' <span style="color:#EF4444;font-size:0.75rem;font-weight:700"> !</span>' if d["escalate"] else ""

            # Clickable row via button
            if st.button(f"→ {d['from_name']} · {d['subject'][:50]}", key=f"btn_{d['id']}_{i}", use_container_width=True):
                st.session_state.selected_id = d["id"]
                st.session_state["selected_demand"] = d
                st.rerun()

            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E8ECF4;border-top:none;
                        padding:12px 20px;border-radius:{radius};
                        display:grid;grid-template-columns:2fr 1.6fr 1fr 1fr 1fr 80px;
                        align-items:center;margin-top:-44px;pointer-events:none;
                        border-bottom:1px solid {'transparent' if is_last else '#F7F8FC'}">
                <div>
                    <div style="font-size:0.83rem;font-weight:600;color:#1C1C2E">
                        {d['from_name']}{seg_tag}{esc_tag}{new_tag}
                    </div>
                    <div style="font-size:0.71rem;color:#B0B8CC;margin-top:2px">{d['from_email']}</div>
                </div>
                <div>
                    <div style="font-size:0.76rem;color:#6B7A99">{d['category']}</div>
                    <div style="font-size:0.71rem;color:#B0B8CC;margin-top:2px">{d['subject'][:42]}{'…' if len(d['subject'])>42 else ''}</div>
                </div>
                <div><span class="chan">{cl}</span></div>
                <div><span class="badge {p_cls}">{p_lbl}</span></div>
                <div><span class="badge {s_cls}">{s_lbl}</span></div>
                <div style="font-size:0.73rem;color:#B0B8CC;font-family:'DM Mono',monospace">{d['date']}<br>{d['time']}</div>
            </div>
            """, unsafe_allow_html=True)

        if not demands:
            st.info("Aucune demande trouvée dans data/events/. Uploadez des fichiers JSON via la page Upload.")

# ══════════════════════════════════════════════════════════════════════════════
# DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════════
else:
    # Retrieve the demand object (by id from the live list)
    demands = load_all_demands()
    demand  = st.session_state.get("selected_demand") or next(
        (d for d in demands if d["id"] == sel), None
    )
    if not demand:
        st.session_state.selected_id = None
        st.rerun()

    if st.button("← Retour au dashboard"):
        st.session_state.selected_id = None
        st.rerun()

    if sel not in st.session_state.wf_results:
        ev = load_event_by_id(demand)
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
    event  = load_event_by_id(demand)
    draft  = result.get("draft_response")
    ctx    = result.get("customer_context")
    hist   = result.get("customer_history") or {}
    errors = result.get("errors", [])

    p_cls, p_lbl = PRIORITY_BADGE.get(demand["priority"], ("badge-grey", demand["priority"]))
    s_cls, s_lbl = STATUS_BADGE.get(demand["status"],    ("badge-grey", demand["status"]))
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
        dest   = result.get("escalate_to", "superviseur")
        reason = result.get("escalate_reason", "")
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
                    <div style="font-size:0.9rem;font-weight:600;color:#1C1C2E;margin-bottom:8px">
                        {ctx.name} <span class="badge" style="background:#FFF4E0;color:{ic};border:1px solid #FDDBA0;font-size:0.6rem">{ctx.segment.upper()}</span>
                    </div>
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
        req_sub = result.get("request_subject") or "—"
        sources = result.get("rag_sources", [])

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
            if action_done == "send":           st.success("Réponse envoyée · Ticket mis à jour")
            elif action_done == "escalate":     st.warning(f"Transmis → **{result.get('escalate_to','superviseur').upper()}**")
            elif action_done == "request_info": st.info("Demande d'infos envoyée au client")
            elif action_done == "reject":       st.error("Brouillon rejeté")
            if st.button("Réinitialiser", key=f"rst_{sel}"):
                st.session_state.action_taken.pop(sel, None)
                st.rerun()
        else:
            if draft:
                edited = st.text_area(
                    "Brouillon",
                    value=st.session_state.edited_drafts.get(sel, draft.body),
                    height=210, label_visibility="collapsed", key=f"draft_{sel}",
                )
                st.session_state.edited_drafts[sel] = edited
            else:
                st.markdown('<div style="color:#B0B8CC;font-size:0.8rem;padding:10px 0">Aucun brouillon généré.</div>', unsafe_allow_html=True)

            ba, bb = st.columns(2)
            with ba:
                if st.button("Envoyer",        key=f"send_{sel}", type="primary", use_container_width=True):
                    st.session_state.action_taken[sel] = "send";        st.rerun()
                if st.button("Demander infos", key=f"info_{sel}",       use_container_width=True):
                    st.session_state.action_taken[sel] = "request_info"; st.rerun()
            with bb:
                if st.button("Escalader",      key=f"esc_{sel}",        use_container_width=True):
                    st.session_state.action_taken[sel] = "escalate";    st.rerun()
                if st.button("Rejeter",        key=f"rej_{sel}",        use_container_width=True):
                    st.session_state.action_taken[sel] = "reject";      st.rerun()

        if errors:
            for err in errors:
                st.error(err)

st.markdown('</div>', unsafe_allow_html=True)
