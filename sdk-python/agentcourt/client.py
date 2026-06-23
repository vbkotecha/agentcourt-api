"""
AgentCourt client — dispute resolution for agent commerce.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json
import urllib.request
import urllib.error

from .exceptions import PaymentRequiredError


DEFAULT_BASE_URL = "https://agentcourt-api-production.up.railway.app"


@dataclass
class Evidence:
    """Structured evidence for a dispute."""
    type: str
    source: str
    claimed_fact: str
    timestamp: str = ""
    hash: Optional[str] = None


@dataclass
class Dispute:
    """A dispute to file with AgentCourt."""
    policy: str
    claim: str
    desired_remedy: str
    claimant: str = "anonymous"
    respondent: str = "counterparty"
    contract_obligations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "policy": self.policy,
            "claim": self.claim,
            "claimant": self.claimant,
            "respondent": self.respondent,
            "desired_remedy": self.desired_remedy,
            "contract": {
                "parties": [self.claimant, self.respondent],
                "obligations": self.contract_obligations or [self.claim],
            },
            "metadata": self.metadata,
            "evidence": self.evidence,
        }


@dataclass
class Ruling:
    """The result of a dispute resolution."""
    ruling: str
    confidence: float
    case_id: str = ""
    reasoning: str = ""
    policy: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict) -> "Ruling":
        return cls(
            ruling=data.get("ruling", "unknown"),
            confidence=data.get("confidence", 0.0),
            case_id=data.get("case_id", ""),
            reasoning=data.get("reasoning", ""),
            policy=data.get("policy", ""),
            raw=data,
        )


@dataclass
class Policy:
    """A dispute resolution policy template."""
    name: str
    description: str = ""
    version: str = ""
    rule_count: int = 0
    rules: List[Dict[str, Any]] = field(default_factory=list)


class AgentCourt:
    """
    AgentCourt client for filing and resolving disputes.

    Args:
        base_url: AgentCourt API URL (default: production)
        api_key: Optional API key for paid tier (not required for free tier)

    Example:
        court = AgentCourt()
        ruling = court.file_dispute(
            policy="api-quality",
            claim="Wrong response format",
            desired_remedy="full_refund",
            metadata={"response_received": True, "schema_matches": False},
        )
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            if e.code == 402:
                challenge = e.headers.get("payment-required", "")
                raise PaymentRequiredError(
                    "Payment required. You may have exceeded the free tier (100 disputes/month). "
                    "Include x402 payment or wait for monthly reset.",
                    payment_challenge=challenge,
                ) from e
            raise Exception(f"AgentCourt API error {e.code}: {error_body}") from e

    def file_dispute(
        self,
        policy: str,
        claim: str,
        desired_remedy: str = "full_refund",
        claimant: str = "agent",
        respondent: str = "counterparty",
        contract_obligations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> Ruling:
        """
        File a dispute and get a deterministic ruling.

        Args:
            policy: Policy template (api-quality, freelance-delivery, etc.)
            claim: What went wrong
            desired_remedy: full_refund, partial_refund, or no_payout
            claimant: Who is filing
            respondent: Who is being disputed
            contract_obligations: What was agreed
            metadata: Structured facts about the dispute
            evidence: Supporting evidence

        Returns:
            Ruling object with ruling, confidence, and case_id
        """
        dispute = Dispute(
            policy=policy,
            claim=claim,
            desired_remedy=desired_remedy,
            claimant=claimant,
            respondent=respondent,
            contract_obligations=contract_obligations or [],
            metadata=metadata or {},
            evidence=evidence or [],
        )
        result = self._request("POST", "/v1/disputes", dispute.to_dict())
        return Ruling.from_response(result)

    def list_policies(self) -> List[Policy]:
        """List all available policy templates."""
        result = self._request("GET", "/v1/policies")
        if isinstance(result, list):
            return [
                Policy(
                    name=p.get("name", ""),
                    description=p.get("description", ""),
                    rule_count=p.get("rule_count", 0),
                    version=p.get("version", ""),
                )
                for p in result
            ]
        return []

    def get_policy(self, name: str) -> Policy:
        """Get details for a specific policy."""
        result = self._request("GET", f"/v1/policies/{name}")
        return Policy(
            name=result.get("name", name),
            description=result.get("description", ""),
            version=result.get("version", ""),
            rule_count=len(result.get("rules", [])),
            rules=result.get("rules", []),
        )

    def get_case(self, case_id: str) -> dict:
        """Retrieve a filed case by ID."""
        return self._request("GET", f"/v1/cases/{case_id}")

    def list_cases(self, limit: int = 10) -> List[dict]:
        """List recent cases."""
        return self._request("GET", f"/v1/cases?limit={limit}")

    def health(self) -> dict:
        """Check API health."""
        return self._request("GET", "/health")
