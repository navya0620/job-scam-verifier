import os

import streamlit as st

from src import theme, components as ui
from src.company_verifier import verify_company_with_gemini
from src.domain_checker import check_domain, extract_domain_from_email
from src.extractor import extract_information
from src.gemini_client import GeminiClient
from src.red_flags import detect_red_flags
from src.risk_engine import compute_risk

st.set_page_config(page_title="OfferGuard", page_icon="🛡️", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

theme.inject(st, dark=st.session_state.dark_mode)

if "offer_text" not in st.session_state:
    st.session_state.offer_text = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "pending_offer_text" in st.session_state:
    st.session_state.offer_text = st.session_state.pop("pending_offer_text")

SAMPLES = {
    "⚠️ Fake Internship (Payment)": (
        "Subject: Congratulations! You are SELECTED for Data Entry Internship\n\n"
        "Dear Candidate,\n\nCongratulations! Based on your resume you are directly selected "
        "for our Work From Home Data Entry Internship. No interview required. You can earn "
        "up to Rs. 45,000 per month working just 2 hours a day.\n\nTo confirm your seat you "
        "must pay a refundable registration fee of Rs. 1500 within 24 hours as slots are "
        "limited. Please share your Aadhaar card and bank account details for the offer "
        "letter and salary account setup.\n\nRegards,\nHR Team\nBright Future Global Pvt Ltd\n"
        "hr.brightfuture2024@gmail.com"
    ),
    "📱 WhatsApp Job Scam": (
        "Hii! We found your resume online. We have an urgent opening for Online Part Time "
        "Job, earn Rs 3000-5000 daily, just like and subscribe YouTube videos. No fees, no "
        "targets. For more details and to start today, message us only on WhatsApp at "
        "+91-9xxxxxxxxx. Do not call, WhatsApp only. Limited seats, join now!"
    ),
    "💰 Fake Job (High Salary)": (
        "Hi, we are excited to inform you that you have been instantly selected for the "
        "position of Remote Business Associate with a guaranteed salary of Rs 1,20,000 per "
        "month. No experience needed, no interview, 100% selection. Just complete your "
        "registration by sharing your bank details so we can process your first advance "
        "payment.\n\nBest,\nQuickHire Global\ncareers.quickhireglobal@yahoo.com"
    ),
    "✅ Real Internship Offer": (
        "Dear Aditi,\n\nThank you for interviewing with us. We are pleased to offer you the "
        "Software Engineering Intern position at Clearbridge Analytics, starting 15th "
        "September. Your stipend will be Rs 20,000/month. Please find the formal offer letter "
        "attached, and reach out to hr@clearbridgeanalytics.com or +91-80-4123-5566 with any "
        "questions. You can also verify this role on our careers page at "
        "clearbridgeanalytics.com/careers.\n\nBest regards,\nPriya Menon\nHR Manager, "
        "Clearbridge Analytics"
    ),
}

# ---------------- Navbar ----------------
nav_l, nav_r = st.columns([3, 2])
with nav_l:
    ui.render_navbar_brand(st)
with nav_r:
    b1, b2, b3 = st.columns(3)
    with b1:
        with st.popover("❓ How it works", use_container_width=True):
            st.markdown(
                "**1. Paste** the offer message.\n\n"
                "**2. We extract** company, recruiter, and job details.\n\n"
                "**3. We check** the sender's domain and website.\n\n"
                "**4. We scan** for common scam warning signs.\n\n"
                "**5. You get** a plain-language risk score and what to do next."
            )
    with b2:
        with st.popover("☰ Settings", use_container_width=True):
            api_key = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
            model_name = st.text_input("Gemini model", value=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"))
    with b3:
        if st.toggle("🌙 Dark", value=st.session_state.dark_mode, key="dark_toggle"):
            if not st.session_state.dark_mode:
                st.session_state.dark_mode = True
                st.rerun()
        else:
            if st.session_state.dark_mode:
                st.session_state.dark_mode = False
                st.rerun()

st.markdown('<div class="navbar-rule"></div>', unsafe_allow_html=True)
ui.render_hero(st)

# ---------------- Main layout ----------------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<div class="form-panel">', unsafe_allow_html=True)
    st.markdown('<div class="step-row"><span class="step-badge">1</span><span class="step-title">Paste the offer email or message</span></div>', unsafe_allow_html=True)

    message = st.text_area(
        " ", height=190, key="offer_text",
        placeholder="Paste the full offer email, WhatsApp message, or any job/internship offer here...",
        label_visibility="collapsed",
    )
    st.caption(f"💡 Include as much detail as possible for better analysis.  ·  {len(message)}/8000 characters")

    lbl_col, clear_col = st.columns([4, 1])
    with lbl_col:
        st.markdown('<div class="chip-row-label">Try an example</div>', unsafe_allow_html=True)
    with clear_col:
        if st.button("🔄 Clear", key="clear_btn"):
            st.session_state.pending_offer_text = ""
            st.session_state.result = None
            st.rerun()

    chip_cols = st.columns(4)
    for col, label in zip(chip_cols, SAMPLES.keys()):
        with col:
            if st.button(label, key=f"chip_{label}", use_container_width=True):
                st.session_state.pending_offer_text = SAMPLES[label]
                st.session_state.result = None
                st.rerun()

    st.markdown('<div class="step-row" style="margin-top:22px"><span class="step-badge">2</span><span class="step-title">(Optional) Add extra details</span></div>', unsafe_allow_html=True)
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        extra_company = st.text_input("Company name (if known)", placeholder="e.g., Infosys")
    with ec2:
        extra_sender = st.text_input("Sender email / number", placeholder="e.g., hr@company.com")
    with ec3:
        extra_role = st.text_input("Job role (if mentioned)", placeholder="e.g., Data Analyst Intern")
    ec4, ec5 = st.columns(2)
    with ec4:
        extra_platform = st.selectbox("Source platform", ["Select platform", "Email", "WhatsApp", "LinkedIn", "Telegram", "Instagram", "Job Portal", "Other"])
    with ec5:
        extra_links = st.text_input("Any links shared in the offer?", placeholder="e.g., https://example.com")

    st.caption("🔒 We don't store your data. Everything is analyzed in real-time.")
    analyze = st.button("🔍  Analyze Offer", type="primary", use_container_width=True)

with right:
    st.markdown('<div class="result-panel">', unsafe_allow_html=True)
    st.markdown('<div class="result-panel-title">🛡️ Analysis Result</div>', unsafe_allow_html=True)

    result = st.session_state.result
    ui.render_gauge(st, result["score"] if result else None, result["level"] if result else None)

    if result:
        why_html = "".join(f"<div>• {ui.esc(r)}</div>" for r in result["why"][:5]) or "<div class='mini-placeholder'>No major concerns found.</div>"
        extracted_html = f"<div>{ui.esc(result['extracted_summary'])}</div>"
        verify_html = f"<div>{ui.esc(result['verify_summary'])}</div>"
        rec_html = "".join(f"<div>• {ui.esc(r)}</div>" for r in result["recs"][:3])
    else:
        why_html = "<div class='mini-placeholder'>Key reasons and red flags will appear here.</div>"
        extracted_html = "<div class='mini-placeholder'>Company, sender, role, links and other details will be shown here.</div>"
        verify_html = "<div class='mini-placeholder'>We'll show evidence from domain checks and company lookups here.</div>"
        rec_html = "<div class='mini-placeholder'>Actionable steps to protect yourself. Always verify independently.</div>"

    ui.render_mini_card(st, "⚠️", "Why this risk?", why_html)
    ui.render_mini_card(st, "📄", "Extracted Information", extracted_html)
    ui.render_mini_card(st, "🛡️", "Verification & Evidence", verify_html)
    ui.render_mini_card(st, "📋", "Safety Recommendation", rec_html)

# ---------------- Run analysis ----------------
if analyze:
    full_text = message
    extras = []
    if extra_company: extras.append(f"Company: {extra_company}")
    if extra_sender: extras.append(f"Sender: {extra_sender}")
    if extra_role: extras.append(f"Role: {extra_role}")
    if extra_platform != "Select platform": extras.append(f"Platform: {extra_platform}")
    if extra_links: extras.append(f"Links: {extra_links}")
    if extras:
        full_text += "\n\n[Additional details provided by user]\n" + "\n".join(extras)

    if not api_key:
        st.error("Please add your Gemini API key from the ☰ Settings menu at the top right.")
    elif not full_text.strip():
        st.error("Please paste a message to analyze.")
    else:
        try:
            with st.spinner("Reading the message..."):
                client = GeminiClient(api_key=api_key, model_name=model_name)
                info = extract_information(client, full_text)
        except Exception as e:
            st.error(f"Something went wrong while reading the message: {e}")
            st.stop()

        domain = info.sender_domain or extract_domain_from_email(info.contact_email)
        with st.spinner("Checking the sender's website..."):
            domain_info = check_domain(domain, info.company_name)

        with st.spinner("Looking up the company..."):
            company_summary = verify_company_with_gemini(client, info.company_name, domain, info.job_title)
        domain_info.search_summary = company_summary

        flags = detect_red_flags(
            raw_text=full_text, info=info,
            is_free_email=domain_info.is_free_email_provider,
            domain_age_days=domain_info.domain_age_days,
        )
        risk = compute_risk(flags, domain_info)

        why = [f.description for f in sorted(flags, key=lambda x: -x.weight)]
        extracted_summary = f"{info.company_name or 'Unknown company'} · {info.job_title or 'role not specified'} · {info.contact_email or info.sender_domain or 'no contact found'}"
        verify_summary = f"Website: {'found' if domain_info.website_reachable else 'not found'} · Domain age: {domain_info.domain_age_days if domain_info.domain_age_days is not None else 'unknown'} days"

        st.session_state.result = {
            "score": risk.score, "level": risk.level, "why": why, "recs": risk.recommendations,
            "extracted_summary": extracted_summary, "verify_summary": verify_summary,
            "info": info, "domain_info": domain_info, "flags": flags, "risk": risk,
        }
        st.rerun()

# ---------------- Full detailed report ----------------
if st.session_state.result:
    r = st.session_state.result
    info, domain_info, flags, risk = r["info"], r["domain_info"], r["flags"], r["risk"]

    def yn(v):
        return "Yes" if v is True else ("No" if v is False else "Not sure")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    ui.render_section_label(st, "Full Report")

    col1, col2 = st.columns(2)
    with col1:
        ui.render_field_card(st, "What We Found In The Message", "📋", [
            ("Company Name", info.company_name), ("Recruiter Name", info.recruiter_name),
            ("Job Title", info.job_title), ("Location", info.job_location),
            ("Pay Offered", info.salary_offered), ("Contact Email", info.contact_email),
            ("Contact Phone", info.contact_phone), ("How They Contacted You", info.communication_channel),
        ])
    with col2:
        age_text = "Not available"
        if domain_info.domain_age_days is not None:
            age_text = f"{domain_info.domain_age_days} days old"
            if domain_info.domain_age_days < 180:
                age_text += " (very new)"
        ui.render_field_card(st, "Website & Email Check", "🌐", [
            ("Sender's Domain", domain_info.domain or "Unknown"),
            ("Personal Email (Gmail etc.)?", yn(domain_info.is_free_email_provider)),
            ("Company Website Found?", yn(domain_info.website_reachable)),
            ("Website Is Secure (HTTPS)?", yn(domain_info.https_valid)),
            ("How Old Is The Domain?", age_text),
            ("Company Name On Website?", yn(domain_info.company_name_on_site)),
        ])

    if info.claims or info.requests_made:
        c3, c4 = st.columns(2)
        with c3:
            ui.render_chip_list_card(st, "Promises Made To You", "💬", info.claims)
        with c4:
            ui.render_chip_list_card(st, "What They're Asking You To Do", "📎", info.requests_made)

    if domain_info.search_summary:
        ui.render_field_card(st, "About This Company", "🔎", [], notes=[domain_info.search_summary])

    ui.render_section_label(st, f"Warning Signs Found ({len(flags)})")
    if flags:
        for f in sorted(flags, key=lambda x: -x.weight):
            ui.render_flag_ticket(st, f.category, f.severity, f.description, f.evidence)
    else:
        st.success("We didn't spot any common scam warning signs in this message.")

    ui.render_checklist_card(st, "What You Should Do", "✅", risk.recommendations)
    st.caption("This is an automated check to help you spot warning signs — it can make mistakes. Always verify a job offer yourself before paying money or sharing personal documents.")

# ---------------- Feature strip + footer ----------------
ui.render_feature_strip(st, [
    ("🛡️", "No upfront payments", "Legit companies don't ask for fees"),
    ("🔍", "Verify independently", "Check on official websites"),
    ("⏱️", "Trust, but verify", "Scammers create urgency"),
    ("🔒", "Your safety first", "Protect your personal information"),
])
st.markdown('<div class="app-footer">OfferGuard is a student project prototype. Not legal or professional advice. Always verify offers independently.</div>', unsafe_allow_html=True)