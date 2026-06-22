"""
AgentCourt Python SDK
=====================
pip install agentcourt  (coming soon)
or copy this file into your project.

Usage:
    from agentcourt import AgentCourt

    court = AgentCourt()  # uses default live API

    # Resolve a dispute
    ruling = court.resolve(
        policy="freelance-delivery",
        claim="Work never delivered",
        claimant="my_agent",
        respondent="freelancer_bot",
        desired_remedy="full_refund",
        evidence=[
            {"type": "contract", "source": "agreement.pdf",
             "timestamp": "2026-06-01", "claimed_fact": "Logo due June 20"},
            {"type": "log", "source": "email.pdf",
             "timestamp": "2026-06-22", "claimed_fact": "No deliverable submitted"},
        ]
    )

    print(ruling.remedy)      # "full_refund"
    print(ruling.confidence)  # "high"
    print(ruling.case_id)     # "abc123"

    # List available policies
    policies = court.list_policies()

    # Get a previous verdict
    verdict = court.get_verdict(ruling.case_id)
"""

import json
import urllib.request
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


DEFAULT_API = "https://agentcourt-api-production.up.railway.app"


@dataclass
class Evidence:
    """Evidence item for a dispute."""
    type: str
    claimed_fact: str
    source: str = ""
    timestamp: str = ""


@dataclass
class Ruling:
    """Parsed ruling from AgentCourt."""
    case_id: str
    status: str
    matched_rule: str
    remedy: str
    confidence: str
    ruling_text: str
    reasoning: str
    policy_name: str
    evidence_scores: List[Dict] = field(default_factory=list)
    facts_established: List[Dict] = field(default_factory=list)
    facts_disputed: List[Dict] = field(default_factory=list)
    facts_unknown: List[Dict] = field(default_factory=list)
    ruled_at: str = ""
    engine_version: str = ""
    raw: Dict = field(default_factory=dict)


@dataclass
class Policy:
    """Policy template info."""
    name: str
    version: str
    description: str
    rules_count: int


class AgentCourt:
    """
    AgentCourt API client.

    Args:
        api_url: API base URL (defaults to live production)
        timeout: Request timeout in seconds
    """

    def __init__(self, api_url: str = DEFAULT_API, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, data: Dict) -> Dict:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{self.api_url}{path}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())

    def _get(self, path: str) -> Any:
        req = urllib.request.Request(f"{self.api_url}{path}")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())

    def resolve(
        self,
        policy: str,
        claim: str,
        claimant: str,
        respondent: str,
        desired_remedy: str = "full_refund",
        evidence: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
        contract: Optional[Dict] = None,
    ) -> Ruling:
        """
        Submit a dispute and get a ruling.

        Args:
            policy: Policy template name (e.g. "freelance-delivery")
            claim: Description of the dispute
            claimant: Party filing the claim
            respondent: Party being claimed against
            desired_remedy: What the claimant wants
            evidence: List of evidence items
            metadata: Structured facts (primary input for rule matching)
            contract: Contract details

        Returns:
            Ruling object with remedy, confidence, and details

        Example:
            ruling = court.resolve(
                policy="sla-monitoring",
                claim="SLA violation",
                claimant="client",
                respondent="provider",
                metadata={
                    "required_uptime": 99.9,
                    "actual_uptime": 98.5,
                    "monitoring_period_confirmed": True
                },
                evidence=[
                    {"type": "contract", "source": "sla.pdf",
                     "timestamp": "2026-06-01",
                     "claimed_fact": "SLA requires 99.9 percent uptime"},
                ]
            )
        """
        payload = {
            "policy": policy,
            "claim": claim,
            "claimant": claimant,
            "respondent": respondent,
            "desired_remedy": desired_remedy,
            "evidence": evidence or [],
        }
        if metadata:
            payload["metadata"] = metadata
        if contract:
            payload["contract"] = contract

        raw = self._post("/v1/disputes", payload)

        return Ruling(
            case_id=raw.get("case_id", ""),
            status=raw.get("status", ""),
            matched_rule=raw.get("matched_rule_id", ""),
            remedy=raw.get("remedy", ""),
            confidence=raw.get("confidence", ""),
            ruling_text=raw.get("ruling", ""),
            reasoning=raw.get("reasoning", ""),
            policy_name=raw.get("policy_name", ""),
            evidence_scores=raw.get("evidence_scores", []),
            facts_established=raw.get("facts_established", []),
            facts_disputed=raw.get("facts_disputed", []),
            facts_unknown=raw.get("facts_unknown", []),
            ruled_at=raw.get("ruled_at", ""),
            engine_version=raw.get("engine_version", ""),
            raw=raw,
        )

    def list_policies(self) -> List[Policy]:
        """List all available policy templates."""
        raw = self._get("/v1/policies")
        if isinstance(raw, list):
            return [
                Policy(
                    name=p.get("name", ""),
                    version=p.get("version", ""),
                    description=p.get("description", ""),
                    rules_count=p.get("rules_count", 0),
                )
                for p in raw
            ]
        return []

    def get_policy(self, name: str) -> Dict:
        """Get details of a specific policy template."""
        return self._get(f"/v1/policies/{name}")

    def get_verdict(self, case_id: str) -> Dict:
        """Look up a previous verdict by case ID."""
        return self._get(f"/v1/cases/{case_id}")

    def list_verdicts(self) -> Dict:
        """List all stored verdicts."""
        return self._get("/v1/verdicts")

    def health(self) -> Dict:
        """Check API health."""
        return self._get("/health")


# ─── Convenience functions ────────────────────────────────────────────────

def resolve_dispute(
    policy: str,
    claim: str,
    claimant: str,
    respondent: str,
    **kwargs,
) -> Ruling:
    """Quick one-liner to resolve a dispute without creating a client."""
    return AgentCourt().resolve(
        policy=policy, claim=claim, claimant=claimant,
        respondent=respondent, **kwargs
    )


# ─── Example usage ────────────────────────────────────────────────────────

if __name__ == "__main__":
    court = AgentCourt()

    # Health check
    health = court.health()
    print(f"API: {health['status']} | {len(health['policies'])} policies\n")

    # List policies
    policies = court.list_policies()
    for p in policies:
        print(f"  {p.name}: {p.description[:60]}... ({p.rules_count} rules)")

    # Resolve a dispute
    print("\n--- Resolving dispute ---")
    ruling = court.resolve(
        policy="freelance-delivery",
        claim="Logo design never delivered",
        claimant="client_agent",
        respondent="freelancer_bot",
        desired_remedy="full_refund",
        evidence=[
            {"type": "contract", "source": "agreement.pdf",
             "timestamp": "2026-06-01", "claimed_fact": "Logo due June 20"},
            {"type": "log", "source": "email.pdf",
             "timestamp": "2026-06-22", "claimed_fact": "No deliverable submitted"},
        ],
        contract={
            "parties": ["client_agent", "freelancer_bot"],
            "obligations": ["Deliver logo design"],
            "deadlines": ["2026-06-20"],
        },
    )

    print(f"  Case: {ruling.case_id}")
    print(f"  Status: {ruling.status}")
    print(f"  Rule: {ruling.matched_rule}")
    print(f"  Remedy: {ruling.remedy}")
    print(f"  Confidence: {ruling.confidence}")
