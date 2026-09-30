"""
HTML rendering helpers for the OfferGuard report UI.
"""

import html
import math
import textwrap

LEVEL_META = {
    "LOW": {"label": "LOW RISK", "verdict": "No strong scam indicators found."},
    "MEDIUM": {"label": "MEDIUM RISK", "verdict": "Some concerning signals — verify before acting."},
    "HIGH": {"label": "HIGH RISK", "verdict": "Multiple strong scam indicators detected."},
}
LEVEL_COLOR = {"LOW": "#15803D", "MEDIUM": "#B45309", "HIGH": "#B91C1C"}
SEVERITY_COLOR = {"LOW": "#9CA3AF", "MEDIUM": "#B45309", "HIGH": "#B91C1C"}


def esc(text) -> str:
    if text is None:
        return "—"
    return html.escape(str(text))


# ---------------- Navbar / Hero ----------------

def render_navbar_brand(st):
    st.markdown(
        """
        <div class="navbar-brand">
            <div class="brand-icon">🛡️</div>
            <div>
                <div class="brand-title">Offer<span class="brand-title-accent">Guard</span></div>
                <div class="brand-tagline">AI-Powered Offer Verification</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(st):
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Verify <span class="hero-accent">any job or internship offer</span> in seconds</div>
            <div class="hero-sub">Paste the offer email or message, and get an evidence-based risk analysis with reasons and safety recommendations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Gauge ----------------

def render_gauge(st, score, level):
    cx, cy, r = 100, 100, 78
    path = f"M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}"

    if score is None:
        svg = f"""
        <svg viewBox="0 0 200 110" class="gauge-svg">
          <path d="{path}" stroke="#E3E6EB" stroke-width="14" fill="none" stroke-linecap="round"/>
        </svg>
        """
        score_text, badge_html, caption = "--", '<div class="gauge-badge gauge-badge-placeholder">--</div>', "Submit an offer to see the analysis"
    else:
        frac = max(0, min(score, 100)) / 100
        theta = math.radians(180 - frac * 180)
        mx, my = cx + r * math.cos(theta), cy - r * math.sin(theta)
        circumference = math.pi * r
        filled = circumference * frac
        remaining = circumference - filled
        badge_color = LEVEL_COLOR.get(level, "#6B7280")
        svg = f"""
        <svg viewBox="0 0 200 110" class="gauge-svg">
          <defs>
            <linearGradient id="riskGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#22C55E"/>
              <stop offset="35%" stop-color="#EAB308"/>
              <stop offset="65%" stop-color="#F97316"/>
              <stop offset="100%" stop-color="#DC2626"/>
            </linearGradient>
          </defs>
          <path d="{path}" stroke="#EDEEF1" stroke-width="14" fill="none" stroke-linecap="round"/>
          <path d="{path}" stroke="url(#riskGrad)" stroke-width="14" fill="none" stroke-linecap="round"
                stroke-dasharray="{filled:.1f} {remaining:.1f}"/>
          <circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="white" stroke="{badge_color}" stroke-width="3"/>
        </svg>
        """
        score_text = str(score)
        badge_html = f'<div class="gauge-badge" style="background:{badge_color}1A;color:{badge_color};border:1px solid {badge_color}55">{level} RISK</div>'
        caption = ""

    st.markdown(textwrap.dedent(f"""
       <div class="gauge-wrap">
       {svg}
       <div class="gauge-score-label">Risk Score</div>
       <div class="gauge-score-text">{score_text}<span class="gauge-score-max">/100</span></div>
       {badge_html}
       <div class="gauge-caption">{caption}</div>
       </div>
       """).strip(), 
       unsafe_allow_html=True
    )


def render_mini_card(st, icon, title, body_html):
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-card-title">{icon} {esc(title)}</div>
            <div class="mini-card-body">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- Full-detail report cards ----------------

def render_field_card(st, title: str, icon: str, fields: list, notes: list = None):
    rows = "".join(
        f'<div class="field-row"><span class="k">{esc(k)}</span><span class="v">{esc(v)}</span></div>'
        for k, v in fields
    )
    notes_html = "".join(f'<div class="note-line">• {esc(n)}</div>' for n in (notes or []))
    st.markdown(
        f'<div class="report-card"><div class="card-title">{icon} {esc(title)}</div>{rows}{notes_html}</div>',
        unsafe_allow_html=True,
    )


def render_chip_list_card(st, title: str, icon: str, items: list):
    if not items:
        return
    chips = "".join(f'<div class="chip">{esc(i)}</div>' for i in items)
    st.markdown(
        f'<div class="report-card"><div class="card-title">{icon} {esc(title)}</div><div class="chip-list">{chips}</div></div>',
        unsafe_allow_html=True,
    )


def render_flag_ticket(st, category: str, severity: str, description: str, evidence: str):
    color = SEVERITY_COLOR.get(severity, "#9CA3AF")
    st.markdown(
        f"""
        <div class="flag-ticket" style="--flag-color:{color}">
            <div class="flag-top"><span>{esc(category)}</span><span class="flag-sev">{esc(severity)}</span></div>
            <p>{esc(description)}</p>
            <span class="evidence">{esc(evidence)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_checklist_card(st, title: str, icon: str, items: list):
    rows = "".join(f'<div class="checklist-item"><div class="dot"></div><div>{esc(i)}</div></div>' for i in items)
    st.markdown(f'<div class="report-card"><div class="card-title">{icon} {esc(title)}</div>{rows}</div>', unsafe_allow_html=True)


def render_section_label(st, text: str):
    st.markdown(f'<div class="section-label">{esc(text)}</div>', unsafe_allow_html=True)


def render_feature_strip(st, items):
    cells = "".join(
        f'<div class="feature-item"><div class="feature-icon">{icon}</div>'
        f'<div><div class="feature-title">{esc(title)}</div><div class="feature-sub">{esc(sub)}</div></div></div>'
        for icon, title, sub in items
    )
    st.markdown(f'<div class="feature-strip">{cells}</div>', unsafe_allow_html=True)