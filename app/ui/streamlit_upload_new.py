"""
streamlit_upload.py
Page Streamlit — Upload & traitement d'evenements JSON clients
Saves uploaded files into the correct data/events/ subfolder based on channel.
"""

import json
import time
import traceback
from pathlib import Path
from datetime import datetime

import streamlit as st

# -- Import du workflow existant -----------------------------------------------
try:
    from app.graph.workflow import build_graph
    from app.graph.state import AgentState
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False

# -- Folder routing map --------------------------------------------------------
# Maps the "channel" field value -> relative path inside data/events/
CHANNEL_TO_FOLDER: dict[str, str] = {
    "email_claim":   "data/events/email_claim",
    "email_general": "data/events/email_general",
    "form":          "data/events/forms",
    "call":          "data/events/calls",
}

# Root of the project (2 levels up from app/ui/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_folder(channel: str) -> Path | None:
    """Returns the absolute path of the target folder for a given channel."""
    relative = CHANNEL_TO_FOLDER.get(channel)
    if relative is None:
        return None
    folder = PROJECT_ROOT / relative
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_event_to_folder(filename: str, event: dict) -> tuple[bool, str]:
    """
    Saves the event JSON into the correct data/events/ subfolder.
    Returns (success, message).
    """
    channel = event.get("channel", "")
    folder = resolve_folder(channel)

    if folder is None:
        return False, (
            f"Unknown channel '{channel}'. "
            f"Expected one of: {list(CHANNEL_TO_FOLDER.keys())}"
        )

    # Avoid overwriting: append timestamp suffix if file already exists
    dest = folder / filename
    if dest.exists():
        stem   = Path(filename).stem
        suffix = Path(filename).suffix
        ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest   = folder / f"{stem}_{ts}{suffix}"

    dest.write_text(json.dumps(event, ensure_ascii=False, indent=2))
    return True, str(dest.relative_to(PROJECT_ROOT))


# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="Customer Service - Upload JSON",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .main-title {
    font-size: 1.8rem; font-weight: 800;
    letter-spacing: -0.02em; margin-bottom: 4px;
  }
  .sub-title { color: #6B7280; font-size: 0.92rem; margin-bottom: 24px; }

  .step-badge {
    display: inline-block; padding: 2px 9px;
    border-radius: 100px; font-size: 0.72rem;
    font-weight: 600; letter-spacing: 0.05em; margin-right: 4px;
  }
  .badge-auto  { background:#DBEAFE; color:#1D4ED8; }
  .badge-ia    { background:#EDE9FE; color:#6D28D9; }
  .badge-human { background:#FEF3C7; color:#92400E; }
  .badge-save  { background:#D1FAE5; color:#065F46; }
  .badge-error { background:#FEE2E2; color:#991B1B; }

  .folder-tag {
    font-family: monospace; font-size: 0.82rem;
    background: #F3F4F6; padding: 2px 8px;
    border-radius: 6px; color: #374151;
  }
  .saved-path {
    font-family: monospace; font-size: 0.8rem;
    background: #ECFDF5; padding: 4px 10px;
    border-radius: 6px; color: #065F46;
    border: 1px solid #A7F3D0;
  }
</style>
""", unsafe_allow_html=True)


# -- Helpers -------------------------------------------------------------------

def load_json(file) -> dict:
    try:
        return json.loads(file.read())
    except json.JSONDecodeError as e:
        return {"_error": str(e), "_filename": file.name}


def validate_schema(event: dict) -> tuple[bool, list[str]]:
    errors = []
    for field in ["event_id", "channel", "timestamp"]:
        if field not in event:
            errors.append(f"Missing required field: `{field}`")
    channel = event.get("channel", "")
    if channel and channel not in CHANNEL_TO_FOLDER:
        errors.append(
            f"Unknown channel `{channel}`. "
            f"Expected: {list(CHANNEL_TO_FOLDER.keys())}"
        )
    return len(errors) == 0, errors


def run_workflow(event: dict) -> dict:
    if WORKFLOW_AVAILABLE:
        graph = build_graph()
        state: AgentState = {
            "event": event,
            "ticket_id": None,
            "customer_data": None,
            "classification": None,
            "draft_response": None,
            "validation_status": None,
            "audit_log": [],
            "errors": [],
        }
        return graph.invoke(state)
    return _demo_run(event)


def _demo_run(event: dict) -> dict:
    time.sleep(0.3)
    intent = event.get("intent", "reclamation_colis")
    score  = 0.84
    return {
        "_demo": True,
        "event_id":  event.get("event_id"),
        "channel":   event.get("channel"),
        "classification":   {"intent": intent, "confidence": score},
        "draft_response": (
            f"Bonjour, suite a votre demande concernant '{intent}', "
            "nous avons bien pris en compte votre dossier et revenons vers vous sous 24h."
        ),
        "validation_status": "pending_human",
        "steps": [
            {"step": "INGESTION",           "status": "ok", "detail": f"event_id={event.get('event_id')}"},
            {"step": "NORMALISATION",       "status": "ok", "detail": "Schema valide"},
            {"step": "ROUTAGE",             "status": "ok", "detail": f"Canal -> {event.get('channel')}"},
            {"step": "CLASSIFICATION IA",   "status": "ok", "detail": f"Intent: {intent} ({score:.0%})"},
            {"step": "ENRICHISSEMENT",      "status": "ok", "detail": "CRM + tracking injectes"},
            {"step": "SCORING",             "status": "ok", "detail": f"Confiance: {score:.0%}"},
            {"step": "REDACTION BROUILLON", "status": "ok", "detail": "Brouillon genere"},
        ],
        "audit_log": [f"[{datetime.now().isoformat()}] Demo workflow OK"],
    }


def render_result(filename: str, saved_path: str | None, result: dict, idx: int):
    is_error = "_error" in result
    label = "Error" if is_error else result.get("validation_status", "processed")

    with st.expander(f"  {filename}  —  {label}", expanded=(idx == 0)):

        if saved_path:
            st.markdown(
                f'Saved to <span class="saved-path">{saved_path}</span>',
                unsafe_allow_html=True,
            )
            st.divider()

        if is_error:
            st.error(result["_error"])
            if "_traceback" in result:
                with st.expander("Traceback"):
                    st.code(result["_traceback"])
            return

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Event info**")
            classification = result.get("classification") or {}
            for k, v in {
                "Event ID":   result.get("event_id", "—"),
                "Channel":    result.get("channel", "—"),
                "Intent":     classification.get("intent", "—"),
                "Confidence": f"{classification.get('confidence', 0):.0%}" if classification else "—",
                "Status":     result.get("validation_status", "—"),
            }.items():
                st.markdown(f"- **{k}** : `{v}`")

        with col2:
            st.markdown("**Draft response**")
            draft = result.get("draft_response", "")
            if draft:
                st.info(draft[:300] + ("…" if len(draft) > 300 else ""))
            else:
                st.caption("No draft generated.")

        if result.get("steps"):
            st.markdown("**Pipeline steps**")
            for s in result["steps"]:
                badge = "badge-save" if s["status"] == "ok" else "badge-error"
                st.markdown(
                    f'<span class="step-badge {badge}">{s["step"]}</span> {s["detail"]}',
                    unsafe_allow_html=True,
                )

        if result.get("audit_log"):
            with st.expander("Audit log"):
                for entry in result["audit_log"]:
                    st.code(entry)

        with st.expander("Raw JSON result"):
            st.json(result)


# -- Main ----------------------------------------------------------------------

def main():
    st.markdown('<div class="main-title">Customer Service · Simulation: Event Upload</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">'
        'Upload JSON events — each file is automatically saved to the correct '
        '<code>data/events/</code> subfolder based on its <code>channel</code> field.'
        '</div>',
        unsafe_allow_html=True,
    )

    if not WORKFLOW_AVAILABLE:
        st.warning(
            "**Demo mode** — Ceci est juste pour une simulation de l'arrivée d'un évènement, ceci ne sera pas vu par le conseiller.",
        )

    # -- Sidebar ---------------------------------------------------------------
    with st.sidebar:
        st.markdown("### Options")
        max_files       = st.number_input("Max files per run", 1, 50, 5)
        validate_before = st.toggle("Validate schema before saving", value=True)
        run_pipeline    = st.toggle("Run pipeline after saving",     value=True)
        stop_on_error   = st.toggle("Stop on first error",           value=False)
        show_raw_input  = st.toggle("Show uploaded JSON",            value=False)

        st.divider()
        st.markdown("### Folder routing")
        st.caption("Each file is routed based on its `channel` field:")
        for channel, folder in CHANNEL_TO_FOLDER.items():
            st.markdown(
                f'`{channel}`<br><span class="folder-tag">{folder}/</span>',
                unsafe_allow_html=True,
            )
            st.markdown("")

        st.divider()
        st.markdown("### Pipeline steps")
        for badge, label in [
            ( "auto",  "Ingestion & Routing"),
            ("ia",    "AI Classification"),
            ( "auto",  "Enrichment"),
            ( "ia",    "Scoring / Decision"),
            ( "auto",  "Draft generation"),
            ( "human", "Human validation"),
        ]:
            badge_cls = f"badge-{'ia' if badge=='ia' else 'human' if badge=='human' else 'auto'}"
            st.markdown(
                f' <span class="step-badge {badge_cls}">{badge.upper()}</span> {label}',
                unsafe_allow_html=True,
            )

    # -- Upload zone -----------------------------------------------------------
    st.markdown("### Upload JSON files")
    uploaded = st.file_uploader(
        f"Drop your .json files here (max {int(max_files)})",
        type=["json"],
        accept_multiple_files=True,
    )

    if not uploaded:
        st.info("Upload one or more `.json` event files to get started.")
        with st.expander("Expected JSON schema"):
            st.json({
                "event_id":    "EVT-001",
                "channel":     "email_claim",
                "timestamp":   "2024-01-15T10:30:00Z",
                "customer_id": "CUST-456",
                "subject":     "Missing parcel",
                "body":        "Hello, my order from 10/01 has not arrived yet...",
            })
        with st.expander("Channel -> folder mapping"):
            for ch, folder in CHANNEL_TO_FOLDER.items():
                st.markdown(f"- `{ch}` → `{folder}/`")
        return

    files  = list(uploaded)[:int(max_files)]
    events: list[tuple[str, dict]] = [(f.name, load_json(f)) for f in files]

    c1, c2, c3 = st.columns(3)
    c1.metric("Files loaded",       len(events))
    c2.metric("Schema validation",  "ON" if validate_before else "OFF")
    c3.metric("Run pipeline",       "ON" if run_pipeline    else "OFF")

    if show_raw_input:
        st.markdown("#### Uploaded files")
        for name, data in events:
            with st.expander(f"{name}"):
                st.json(data)

    st.divider()

    # -- Process button --------------------------------------------------------
    if st.button("Save & Process", type="primary", use_container_width=True):
        st.markdown(" Results")
        progress = st.progress(0, text="Starting…")
        summary  = {"saved": 0, "error": 0}

        for i, (fname, event) in enumerate(events):
            progress.progress(int(i / len(events) * 100), text=f"Processing `{fname}`…")

            # 1. Catch JSON parse errors from load step
            if "_error" in event:
                render_result(fname, None, event, i)
                summary["error"] += 1
                if stop_on_error:
                    break
                continue

            # 2. Schema validation
            if validate_before:
                ok, errs = validate_schema(event)
                if not ok:
                    render_result(
                        fname, None,
                        {"_error": "Schema invalid:\n" + "\n".join(errs)},
                        i,
                    )
                    summary["error"] += 1
                    if stop_on_error:
                        st.error("Stopped on first error.")
                        break
                    continue

            # 3. Save to correct folder
            ok, msg = save_event_to_folder(fname, event)
            if not ok:
                render_result(fname, None, {"_error": f"Save failed: {msg}"}, i)
                summary["error"] += 1
                if stop_on_error:
                    st.error("Stopped on first error.")
                    break
                continue
            saved_path = msg
            summary["saved"] += 1

            # 4. Run pipeline (optional)
            result: dict = {}
            if run_pipeline:
                try:
                    result = run_workflow(event)
                except Exception as e:
                    result = {"_error": str(e), "_traceback": traceback.format_exc()}
                    summary["error"] += 1

            render_result(fname, saved_path, result, i)

        progress.progress(100, text="Done ✓")

        # Summary
        st.divider()
        st.markdown("### Summary")
        s1, s2 = st.columns(2)
        s1.metric("Saved & processed", summary["saved"])
        s2.metric("Errors",            summary["error"])

        if summary["error"] == 0:
            st.success("All files saved successfully.")
        else:
            st.warning(f"{summary['error']} file(s) had errors — see details above.")


if __name__ == "__main__":
    main()
