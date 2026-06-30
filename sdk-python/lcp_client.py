"""
AgentCourt LCP Client Library.

Python client for agents to:
1. Check any domain's LCP discovery document
2. Verify terms hashes
3. File LCP-compliant disputes through AgentCourt
4. Resolve disputes with full legal context

Installation:
    Copy this file or pip install agentcourt (coming soon)

Quick Start:
    from lcp_client import AgentCourtLCP

    client = AgentCourtLCP()

    # Check a domain's LCP status
    info = client.check_domain("api.example.com")

    # File a dispute with LCP context
    ruling = client.dispute(
        service_domain="api.example.com",
        claimant="my-agent",
        respondent="example.com",
        claim="Non-delivery of API credits",
        desired_remedy="Full refund of $50 USDC",
        evidence=[...],
    )
"""

import json
import hashlib
import urllib.request
import urllib.parse
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Evidence:
    """Structured evidence item for disputes."""
    type: str  # contract, message, payment, file, log, screenshot, commit, other
    source: str
    timestamp: str
    claimed_fact: str
    content_hash: Optional[str] = None
    content_uri: Optional[str] = None
    excerpt: Optional[str] = None
    reliability: Optional[str] = None  # high / medium / low
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class LCPDiscoveryInfo:
    """Parsed LCP discovery document from a domain."""
    domain: str
    lcp_enabled: bool
    terms_url: Optional[str] = None
    atr_hash: Optional[str] = None
    acceptance_required: bool = False
    has_dispute_resolution: bool = False
    dispute_method: Optional[str] = None
    jurisdiction: Optional[str] = None
    dispute_contact: Optional[str] = None
    dispute_api: Optional[str] = None
    terms_format: Optional[str] = None
    full_document: Optional[dict] = None
    error: Optional[str] = None

    def summary(self) -> str:
        if not self.lcp_enabled:
            return f"{self.domain}: LCP not enabled ({self.error})"
        parts = [
            f"{self.domain}: LCP enabled",
            f"  Terms: {self.terms_url}",
            f"  Hash: {'Yes' if self.atr_hash else 'No (Level 1)'}",
            f"  Acceptance required: {self.acceptance_required}",
        ]
        if self.has_dispute_resolution:
            parts.append(f"  Dispute method: {self.dispute_method}")
            parts.append(f"  Jurisdiction: {self.jurisdiction}")
        return "\n".join(parts)


@dataclass
class Ruling:
    """AgentCourt dispute ruling."""
    case_id: str
    status: str
    confidence: str
    ruling: str
    reasoning: str
    remedy: str
    facts_established: List[dict] = field(default_factory=list)
    facts_disputed: List[dict] = field(default_factory=list)
    facts_unknown: List[dict] = field(default_factory=list)
    matched_rule_id: Optional[str] = None
    policy_name: Optional[str] = None
    lcp_verified: bool = False
    lcp_domain: Optional[str] = None
    ruled_at: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"Case {self.case_id}: {self.status} ({self.confidence} confidence)\n"
            f"Ruling: {self.ruling}\n"
            f"Remedy: {self.remedy}\n"
            f"Policy: {self.policy_name} | Rule: {self.matched_rule_id}\n"
            f"LCP verified: {self.lcp_verified}"
        )


