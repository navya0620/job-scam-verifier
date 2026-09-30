"""
Visual theme for OfferGuard — a verification-report style UI.
Fonts: Space Grotesk (display), Inter (body), JetBrains Mono (data/evidence).
"""
LIGHT_VARS = """
    --ink: #0B1220;
    --paper: #F6F7FB;
    --card: #FFFFFF;
    --border: #E3E6EB;
    --text: #111827;
    --text-muted: #6B7280;
    --accent: #4F46E5;
    --accent-2: #6366F1;
    --risk-low: #15803D;
    --risk-medium: #B45309;
    --risk-high: #B91C1C;
"""

DARK_VARS = """
    --ink: #F6F7FB;
    --paper: #0B1220;
    --card: #131B2E;
    --border: #253047;
    --text: #E5E7EB;
    --text-muted: #9CA3AF;
    --accent: #818CF8;
    --accent-2: #A5B4FC;
    --risk-low: #4ADE80;
    --risk-medium: #FBBF24;
    --risk-high: #F87171;
"""
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
__VARS__
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text); }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.4rem; max-width: 1180px; }
[data-testid="stAppViewContainer"] { background: var(--paper); }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.01em; }

/* ---- Navbar ---- */
.navbar-brand { display: flex; align-items: center; gap: 10px; }
.brand-icon { font-size: 1.7rem; }
.brand-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: var(--text); }
.brand-title-accent { background: linear-gradient(90deg, var(--accent), var(--accent-2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.brand-tagline { font-size: 0.78rem; color: var(--text-muted); margin-top: -2px; }
.navbar-rule { height: 2px; background: linear-gradient(90deg, var(--accent), var(--accent-2), transparent); margin: 10px 0 20px 0; border-radius: 2px; }

/* ---- Hero ---- */
.hero { margin-bottom: 18px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700; line-height: 1.2; color: var(--text); }
.hero-accent { background: linear-gradient(90deg, var(--accent), var(--accent-2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-sub { color: var(--text-muted); font-size: 0.95rem; margin-top: 6px; max-width: 640px; }

/* ---- Form panel (left) ---- */
.st-key-form_panel { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 22px 24px; margin-bottom: 18px; }
.step-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.step-badge { width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, var(--accent), var(--accent-2)); color: white; font-size: 0.78rem; font-weight: 700; display: flex; align-items: center; justify-content: center; font-family: 'Space Grotesk', sans-serif; flex-shrink: 0; }
.step-title { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1rem; }
.chip-row-label { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.88rem; margin-top: 14px; }

[data-testid="stTextArea"] textarea {
    background: var(--card); color: var(--text) !important;
    border: 1.5px dashed var(--border) !important; border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; padding: 14px !important;
}
[data-testid="stTextArea"] textarea::placeholder {
    color: var(--text-muted) !important; opacity: 1;
}
[data-testid="stTextArea"] textarea:focus { border-color: var(--accent) !important; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: var(--card) !important; color: var(--text) !important;
    border-radius: 8px !important; font-size: 0.85rem;
}
[data-testid="stTextInput"] input::placeholder {
    color: var(--text-muted) !important; opacity: 1;
}

/* Buttons */
button[kind="secondary"], [data-testid="baseButton-secondary"] {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 999px !important;
    font-size: 0.8rem !important; padding: 0.35rem 0.9rem !important;
}
button[kind="secondary"], [data-testid="baseButton-secondary"] {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 999px !important;
    font-size: 0.8rem !important; padding: 0.35rem 0.9rem !important;
}
button[kind="secondary"]:hover, [data-testid="baseButton-secondary"]:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

[data-testid="stPopover"] > div > button {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stPopoverBody"] {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
/* ---- Result panel (right) ---- */
.st-key-result_panel { background: var(--card); border: 1.5px dashed #C7CCD6; border-radius: 16px; padding: 20px; margin-bottom: 18px; }
.result-panel-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.02rem; margin-bottom: 14px; }

.gauge-wrap { display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 8px; }
.gauge-svg { width: 210px; margin-bottom: -18px; }
.gauge-score-label { font-size: 0.78rem; color: var(--text-muted); }
.gauge-score-text { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; }
.gauge-score-max { font-size: 1rem; color: var(--text-muted); font-weight: 500; }
.gauge-badge { display: inline-block; padding: 4px 14px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; margin-top: 6px; }
.gauge-badge-placeholder { background: #F0F1F4; color: var(--text-muted); }
.gauge-caption { font-size: 0.78rem; color: var(--text-muted); margin-top: 8px; }

.mini-card { border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }
.mini-card-title { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.85rem; margin-bottom: 6px; }
.mini-card-body { font-size: 0.8rem; color: var(--text); line-height: 1.5; }
.mini-placeholder { color: var(--text-muted); font-style: italic; }

/* ---- Full report cards (reused below) ---- */
.report-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; margin-bottom: 16px; }
.report-card .card-title { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.95rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.field-row { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; border-bottom: 1px solid #F0F1F4; font-size: 0.86rem; }
.field-row:last-child { border-bottom: none; }
.field-row .k { color: var(--text-muted); }
.field-row .v { font-family: 'JetBrains Mono', monospace; text-align: right; color: var(--text); }
.chip-list { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
.chip-list .chip { background: #F5F6F8; border-radius: 8px; padding: 6px 10px; font-size: 0.82rem; color: var(--text); }
.note-line { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }

.flag-ticket { background: var(--card); border: 1px solid var(--border); border-left: 5px solid var(--flag-color, #999); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
.flag-ticket .flag-top { display: flex; justify-content: space-between; align-items: center; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.88rem; }
.flag-ticket .flag-sev { font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; padding: 2px 8px; border-radius: 999px; color: white; background: var(--flag-color, #999); }
.flag-ticket p { font-size: 0.84rem; color: var(--text-muted); margin: 6px 0 8px 0; }
.flag-ticket .evidence { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; background: #F5F6F8; padding: 5px 10px; border-radius: 6px; display: inline-block; }

.checklist-item { display: flex; gap: 10px; align-items: flex-start; padding: 7px 0; font-size: 0.88rem; }
.checklist-item .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); margin-top: 7px; flex-shrink: 0; }

.section-label { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); margin: 26px 0 10px 0; }

/* ---- Feature strip ---- */
.feature-strip { display: flex; flex-wrap: wrap; gap: 26px; justify-content: space-between; background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px 24px; margin: 24px 0 10px 0; }
.feature-item { display: flex; align-items: flex-start; gap: 10px; min-width: 200px; flex: 1; }
.feature-icon { font-size: 1.3rem; }
.feature-title { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.86rem; }
.feature-sub { font-size: 0.76rem; color: var(--text-muted); }

.app-footer { text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 20px; padding: 16px 0; }
</style>
"""


def inject(st, dark: bool = False):
    vars_block = DARK_VARS if dark else LIGHT_VARS
    css = CSS_TEMPLATE.replace("__VARS__", vars_block)
    st.markdown(css, unsafe_allow_html=True)