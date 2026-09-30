# 🛡️ AI Job/Internship Scam & Offer Verification System

A Streamlit + Gemini prototype that takes a pasted job/internship offer
email or chat message and produces an **evidence-based LOW / MEDIUM / HIGH
risk score** — with explicit reasons and recommendations — instead of a
flat "fake/real" label.

## How it works (pipeline)

1. **Extraction (Gemini)** — `src/extractor.py` prompts Gemini to pull out
   structured facts only (company, recruiter, job details, domain,
   claims, requests made, suspicious phrases). Gemini is explicitly told
   *not* to judge scam-vs-real here.
2. **Domain verification (rule-based + best-effort network checks)** —
   `src/domain_checker.py` checks: free-email-provider use, WHOIS domain
   age, website reachability/HTTPS, and whether the company name appears
   on the site.
3. **Optional AI company check** — `src/company_verifier.py` asks Gemini
   for a short descriptive note on the company/domain (uses Google Search
   grounding if the installed SDK/model plan supports it, otherwise falls
   back to a plain response). This is additive context, not a verdict.
4. **Red-flag detection (rule-based)** — `src/red_flags.py` scans for
   payment/fee requests, sensitive-data requests, urgency language,
   unrealistic-offer language, unofficial channels (WhatsApp/Telegram),
   non-corporate email, and missing/generic identity details — each with
   a weight, severity, and quoted evidence.
5. **Risk scoring** — `src/risk_engine.py` sums flag weights + domain
   penalties into a 0–100 score, buckets it into LOW (<25) / MEDIUM
   (25–54) / HIGH (55+), and generates human-readable reasons +
   recommendations.

This keeps the AI's role limited to *extraction and context*, while the
actual scoring logic is transparent rule-based code you can explain and
justify live at the expo (judges will likely ask "how did it decide
that?" — you can point to `red_flags.py` and `risk_engine.py` directly).

## Setup

```bash
cd job_scam_verifier
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a free Gemini API key at https://aistudio.google.com/app/apikey.

You can either:
- paste it into the sidebar text field when the app runs, or
- copy `.env.example` to `.env` and fill in `GEMINI_API_KEY` (then
  `export $(cat .env | xargs)` before running, or use `python-dotenv`
  in your shell of choice).

## Run

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501).

## Using it

1. Paste an offer email/message into the text box (or pick one of the
   three built-in sample messages from the sidebar — handy for a quick
   expo demo).
2. Click **Analyze Offer**.
3. Review:
   - **Risk Level & Score** at the top
   - **Extracted Details** (left) and **Domain Verification** (right)
   - **Red Flags Detected** — each expandable with the exact evidence
   - **Explanation** — plain-language reasons behind the score
   - **Recommendations** — what the candidate should actually do next

## Notes, limitations & things to mention at the expo

- **This is a decision-support tool, not a verdict.** It's explicitly
  designed to avoid a bare "fake/real" claim — the UI always shows
  score + reasons + recommendations together.
- **WHOIS and website checks are best-effort.** Corporate networks,
  rate limits, or a missing `whois` binary on some OSes can make these
  checks fail silently — they degrade to a note ("WHOIS lookup
  unavailable") rather than crashing.
- **Google Search grounding for the company-verification step depends
  on your Gemini API plan/SDK version.** If it's not available, the
  code automatically falls back to a plain (non-grounded) Gemini answer
  — still useful, just without live search context. You can mention
  this as a "future work" item (e.g., integrating a dedicated search
  API or a company registry lookup).
- **Model name drift:** Gemini model names change fairly often
  (`gemini-2.0-flash`, `gemini-1.5-flash`, etc.). The model name is a
  sidebar field precisely so you can swap it at demo time without
  touching code if Google renames/retires a model.
- **Good expo talking points:**
  - Why extraction and scoring are separated (explainability, no
    black-box AI verdict).
  - The weighted scoring table in `red_flags.py`/`risk_engine.py` —
    easy to walk a judge through.
  - Possible extensions: a browser extension version, a database of
    known scam domains/company names for instant flagging, OCR support
    for screenshot offers, multi-language support.

## Project structure

```
job_scam_verifier/
├── app.py                    # Streamlit UI
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── models.py              # Shared dataclasses
    ├── gemini_client.py       # Gemini API wrapper
    ├── extractor.py           # Step 1: structured extraction
    ├── domain_checker.py      # Step 2: domain/website verification
    ├── company_verifier.py    # Step 3 (optional): AI company notes
    ├── red_flags.py           # Step 4: rule-based red-flag detection
    └── risk_engine.py         # Step 5: score -> LOW/MEDIUM/HIGH + reasons
```
