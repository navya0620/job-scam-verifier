"""
Step 4: Combine red flags + domain verification into a single explainable
score (0-100) and LOW/MEDIUM/HIGH bucket, plus human-readable reasons and
recommendations. Thresholds and weights are intentionally simple and
transparent (see WEIGHTS in red_flags.py) so they can be justified live
at the expo, rather than a hidden ML score.
"""

from typing import List

from .models import DomainVerification, RedFlag, RiskAssessment

HIGH_THRESHOLD = 55
MEDIUM_THRESHOLD = 25


def compute_risk(flags: List[RedFlag], domain_info: DomainVerification) -> RiskAssessment:
    score = sum(f.weight for f in flags)

    if domain_info.website_reachable is False:
        score += 15
    if domain_info.company_name_on_site is False:
        score += 10

    score = min(score, 100)

    if score >= HIGH_THRESHOLD:
        level = "HIGH"
    elif score >= MEDIUM_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "LOW"

    reasons = [f"[{f.severity}] {f.category}: {f.description}" for f in flags]
    if domain_info.website_reachable is False:
        reasons.append(
            f"[MEDIUM] Domain Unreachable: No live website could be reached at '{domain_info.domain}'."
        )
    if domain_info.company_name_on_site is False:
        reasons.append(
            "[LOW] Company name not found on the sender domain's website content."
        )
    if not reasons:
        reasons.append(
            "No significant red flags were detected in the message content or domain checks."
        )

    recommendations = _build_recommendations(level, flags)

    return RiskAssessment(score=score, level=level, reasons=reasons, recommendations=recommendations)


def _build_recommendations(level: str, flags: List[RedFlag]) -> List[str]:
    recs: List[str] = []
    categories = {f.category for f in flags}

    if "Payment / Fee Request" in categories:
        recs.append(
            "Never pay any fee, deposit, or 'training cost' to a recruiter or company before formal, verified onboarding."
        )
    if "Sensitive Data Request" in categories:
        recs.append(
            "Do not share ID proofs, bank details, or OTPs over chat/email until the employer is independently verified."
        )
    if "Non-Corporate Email Domain" in categories or "Newly Registered Domain" in categories:
        recs.append(
            "Verify the company independently: check its official website, LinkedIn page, and reviews (e.g. Glassdoor)."
        )
    if "Artificial Urgency" in categories:
        recs.append(
            "Treat urgency as a warning sign — legitimate offers allow reasonable time to review and respond."
        )
    if "Unofficial Communication Channel" in categories:
        recs.append(
            "Ask for communication over official company email/phone, not personal WhatsApp/Telegram numbers."
        )

    recs.append(
        "Cross-check the recruiter's identity on LinkedIn and confirm the job posting exists on the company's official careers page."
    )
    recs.append(
        "When in doubt, call the company's official (publicly listed) phone number to confirm the offer directly."
    )

    if level == "HIGH":
        recs.insert(0, "Treat this offer with strong suspicion. Do not proceed, pay, or share personal information.")
    elif level == "MEDIUM":
        recs.insert(0, "Proceed cautiously — verify every claim independently before taking any action.")
    else:
        recs.insert(0, "No strong scam indicators found, but always do basic due diligence before sharing personal data.")

    return recs
