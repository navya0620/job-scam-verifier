"""
Shared data structures used across the pipeline:
extract -> verify domain/company -> detect red flags -> compute risk.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExtractedInfo:
    company_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_title: Optional[str] = None
    job_title: Optional[str] = None
    job_location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_offered: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    sender_domain: Optional[str] = None
    communication_channel: Optional[str] = None
    claims: List[str] = field(default_factory=list)
    requests_made: List[str] = field(default_factory=list)
    suspicious_phrases: List[str] = field(default_factory=list)
    raw_summary: Optional[str] = None


@dataclass
class RedFlag:
    category: str
    severity: str  # LOW / MEDIUM / HIGH
    weight: int
    description: str
    evidence: str


@dataclass
class DomainVerification:
    domain: str = ""
    is_free_email_provider: bool = False
    website_reachable: Optional[bool] = None
    https_valid: Optional[bool] = None
    domain_age_days: Optional[int] = None
    registrar: Optional[str] = None
    company_name_on_site: Optional[bool] = None
    notes: List[str] = field(default_factory=list)
    search_summary: Optional[str] = None


@dataclass
class RiskAssessment:
    score: int
    level: str  # LOW / MEDIUM / HIGH
    reasons: List[str]
    recommendations: List[str]