class AgentCourtLCP:
    """
    Client for LCP-compliant dispute resolution via AgentCourt.

    Args:
        api_url: AgentCourt API URL (default: production)
        api_key: Optional API key for authentication
    """

    def __init__(
        self,
        api_url: str = "https://api.agentcourt.to",
        api_key: Optional[str] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Make an HTTP request to AgentCourt API."""
        url = f"{self.api_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        for k, v in headers.items():
            req.add_header(k, v)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                error_data = json.loads(error_body)
                raise Exception(f"API error {e.code}: {error_data.get('detail', error_body)}")
            except json.JSONDecodeError:
                raise Exception(f"API error {e.code}: {error_body}")

    def check_domain(self, domain: str) -> LCPDiscoveryInfo:
        """
        Check if a domain implements LCP.
        Fetches and parses their /.well-known/legal-context.json.

        Args:
            domain: The domain to check (e.g., "api.example.com")

        Returns:
            LCPDiscoveryInfo with all discovered legal context
        """
        result = self._request("GET", f"/v1/lcp/check/{domain}")
        return LCPDiscoveryInfo(
            domain=result.get("domain", domain),
            lcp_enabled=result.get("lcp_enabled", False),
            terms_url=result.get("terms_url"),
            atr_hash=result.get("atr_hash"),
            acceptance_required=result.get("acceptance_required", False),
            has_dispute_resolution=result.get("has_dispute_resolution", False),
            dispute_method=result.get("dispute_method"),
            jurisdiction=result.get("jurisdiction"),
            dispute_contact=result.get("dispute_contact"),
            dispute_api=result.get("dispute_api"),
            full_document=result.get("full_document"),
            error=result.get("error"),
        )

    def verify_terms(self, domain: str) -> dict:
        """
        Verify a domain's LCP terms hash.
        Fetches the terms document and checks it against the published atrHash.

        Args:
            domain: The domain to verify

        Returns:
            Verification result dict
        """
        return self._request("GET", f"/v1/lcp/verify/{domain}")

    def dispute(
        self,
        service_domain: str,
        claimant: str,
        respondent: str,
        claim: str,
        desired_remedy: str,
        evidence: List[Evidence],
        terms_content: Optional[str] = None,
        policy_override: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Ruling:
        """
        File an LCP-compliant dispute through AgentCourt.

        Automatically:
        1. Fetches the service's LCP discovery document
        2. Verifies terms hash (if terms_content provided)
        3. Maps LCP dispute method to appropriate AgentCourt policy
        4. Resolves the dispute with deterministic ruling engine
        5. Returns ruling with full LCP metadata

        Args:
            service_domain: Domain of the disputed service
            claimant: Party filing the dispute
            respondent: Party being disputed
            claim: Description of the dispute
            desired_remedy: What the claimant wants
            evidence: List of Evidence items
            terms_content: Raw terms document (for hash verification)
            policy_override: Override automatic policy selection
            metadata: Additional metadata

        Returns:
            Ruling object with case details and outcome
        """
        body = {
            "service_domain": service_domain,
            "claimant": claimant,
            "respondent": respondent,
            "claim": claim,
            "desired_remedy": desired_remedy,
            "evidence": [e.to_dict() for e in evidence],
            "terms_content": terms_content,
            "policy_override": policy_override,
            "metadata": metadata,
        }

        result = self._request("POST", "/v1/lcp/disputes", data=body)
        return Ruling(
            case_id=result.get("case_id", ""),
            status=result.get("status", ""),
            confidence=result.get("confidence", ""),
            ruling=result.get("ruling", ""),
            reasoning=result.get("reasoning", ""),
            remedy=result.get("remedy", ""),
            facts_established=result.get("facts_established", []),
            facts_disputed=result.get("facts_disputed", []),
            facts_unknown=result.get("facts_unknown", []),
            matched_rule_id=result.get("matched_rule_id"),
            policy_name=result.get("policy_name"),
            lcp_verified=result.get("lcp_verified", False),
            lcp_domain=result.get("lcp_domain"),
            ruled_at=result.get("ruled_at"),
        )

    def list_policies(self) -> dict:
        """List all available AgentCourt dispute resolution policies."""
        return self._request("GET", "/v1/policies")

    def get_case(self, case_id: str) -> dict:
        """Get details of a specific case."""
        return self._request("GET", f"/v1/cases/{case_id}")

    def health(self) -> dict:
        """Check AgentCourt API health."""
        return self._request("GET", "/health")

    @staticmethod
    def compute_terms_hash(terms_content: str) -> str:
        """Compute the LCP atrHash for a terms document."""
        return "0x" + hashlib.sha256(terms_content.encode()).hexdigest()


# ─── Convenience Functions ───────────────────────────────────────────────────

def check_lcp(domain: str) -> LCPDiscoveryInfo:
    """Quick helper to check a domain's LCP status."""
    client = AgentCourtLCP()
    return client.check_domain(domain)


def file_dispute(
    service_domain: str,
    claimant: str,
    respondent: str,
    claim: str,
    desired_remedy: str,
    evidence: List[Evidence],
    **kwargs,
) -> Ruling:
    """Quick helper to file an LCP-compliant dispute."""
    client = AgentCourtLCP()
    return client.dispute(
        service_domain=service_domain,
        claimant=claimant,
        respondent=respondent,
        claim=claim,
        desired_remedy=desired_remedy,
        evidence=evidence,
        **kwargs,
    )
