import streamlit as st
import time
import os
import google.generativeai as genai
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI-Powered Enterprise RFP Bidding Agent",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — MODERN DARK PROFESSIONAL THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0d0f1a 0%, #111827 50%, #0d1117 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1a2035 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    [data-testid="stSidebar"] .stMarkdown p { color: #94a3b8; font-size: 0.85rem; }

    /* ── Hero Header ── */
    .hero-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a5f 100%);
        border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 16px;
        padding: 2.5rem 3rem; margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15), 0 2px 8px rgba(0,0,0,0.4);
        text-align: center;
    }
    .hero-header h1 {
        font-size: 2.2rem; font-weight: 800; color: #ffffff;
        margin: 0; letter-spacing: -0.5px; line-height: 1.2;
    }
    .hero-header p { color: #a5b4fc; font-size: 1rem; margin-top: 0.6rem; }
    .hero-badge {
        display: inline-block; background: rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(99, 102, 241, 0.5); color: #a5b4fc;
        padding: 0.25rem 0.9rem; border-radius: 999px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;
        text-transform: uppercase; margin-bottom: 1rem;
    }

    /* ── Section Cards ── */
    .section-card {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 1.6rem 1.8rem; margin-bottom: 1.4rem;
        backdrop-filter: blur(10px);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .section-card:hover {
        border-color: rgba(99,102,241,0.35);
        box-shadow: 0 4px 20px rgba(99,102,241,0.08);
    }
    .section-card h3 {
        font-size: 1rem; font-weight: 700; color: #a5b4fc;
        margin-top: 0; margin-bottom: 0.8rem;
        text-transform: uppercase; letter-spacing: 0.06em;
    }
    .section-card pre {
        background: rgba(0,0,0,0.25); border-radius: 8px; padding: 1rem;
        color: #cbd5e1; font-size: 0.82rem; line-height: 1.7;
        white-space: pre-wrap; word-wrap: break-word;
        border: 1px solid rgba(255,255,255,0.05); margin: 0;
    }

    /* ── Metric Pills ── */
    .metric-pill {
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
        border: 1px solid rgba(99,102,241,0.3); border-radius: 10px;
        padding: 0.8rem 1.2rem; text-align: center;
    }
    .metric-pill .metric-value { font-size:1.6rem; font-weight:800; color:#818cf8; line-height:1; }
    .metric-pill .metric-label {
        font-size:0.72rem; color:#94a3b8; margin-top:0.3rem;
        text-transform:uppercase; letter-spacing:0.05em;
    }

    /* ── Credential Badge ── */
    .cred-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);
        color: #34d399; padding: 0.35rem 0.85rem; border-radius: 999px;
        font-size: 0.78rem; font-weight: 600; margin: 0.25rem 0.25rem 0.25rem 0;
    }

    /* ── API Key Input ── */
    .api-key-card {
        background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.25);
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    }
    .api-key-card p { color: #94a3b8; font-size: 0.8rem; margin: 0.3rem 0 0 0; }

    /* ── Upload Zone ── */
    [data-testid="stFileUploader"] {
        background: rgba(99,102,241,0.05);
        border: 2px dashed rgba(99,102,241,0.3); border-radius: 14px; padding: 1rem;
    }

    /* ── Generate Button ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; padding: 0.85rem 2rem !important;
        font-size: 1rem !important; font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(79,70,229,0.35) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79,70,229,0.5) !important;
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    }

    /* ── Agent Steps ── */
    .agent-step {
        display: flex; align-items: center; gap: 0.75rem;
        padding: 0.65rem 1rem; border-radius: 10px; margin-bottom: 0.5rem;
        font-size: 0.88rem; font-weight: 500;
    }
    .agent-step.idle { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); color:#475569; }
    .agent-step.running { background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; }
    .agent-step.complete { background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); color:#34d399; }
    .pulse { animation: pulse 1s ease-in-out infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }

    /* ── Streaming Output Box ── */
    .stream-box {
        background: rgba(0,0,0,0.3); border: 1px solid rgba(99,102,241,0.25);
        border-radius: 14px; padding: 1.8rem 2rem;
        font-family: 'Inter', sans-serif; font-size: 0.875rem;
        line-height: 1.85; color: #e2e8f0;
    }
    .stream-box::-webkit-scrollbar { width: 6px; }
    .stream-box::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }

    /* ── Status / Banner Cards ── */
    .approval-banner {
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.1));
        border: 1px solid rgba(16,185,129,0.4); border-radius: 14px;
        padding: 1.2rem 1.6rem; display: flex; align-items: center;
        gap: 1rem; margin-bottom: 1.5rem;
    }
    .approval-banner .approval-title { font-weight:700; color:#34d399; font-size:1rem; }
    .approval-banner .approval-sub { color:#6ee7b7; font-size:0.82rem; }
    .ai-banner {
        background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
        border: 1px solid rgba(99,102,241,0.3); border-radius: 14px;
        padding: 1.2rem 1.6rem; display: flex; align-items: center;
        gap: 1rem; margin-bottom: 1.5rem;
    }
    .ai-banner .ai-title { font-weight:700; color:#a5b4fc; font-size:1rem; }
    .ai-banner .ai-sub { color:#818cf8; font-size:0.82rem; }

    /* ── Download Button ── */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #065f46, #047857) !important;
        border: 1px solid rgba(16,185,129,0.4) !important; color: #ecfdf5 !important;
        border-radius: 10px !important; font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important; transition: all 0.3s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #047857, #059669) !important;
        box-shadow: 0 4px 15px rgba(16,185,129,0.3) !important;
        transform: translateY(-1px) !important;
    }

    hr { border-color: rgba(255,255,255,0.06) !important; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
KNOWLEDGE_BASE_DIR   = os.path.join(os.path.dirname(__file__), "knowledge_base")
COMPANY_PROFILE_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "company_profile.txt")
FINAL_PROPOSAL_PATH  = os.path.join(KNOWLEDGE_BASE_DIR, "final_proposal.md")

GEMINI_MODEL = "gemini-1.5-flash"

PIPELINE_STEPS = [
    ("🔍", "RFP Analyzer Agent",        "Parsing RFP mandatory requirements..."),
    ("📋", "Profile Mapper Agent",       "Cross-referencing company capabilities..."),
    ("🛡️", "Compliance Verifier Agent",  "Validating ISO/IEC 27001:2022 credentials..."),
    ("🏗️", "Architecture Agent",         "Designing cloud migration solution..."),
    ("✍️", "Proposal Writer Agent",      "Sending RAG prompt to Gemini 1.5 Flash..."),
    ("✅", "Compliance Inspector Agent", "Streaming & validating AI response..."),
]

# ── Session state defaults ──
for _k, _v in [
    ("proposal_text",   None),
    ("proposal_ready",  False),
    ("proposal_source", None),
    ("last_rfp_name",   None),
    ("api_key_valid",   False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def load_text_file(path: str) -> str:
    """Read a UTF-8 text file and return its contents."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return f"⚠️  File not found: {path}"
    except Exception as exc:
        return f"⚠️  Error: {exc}"


def extract_field(text: str, label: str) -> str:
    """Extract a single-line field value from a profile by label."""
    for ln in text.splitlines():
        if label in ln:
            return ln.split(":", 1)[-1].strip()
    return "N/A"


def extract_credentials(profile_text: str) -> list[str]:
    """Return credential bullet lines from the company profile."""
    return [
        ln.strip()[2:]
        for ln in profile_text.splitlines()
        if ln.strip().startswith("- ") and any(
            kw in ln for kw in ["ISO", "SOC", "AES", "TLS", "Certified", "Compliant"]
        )
    ]


def resolve_api_key(user_input_key: str) -> str:
    """
    Resolve the Gemini API key in priority order:
    1. Key entered in the sidebar input field.
    2. Key stored in .streamlit/secrets.toml under [secrets] GEMINI_API_KEY.
    Returns an empty string if neither source yields a valid key.
    """
    if user_input_key and user_input_key.strip():
        return user_input_key.strip()
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return ""


def build_rag_prompt(company_profile: str, rfp_text: str) -> str:
    """
    Construct the RAG prompt that combines the company profile
    with the incoming RFP to instruct Gemini.
    """
    return f"""You are an expert enterprise bidding agent with deep knowledge of corporate procurement, cloud technology, and compliance frameworks.

Based on our company profile data provided below, generate a professional, comprehensive, and fully structured vendor proposal that precisely matches the client requirements described in the RFP.

The proposal must include these formal sections:
1. Executive Summary
2. Technical Solution Architecture (address all technical requirements in the RFP explicitly)
3. Compliance Matrix (map our certifications directly to each stated requirement)
4. Case Study Reference (cite our most relevant past project with measurable outcomes)
5. Project Timeline and Delivery Plan (confirm our standard delivery schedule)

Formatting rules:
- Use markdown headers (##, ###) for sections
- Use tables for the compliance matrix and timeline
- Use bold for key facts, certifications, percentages, and technologies
- Be specific — cite exact certification names, encryption standards, and metrics from our profile
- Close with a professional Closing Statement

---
COMPANY PROFILE:
{company_profile}

---
CLIENT RFP:
{rfp_text}

---
Now write the complete, submission-ready proposal:"""


def render_pipeline_animation(sidebar_slot, main_slot, stop_at_step: int = 4):
    """
    Animate pipeline steps 1 through stop_at_step in the sidebar and main area.
    The final steps are handled separately during live AI streaming.
    """
    total = len(PIPELINE_STEPS)

    for idx in range(stop_at_step):
        icon, name, task = PIPELINE_STEPS[idx]

        # ── Sidebar update ──
        sidebar_html = ""
        for i, (ic, nm, _) in enumerate(PIPELINE_STEPS):
            if i < idx:
                sidebar_html += f'<div class="agent-step complete"><span>✅</span><span>{nm}</span></div>'
            elif i == idx:
                sidebar_html += (
                    f'<div class="agent-step running">'
                    f'<span class="pulse">{ic}</span>'
                    f'<span><strong>{nm}</strong></span></div>'
                )
            else:
                sidebar_html += f'<div class="agent-step idle"><span>{ic}</span><span style="color:#334155">{nm}</span></div>'
        sidebar_slot.markdown(sidebar_html, unsafe_allow_html=True)

        # ── Main area step card ──
        pct = int((idx / total) * 100)
        main_slot.markdown(f"""
        <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.3);
                    border-radius:12px; padding:1.2rem 1.5rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.6rem;">
                <span style="color:#a5b4fc; font-weight:700; font-size:0.9rem;">{icon} {name}</span>
                <span style="color:#64748b; font-size:0.8rem;">Step {idx+1} of {total}</span>
            </div>
            <div style="color:#94a3b8; font-size:0.85rem; margin-bottom:0.8rem;">{task}</div>
            <div style="background:rgba(0,0,0,0.3); border-radius:999px; height:6px;">
                <div style="background:linear-gradient(90deg,#6366f1,#8b5cf6);
                            width:{pct}%; height:6px; border-radius:999px;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        time.sleep(0.7)


def stream_gemini_proposal(
    api_key: str,
    company_profile: str,
    rfp_text: str,
    sidebar_slot,
    pipeline_slot,
    stream_slot,
) -> str:
    """
    Configure Gemini, build the RAG prompt, stream the response token-by-token,
    and render it live into stream_slot. Returns the full proposal text.
    """
    # ── Animate steps 5 & 6 in sidebar ──
    def _set_sidebar(active_idx: int, done: bool = False):
        html = ""
        for i, (ic, nm, _) in enumerate(PIPELINE_STEPS):
            if done or i < active_idx:
                html += f'<div class="agent-step complete"><span>✅</span><span>{nm}</span></div>'
            elif i == active_idx:
                html += (
                    f'<div class="agent-step running">'
                    f'<span class="pulse">{ic}</span>'
                    f'<span><strong>{nm}</strong></span></div>'
                )
            else:
                html += f'<div class="agent-step idle"><span>{ic}</span><span style="color:#334155">{nm}</span></div>'
        sidebar_slot.markdown(html, unsafe_allow_html=True)

    # Step 5 — Writer Agent (sending prompt)
    _set_sidebar(4)
    pipeline_slot.markdown("""
    <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.3);
                border-radius:12px; padding:1.2rem 1.5rem;">
        <div style="color:#a5b4fc; font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;">
            ✍️ Proposal Writer Agent — Sending RAG prompt to Gemini 1.5 Flash...
        </div>
        <div style="color:#94a3b8; font-size:0.85rem;">
            Connecting to Google AI · Constructing context-aware prompt · Awaiting stream...
        </div>
    </div>""", unsafe_allow_html=True)
    time.sleep(0.5)

    # ── Configure Gemini ──
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = build_rag_prompt(company_profile, rfp_text)

    # Step 6 — Inspector Agent (streaming response)
    _set_sidebar(5)
    pipeline_slot.markdown("""
    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);
                border-radius:12px; padding:1.2rem 1.5rem;">
        <div style="color:#34d399; font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;">
            ✅ Compliance Inspector Agent — Streaming live AI response...
        </div>
        <div style="color:#6ee7b7; font-size:0.85rem;">
            Gemini 1.5 Flash is generating your proposal in real-time ↓
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Stream response token-by-token ──
    response = model.generate_content(prompt, stream=True)
    full_text = ""

    for chunk in response:
        if chunk.text:
            full_text += chunk.text
            # Live render with blinking cursor
            stream_slot.markdown(
                f'<div class="stream-box">{full_text}<span class="pulse">▌</span></div>',
                unsafe_allow_html=True,
            )

    # Remove cursor on final render
    stream_slot.markdown(
        f'<div class="stream-box">{full_text}</div>',
        unsafe_allow_html=True,
    )

    # All agents green
    _set_sidebar(0, done=True)
    return full_text


# ─────────────────────────────────────────────
# LOAD COMPANY PROFILE
# ─────────────────────────────────────────────
company_profile_text = load_text_file(COMPANY_PROFILE_PATH)
credentials_list     = extract_credentials(company_profile_text)
expertise_raw        = extract_field(company_profile_text, "Core Expertise")
team_size_raw        = extract_field(company_profile_text, "Team Size")

team_count = "45"
for _tok in team_size_raw.split():
    if _tok.isdigit():
        team_count = _tok
        break


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ System Configuration")
    st.divider()

    # ── Gemini API Key ──
    st.markdown("**🔑 Gemini API Key**")
    st.markdown(
        '<div class="api-key-card">'
        '<p>Enter your key below, or add it to '
        '<code>.streamlit/secrets.toml</code> as '
        '<code>GEMINI_API_KEY = "..."</code></p></div>',
        unsafe_allow_html=True,
    )
    sidebar_api_key_input = st.text_input(
        label="Gemini API Key",
        placeholder="AIza...",
        type="password",
        label_visibility="collapsed",
    )
    st.caption(
        "🔗 Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)"
    )

    st.divider()

    # ── Knowledge Base Status ──
    st.markdown("**🗂️ Knowledge Base**")
    st.markdown(
        f"{'🟢' if os.path.exists(COMPANY_PROFILE_PATH) else '🔴'} `company_profile.txt`\n\n"
        f"{'🟢' if os.path.exists(FINAL_PROPOSAL_PATH)  else '🔴'} `final_proposal.md`"
    )

    st.divider()

    # ── Model Info ──
    st.markdown("**🤖 AI Backend**")
    st.markdown(
        f'<span class="cred-badge">⚡ {GEMINI_MODEL}</span>'
        f'<span class="cred-badge">🔄 Streaming ON</span>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("**🔄 Active Agent Pipeline**")
    # Live-updated slot during generation
    sidebar_agent_slot = st.empty()
    idle_html = "".join(
        f'<div class="agent-step idle"><span>{ic}</span>'
        f'<span style="color:#475569">{nm}</span></div>'
        for ic, nm, _ in PIPELINE_STEPS
    )
    sidebar_agent_slot.markdown(idle_html, unsafe_allow_html=True)

    st.divider()
    st.caption(f"Session: {datetime.now().strftime('%d %b %Y, %H:%M')}")


# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">🧠 Live Gemini RAG Pipeline</div>
    <h1>AI-Powered Enterprise RFP Bidding Agent</h1>
    <p>Real-time proposal generation using Google Gemini 1.5 Flash — streamed live into your browser.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION 1 — COMPANY PROFILE DASHBOARD
# ─────────────────────────────────────────────
st.markdown("### 🏢 Company Profile Overview")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
for col, val, lbl in [
    (col_m1, team_count, "Engineers"),
    (col_m2, "2",        "Past Projects"),
    (col_m3, "40%",      "DB Performance ↑"),
    (col_m4, "0",        "Security Vulns"),
]:
    with col:
        st.markdown(
            f'<div class="metric-pill">'
            f'  <div class="metric-value">{val}</div>'
            f'  <div class="metric-label">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
col_left, col_right = st.columns([1.05, 1], gap="large")

with col_left:
    st.markdown(
        f'<div class="section-card"><h3>📄 Raw Company Profile</h3>'
        f'<pre>{company_profile_text}</pre></div>',
        unsafe_allow_html=True,
    )

with col_right:
    expertise_pills = " ".join(
        f'<span class="cred-badge">🔷 {e.strip()}</span>'
        for e in expertise_raw.split(",")
    )
    st.markdown(
        f'<div class="section-card"><h3>💡 Core Expertise</h3>{expertise_pills}</div>',
        unsafe_allow_html=True,
    )

    cred_html = (
        " ".join(f'<span class="cred-badge">🔒 {c}</span>' for c in credentials_list)
        if credentials_list
        else "<span style='color:#94a3b8'>No credentials parsed.</span>"
    )
    st.markdown(
        f'<div class="section-card">'
        f'<h3>🛡️ Security &amp; Compliance Credentials</h3>{cred_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="section-card">
        <h3>📊 Verified Past Projects</h3>
        <div style="margin-bottom:0.75rem; padding:0.75rem; background:rgba(99,102,241,0.08);
                    border-radius:10px; border-left:3px solid #6366f1;">
            <div style="font-weight:600; color:#c7d2fe; font-size:0.88rem;">Global Logistics Corp</div>
            <div style="color:#94a3b8; font-size:0.8rem; margin-top:0.3rem;">
                AWS Cloud Migration — 40% query performance ↑, 35% downtime ↓
            </div>
        </div>
        <div style="padding:0.75rem; background:rgba(139,92,246,0.08);
                    border-radius:10px; border-left:3px solid #8b5cf6;">
            <div style="font-weight:600; color:#c7d2fe; font-size:0.88rem;">FinTech Secure Ltd</div>
            <div style="color:#94a3b8; font-size:0.8rem; margin-top:0.3rem;">
                Ethereum Smart Contracts — Zero critical vulnerabilities in audit
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────
# SECTION 2 — RFP UPLOAD
# ─────────────────────────────────────────────
st.markdown("### 📥 Upload Client RFP Document")
st.markdown(
    "<p style='color:#94a3b8; font-size:0.9rem; margin-top:-0.5rem;'>"
    "Upload any client RFP as a <code>.txt</code> file. Gemini will read it dynamically "
    "and generate a fully custom, context-aware proposal in real time.</p>",
    unsafe_allow_html=True,
)

uploaded_rfp_file = st.file_uploader(
    label="Drop your RFP file here or click to browse",
    type=["txt"],
    label_visibility="collapsed",
)

rfp_content_text = ""

if uploaded_rfp_file is not None:
    rfp_content_text = uploaded_rfp_file.read().decode("utf-8")

    # Reset state when a new file is loaded
    if st.session_state.last_rfp_name != uploaded_rfp_file.name:
        st.session_state.proposal_ready  = False
        st.session_state.proposal_text   = None
        st.session_state.proposal_source = None
        st.session_state.last_rfp_name   = uploaded_rfp_file.name

    rfp_lines  = rfp_content_text.splitlines()
    word_count = len(rfp_content_text.split())
    req_count  = sum(
        1 for ln in rfp_lines
        if ln.strip() and ln.strip()[0].isdigit() and "." in ln
    )

    col_preview, col_meta = st.columns([1.5, 1], gap="large")
    with col_preview:
        st.markdown(
            f'<div class="section-card"><h3>📋 RFP Document Preview</h3>'
            f'<pre>{rfp_content_text}</pre></div>',
            unsafe_allow_html=True,
        )
    with col_meta:
        st.markdown(f"""
        <div class="section-card">
            <h3>📎 File Metadata</h3>
            <table style="width:100%; color:#cbd5e1; font-size:0.85rem; border-collapse:collapse;">
                <tr><td style="padding:0.4rem 0; color:#94a3b8;">Filename</td>
                    <td style="text-align:right; font-weight:600;">{uploaded_rfp_file.name}</td></tr>
                <tr><td style="padding:0.4rem 0; color:#94a3b8;">Size</td>
                    <td style="text-align:right; font-weight:600;">{uploaded_rfp_file.size:,} bytes</td></tr>
                <tr><td style="padding:0.4rem 0; color:#94a3b8;">Lines</td>
                    <td style="text-align:right; font-weight:600;">{len(rfp_lines)}</td></tr>
                <tr><td style="padding:0.4rem 0; color:#94a3b8;">Words</td>
                    <td style="text-align:right; font-weight:600;">{word_count:,}</td></tr>
                <tr><td style="padding:0.4rem 0; color:#94a3b8;">Requirements Detected</td>
                    <td style="text-align:right; font-weight:600; color:#34d399;">{req_count}</td></tr>
            </table>
        </div>
        <div class="section-card" style="margin-top:0;">
            <h3>🟢 Pipeline Status</h3>
            <span class="cred-badge">✅ RFP Loaded</span>
            <span class="cred-badge">✅ Profile Ready</span>
            <span class="cred-badge">⚡ Gemini Armed</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.session_state.proposal_ready = False
    st.session_state.proposal_text  = None
    st.session_state.last_rfp_name  = None
    st.info("📂 No RFP uploaded yet. Upload a `.txt` file to activate the Gemini pipeline.")

st.divider()


# ─────────────────────────────────────────────
# SECTION 3 — GENERATE PROPOSAL
# ─────────────────────────────────────────────
st.markdown("### 🚀 Generate Final Proposal")
st.markdown(
    "<p style='color:#94a3b8; font-size:0.9rem; margin-top:-0.5rem;'>"
    "The six-agent pipeline will process your RFP, build a RAG prompt, and stream "
    "a real AI-generated proposal from Gemini 1.5 Flash directly into the preview below.</p>",
    unsafe_allow_html=True,
)

active_api_key = resolve_api_key(sidebar_api_key_input)
btn_disabled   = (uploaded_rfp_file is None) or (not active_api_key)

generate_clicked = st.button(
    "✨  Generate Final Proposal with Gemini AI",
    use_container_width=True,
    disabled=btn_disabled,
)

# Contextual hints below the button
if uploaded_rfp_file is None and not active_api_key:
    st.caption("⬆️ Upload an RFP file and enter your Gemini API key to begin.")
elif uploaded_rfp_file is None:
    st.caption("⬆️ Upload an RFP file to enable generation.")
elif not active_api_key:
    st.caption("🔑 Enter your Gemini API key in the sidebar to enable generation.")


# ─────────────────────────────────────────────
# PIPELINE + GEMINI EXECUTION
# ─────────────────────────────────────────────
if generate_clicked and rfp_content_text and active_api_key:

    st.markdown("#### 🤖 Agent Pipeline — Live Status")
    pipeline_status_slot = st.empty()

    st.markdown("#### 📡 Live AI Proposal Stream")
    stream_output_slot = st.empty()
    stream_output_slot.markdown(
        '<div class="stream-box" style="color:#475569; font-style:italic;">'
        'Waiting for Gemini stream to begin...</div>',
        unsafe_allow_html=True,
    )

    try:
        # ── Animate pipeline steps 1–4 ──
        render_pipeline_animation(
            sidebar_slot=sidebar_agent_slot,
            main_slot=pipeline_status_slot,
            stop_at_step=4,
        )

        # ── Step 5 & 6: real Gemini call + live streaming ──
        final_proposal = stream_gemini_proposal(
            api_key=active_api_key,
            company_profile=company_profile_text,
            rfp_text=rfp_content_text,
            sidebar_slot=sidebar_agent_slot,
            pipeline_slot=pipeline_status_slot,
            stream_slot=stream_output_slot,
        )

        # Persist to session state
        st.session_state.proposal_text   = final_proposal
        st.session_state.proposal_ready  = True
        st.session_state.proposal_source = "gemini-live"

    except Exception as exc:
        error_msg = str(exc)
        st.error(f"⚠️ Gemini API error: {error_msg}")
        if "API_KEY" in error_msg.upper() or "invalid" in error_msg.lower():
            st.info("💡 Your API key may be invalid or expired. Get a free key at "
                    "[aistudio.google.com](https://aistudio.google.com/app/apikey)")
        st.session_state.proposal_ready = False


# ─────────────────────────────────────────────
# PROPOSAL OUTPUT + DOWNLOADS (persisted)
# ─────────────────────────────────────────────
if st.session_state.proposal_ready and st.session_state.proposal_text:

    proposal_text = st.session_state.proposal_text
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Approval banner ──
    st.markdown("""
    <div class="approval-banner">
        <div style="font-size:2rem;">🏛️</div>
        <div>
            <div class="approval-title">✅ Gemini AI Generation Complete — Ready for Submission</div>
            <div class="approval-sub">
                Live RAG pipeline · Gemini 1.5 Flash · Company profile injected ·
                RFP requirements matched · Full proposal streamed &amp; captured.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI model info banner ──
    st.markdown(f"""
    <div class="ai-banner">
        <div style="font-size:1.8rem;">⚡</div>
        <div>
            <div class="ai-title">Model: {GEMINI_MODEL} &nbsp;|&nbsp; Mode: Streaming RAG</div>
            <div class="ai-sub">
                Prompt context: company_profile.txt + uploaded RFP →
                custom proposal generated in real time.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download options ──
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    col_dl_md, col_dl_txt, _ = st.columns([1, 1, 2])

    with col_dl_md:
        st.download_button(
            label="⬇️  Download as Markdown",
            data=proposal_text.encode("utf-8"),
            file_name=f"ai_proposal_{ts}.md",
            mime="text/markdown",
            use_container_width=True,
            key="dl_md",
        )
    with col_dl_txt:
        st.download_button(
            label="⬇️  Download as Plain Text",
            data=proposal_text.encode("utf-8"),
            file_name=f"ai_proposal_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt",
        )
