"""
Optional Step: ask Gemini for a short, descriptive (not judgmental) note
about company/domain legitimacy signals, using search grounding if the
installed SDK/model supports it. This is best-effort and purely additive —
if grounding isn't available it still returns a plain-knowledge answer,
and if the call fails entirely the UI just shows a short notice instead
of crashing the whole analysis.
"""

from .gemini_client import GeminiClient

VERIFY_PROMPT = """
Based on your knowledge (and web search if you have access to it), briefly
describe legitimacy signals for the following company and domain in 3-5
sentences: is it a known company, does the domain look consistent with the
company's expected official domain, anything notable or unverifiable?
Do NOT give a final "scam" or "legit" verdict — only describe what is known
or unknown, since that judgement is made elsewhere in this tool.

Company name: {company}
Domain: {domain}
Job title mentioned: {job_title}
"""


def verify_company_with_gemini(client: GeminiClient, company, domain, job_title) -> str:
    if not company and not domain:
        return "Insufficient information (no company name or domain) to look up."

    prompt = VERIFY_PROMPT.format(
        company=company or "Unknown",
        domain=domain or "Unknown",
        job_title=job_title or "Unknown",
    )

    # Try to enable search grounding if the SDK/model supports it; otherwise
    # fall back to a plain (non-grounded) Gemini response.
    try:
        import google.generativeai as genai

        try:
            tool_model = genai.GenerativeModel(client.model_name, tools="google_search_retrieval")
            response = tool_model.generate_content(prompt)
            text = (response.text or "").strip()
            if text:
                return text
        except Exception:
            pass  # grounding not supported by this SDK/model/plan — fall back below

        return client.generate_text(prompt)
    except Exception as e:
        return f"Company verification note unavailable ({type(e).__name__}: {e})."
