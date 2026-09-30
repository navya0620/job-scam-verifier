"""
Step 3: Explicit, explainable rule-based red-flag detection.
Kept deliberately rule-based (not another LLM call) so every flag in the
final report can point to exact keyword evidence — this is what makes the
tool "explainable" rather than a black-box AI verdict.
"""

from typing import List, Optional

from .models import ExtractedInfo, RedFlag

PAYMENT_KEYWORDS = [
    "registration fee", "processing fee", "security deposit", "training fee",
    "refundable deposit", "pay for", "purchase kit", "buy equipment",
    "activation fee", "onboarding fee", "convenience fee", "caution money",
]
URGENCY_KEYWORDS = [
    "act now", "limited slots", "within 24 hours", "immediately",
    "urgent", "expires today", "only few seats", "hurry", "last chance",
    "respond within", "offer valid till",
]
SENSITIVE_DATA_KEYWORDS = [
    "aadhaar", "aadhar", "pan card", "passport number", "bank account number",
    "bank details", "credit card", "debit card", "otp", "ifsc", "cvv",
    "social security", "ssn",
]
UNREALISTIC_KEYWORDS = [
    "no interview", "guaranteed job", "guaranteed placement", "work 2 hours",
    "earn lakhs", "easy money", "no experience needed", "instant hire",
    "100% selection", "selected directly", "work from home earn",
]
UNOFFICIAL_CHANNEL_KEYWORDS = ["whatsapp", "telegram", "personal number"]


def _find_matches(text: str, keywords: List[str]) -> List[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def detect_red_flags(
    raw_text: str,
    info: ExtractedInfo,
    is_free_email: bool,
    domain_age_days: Optional[int],
) -> List[RedFlag]:
    flags: List[RedFlag] = []
    combined_text = " ".join(
        [
            raw_text,
            " ".join(info.claims),
            " ".join(info.requests_made),
            " ".join(info.suspicious_phrases),
        ]
    )

    payment_hits = _find_matches(combined_text, PAYMENT_KEYWORDS)
    if payment_hits:
        flags.append(
            RedFlag(
                category="Payment / Fee Request",
                severity="HIGH",
                weight=35,
                description="The message asks the candidate to pay money before or during hiring. Legitimate employers do not charge candidates fees.",
                evidence=", ".join(payment_hits),
            )
        )

    sensitive_hits = _find_matches(combined_text, SENSITIVE_DATA_KEYWORDS)
    if sensitive_hits:
        flags.append(
            RedFlag(
                category="Sensitive Data Request",
                severity="HIGH",
                weight=30,
                description="The message requests sensitive personal/financial identifiers unusually early in the hiring process.",
                evidence=", ".join(sensitive_hits),
            )
        )

    urgency_hits = _find_matches(combined_text, URGENCY_KEYWORDS)
    if urgency_hits:
        flags.append(
            RedFlag(
                category="Artificial Urgency",
                severity="MEDIUM",
                weight=15,
                description="The message pressures the recipient to act fast, discouraging careful verification.",
                evidence=", ".join(urgency_hits),
            )
        )

    unrealistic_hits = _find_matches(combined_text, UNREALISTIC_KEYWORDS)
    if unrealistic_hits:
        flags.append(
            RedFlag(
                category="Unrealistic Offer",
                severity="MEDIUM",
                weight=15,
                description="The offer promises outcomes (guaranteed hiring, unusually high pay, no interview) inconsistent with normal hiring processes.",
                evidence=", ".join(unrealistic_hits),
            )
        )

    channel_hits = _find_matches(combined_text, UNOFFICIAL_CHANNEL_KEYWORDS)
    channel_field = (info.communication_channel or "").lower()
    if channel_hits or any(k in channel_field for k in ["whatsapp", "telegram"]):
        evidence = ", ".join(channel_hits) if channel_hits else info.communication_channel
        flags.append(
            RedFlag(
                category="Unofficial Communication Channel",
                severity="MEDIUM",
                weight=10,
                description="Hiring is being conducted over informal chat apps rather than official company channels.",
                evidence=evidence or "",
            )
        )

    if is_free_email:
        flags.append(
            RedFlag(
                category="Non-Corporate Email Domain",
                severity="MEDIUM",
                weight=15,
                description="The recruiter is emailing from a free/personal email provider rather than a company domain.",
                evidence=info.sender_domain or "",
            )
        )

    if domain_age_days is not None and domain_age_days < 180:
        flags.append(
            RedFlag(
                category="Newly Registered Domain",
                severity="HIGH",
                weight=20,
                description="The company domain was registered very recently, which is common for short-lived scam operations.",
                evidence=f"Domain age: {domain_age_days} days",
            )
        )

    if not info.recruiter_name or not info.company_name:
        flags.append(
            RedFlag(
                category="Missing Identity Details",
                severity="LOW",
                weight=5,
                description="The message lacks a clearly named recruiter and/or company, making it harder to independently verify.",
                evidence="Recruiter or company name missing",
            )
        )

    if info.suspicious_phrases:
        flags.append(
            RedFlag(
                category="Generic / Templated Language",
                severity="LOW",
                weight=5,
                description="The message contains generic or templated phrasing often reused across mass scam messages.",
                evidence="; ".join(info.suspicious_phrases[:3]),
            )
        )

    return flags
