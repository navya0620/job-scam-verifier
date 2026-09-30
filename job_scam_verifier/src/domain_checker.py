"""
Step 2: Best-effort, non-LLM verification of the sender's domain.
All checks degrade gracefully (they never raise) because on an expo laptop
network conditions / WHOIS availability can be flaky — a failed check just
becomes a note, not a crash.
"""

import datetime
from typing import Optional

import requests

from .models import DomainVerification

FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com",
    "protonmail.com", "icloud.com", "aol.com", "yandex.com", "zoho.com",
    "live.com", "mail.com", "gmx.com",
}


def extract_domain_from_email(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    return email.split("@")[-1].strip().lower()


def check_domain(domain: Optional[str], company_name: Optional[str]) -> DomainVerification:
    result = DomainVerification(domain=domain or "")
    if not domain:
        result.notes.append("No sender domain could be determined from the message.")
        return result

    result.is_free_email_provider = domain in FREE_EMAIL_PROVIDERS
    if result.is_free_email_provider:
        result.notes.append(
            f"'{domain}' is a free/personal email provider, not a dedicated corporate domain."
        )

    # --- WHOIS lookup (best-effort) ---
    try:
        import whois  # python-whois

        w = whois.whois(domain)
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        if created:
            age_days = (datetime.datetime.now() - created).days
            result.domain_age_days = age_days
            if age_days < 180:
                result.notes.append(
                    f"Domain is very new ({age_days} days old) — a trait often seen in scam setups."
                )
        result.registrar = getattr(w, "registrar", None)
    except Exception as e:
        result.notes.append(f"WHOIS lookup unavailable or failed ({type(e).__name__}).")

    # --- Website reachability + light content check ---
    fetched = False
    for scheme in ("https://", "http://"):
        try:
            resp = requests.get(
                f"{scheme}{domain}",
                timeout=6,
                headers={"User-Agent": "Mozilla/5.0 (JobOfferVerifier/1.0)"},
            )
            result.website_reachable = resp.status_code < 400
            result.https_valid = scheme == "https://"
            if company_name:
                haystack = resp.text.lower()
                result.company_name_on_site = company_name.lower() in haystack
                if result.company_name_on_site is False:
                    result.notes.append(
                        "Company name was not found in the sender domain's homepage text."
                    )
            fetched = True
            break
        except requests.RequestException:
            continue

    if not fetched:
        result.website_reachable = False
        result.notes.append(f"Could not reach a live website at '{domain}'.")

    return result
