"""
Step 1: Extraction only. Gemini is deliberately instructed NOT to judge
scam-vs-real here — it only pulls out structured facts. Judgement happens
later in red_flags.py and risk_engine.py, using explicit rules, so the
final verdict is explainable rather than a black-box "yes/no" from the LLM.
"""

from .gemini_client import GeminiClient
from .models import ExtractedInfo

EXTRACTION_PROMPT = """
You are an information-extraction assistant helping analyze a job/internship
offer message for a scam-verification tool. Read the message below (it may be
an email, LinkedIn message, or WhatsApp/Telegram chat text) and extract
structured information. Do NOT judge whether it is a scam — only extract facts
and quote suspicious-sounding phrases verbatim; scoring happens elsewhere.

Return ONLY valid JSON with exactly these keys (use null or [] when unknown):
{{
  "company_name": string or null,
  "recruiter_name": string or null,
  "recruiter_title": string or null,
  "job_title": string or null,
  "job_location": string or null,
  "employment_type": string or null,
  "salary_offered": string or null,
  "contact_email": string or null,
  "contact_phone": string or null,
  "sender_domain": string or null,
  "communication_channel": string or null,
  "claims": [notable claims made, e.g. "no interview required", "guaranteed placement"],
  "requests_made": [things the message asks the recipient to do or provide, e.g. "pay registration fee", "share Aadhaar card", "join a Telegram group"],
  "suspicious_phrases": [exact short phrases from the text that read as generic, urgent, or unusual for a legitimate employer],
  "raw_summary": "one or two sentence neutral summary of the message"
}}

Message:
---
{message}
---
"""


def extract_information(client: GeminiClient, message: str) -> ExtractedInfo:
    prompt = EXTRACTION_PROMPT.format(message=message)
    data = client.generate_json(prompt)
    return ExtractedInfo(
        company_name=data.get("company_name"),
        recruiter_name=data.get("recruiter_name"),
        recruiter_title=data.get("recruiter_title"),
        job_title=data.get("job_title"),
        job_location=data.get("job_location"),
        employment_type=data.get("employment_type"),
        salary_offered=data.get("salary_offered"),
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        sender_domain=data.get("sender_domain"),
        communication_channel=data.get("communication_channel"),
        claims=data.get("claims") or [],
        requests_made=data.get("requests_made") or [],
        suspicious_phrases=data.get("suspicious_phrases") or [],
        raw_summary=data.get("raw_summary"),
    )
