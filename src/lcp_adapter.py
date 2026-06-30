"""
Legal Context Protocol (LCP) Adapter for AgentCourt.

This module bridges LCP-compliant transactions with AgentCourt's dispute resolution engine.
It allows agents to:
1. Verify LCP terms hash before filing disputes
2. File disputes using LCP discovery document metadata
3. Map LCP disputeResolution fields to AgentCourt policy templates
4. Return LCP-compliant dispute resolution results

Usage:
    from lcp_adapter import LCPAdapter
    adapter = LCPAdapter()
    dispute = adapter.file_lcp_dispute(...)
"""

import hashlib
import json
import urllib.request
from typing import Optional, Dict, List, Any
from datetime import datetime


# LCP Discovery Document URL pattern
LCP_WELL_KNOWN_PATH = "/.well-known/legal-context.json"

# Map LCP dispute methods to AgentCourt policies
LCP_METHOD_TO_POLICY = {
    "freelance": "freelance-delivery",
    "milestone": "milestone-payment",
    "bug bounty": "bug-bounty",
    "sla": "sla-monitoring",
    "commercial arbitration": "freelance-delivery",
    "dispute resolution service rules": "freelance-delivery",
    "mediation": "freelance-delivery",
}

# Default policy when no LCP method matches
DEFAULT_POLICY = "freelance-delivery"


class LCPDiscoveryDocument:
    """Represents an LCP discovery document fetched from /.well-known/legal-context.json"""

    def __init__(self, data: dict, domain: str):
        self.data = data
        self.domain = domain
        self.terms_url = data.get("terms")
        self.terms_format = data.get("termsFormat", "markdown")
        self.atr_hash = data.get("atrHash")
        self.acceptance_required = data.get("acceptanceRequired", False)
        self.dispute_resolution = data.get("disputeResolution", {})
        self.returns_url = data.get("returns")
        self.contact = data.get("contact", {})
        self.api_url = data.get("api")

    def verify_terms_hash(self, terms_content: bytes) -> bool:
        """Verify that the terms document matches the atrHash."""
        if not self.atr_hash:
            return False
        computed = "0x" + hashlib.sha256(terms_content).hexdigest()
        return computed.lower() == self.atr_hash.lower()

    def get_policy_template(self) -> str:
        """Map LCP dispute resolution method to AgentCourt policy."""
        method = self.dispute_resolution.get("method", "").lower()
        for key, policy in LCP_METHOD_TO_POLICY.items():
            if key in method:
                return policy
        return DEFAULT_POLICY

    def to_agentcourt_contract(self) -> dict:
        """Convert LCP discovery data to AgentCourt contract format."""
        return {
            "parties": [self.domain, "counterparty"],
            "obligations": [
                f"Transaction governed by terms at {self.terms_url}",
                f"Dispute resolution method: {self.dispute_resolution.get('method', 'Not specified')}",
            ],
            "definitions": {
                "lcp_terms_url": self.terms_url,
                "lcp_atr_hash": self.atr_hash,
                "lcp_jurisdiction": self.dispute_resolution.get("jurisdiction", "Not specified"),
                "lcp_acceptance_required": self.acceptance_required,
                "lcp_domain": self.domain,
            },
            "raw_contract": json.dumps(self.data, indent=2),
        }

    @classmethod
    def fetch(cls, domain: str) -> "LCPDiscoveryDocument":
        """Fetch and parse LCP discovery document from a domain."""
        url = f"https://{domain}{LCP_WELL_KNOWN_PATH}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return cls(data, domain)


class LCPDisputeRequest:
    """Builds an AgentCourt dispute request from LCP context."""

    def __init__(
        self,
        service_domain: str,
        claimant: str,
        respondent: str,
        claim: str,
        desired_remedy: str,
        evidence: List[dict],
        terms_content: Optional[bytes] = None,
        policy_override: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.service_domain = service_domain
        self.claimant = claimant
        self.respondent = respondent
        self.claim = claim
        self.desired_remedy = desired_remedy
        self.evidence = evidence
        self.terms_content = terms_content
        self.policy_override = policy_override
        self.metadata = metadata or {}
        self._discovery: Optional[LCPDiscoveryDocument] = None

    def resolve(self) -> dict:
        """Resolve the dispute request into AgentCourt API format."""
        # Fetch LCP discovery document
        try:
            self._discovery = LCPDiscoveryDocument.fetch(self.service_domain)
        except Exception as e:
            raise ValueError(f"Failed to fetch LCP discovery from {self.service_domain}: {e}")

        # Verify terms hash if provided
        terms_verified = False
        if self.terms_content and self._discovery.atr_hash:
            terms_verified = self._discovery.verify_terms_hash(self.terms_content)
            if not terms_verified:
                raise ValueError(
                    f"Terms hash mismatch: expected {self._discovery.atr_hash}, "
                    f"content does not match"
                )

        # Determine policy
        policy = self.policy_override or self._discovery.get_policy_template()

        # Build contract from LCP data
        contract = self._discovery.to_agentcourt_contract()

        # Enrich evidence with LCP context
        enriched_evidence = self.evidence.copy()
        enriched_evidence.append({
            "type": "contract",
            "source": f"LCP discovery at {self.service_domain}",
            "timestamp": datetime.utcnow().isoformat(),
            "content_hash": self._discovery.atr_hash,
            "content_uri": self._discovery.terms_url,
            "claimed_fact": f"LCP terms verified at {self.service_domain}",
            "excerpt": json.dumps(self._discovery.data, indent=2)[:500],
            "reliability": "high" if terms_verified else "medium",
        })

        # Build AgentCourt dispute request
        return {
            "claimant": self.claimant,
            "respondent": self.respondent,
            "contract": contract,
            "claim": self.claim,
            "desired_remedy": self.desired_remedy,
            "evidence": enriched_evidence,
            "policy": policy,
            "dispute_type": "lcp-compliant",
            "metadata": {
                **self.metadata,
                "lcp_domain": self.service_domain,
                "lcp_terms_url": self._discovery.terms_url,
                "lcp_atr_hash": self._discovery.atr_hash,
                "lcp_terms_verified": terms_verified,
                "lcp_jurisdiction": self._discovery.dispute_resolution.get("jurisdiction"),
                "lcp_dispute_method": self._discovery.dispute_resolution.get("method"),
            },
        }


class LCPAdapter:
    """
    Main LCP adapter. Provides methods for:
    - Fetching and inspecting LCP discovery documents
    - Filing LCP-compliant disputes through AgentCourt
    - Generating LCP-compatible discovery files for AgentCourt itself
    """

    AGENTCOURT_LCP_DISCOVERY = {
        "terms": "https://agentcourt.to/terms.md",
        "termsFormat": "markdown",
        "atrHash": None,  # Computed at runtime
        "acceptanceRequired": False,
        "disputeResolution": {
            "method": "AgentCourt Policy-Driven Resolution",
            "jurisdiction": "San Francisco, CA, USA",
            "contact": "disputes@agentcourt.to",
            "clauseId": None,  # Computed at runtime
            "source": "https://agentcourt.to/dispute-resolution-rules.md",
            "catalog": "https://api.agentcourt.to/.well-known/dispute-services.json",
        },
        "returns": "https://api.agentcourt.to/v1/cases",
        "contact": {
            "legal": "legal@agentcourt.to",
            "technical": "api@agentcourt.to",
        },
        "api": "https://api.agentcourt.to/v1/disputes",
    }

    AGENTCOURT_DISPUTE_SERVICES = {
        "version": "1.0",
        "provider": "AgentCourt",
        "description": "Policy-driven dispute resolution for agent commerce",
        "services": [
            {
                "id": "freelance-delivery",
                "name": "Freelance Delivery Dispute",
                "description": "Disputes over deliverables, deadlines, and quality for freelance contracts",
                "price": "$0.05 USDC on Base",
                "rules": 7,
                "avg_resolution_time": "< 500ms",
            },
            {
                "id": "milestone-payment",
                "name": "Milestone Payment Dispute",
                "description": "Disputes over milestone completion and payment release",
                "price": "$0.05 USDC on Base",
                "rules": 6,
                "avg_resolution_time": "< 500ms",
            },
            {
                "id": "bug-bounty",
                "name": "Bug Bounty Severity Dispute",
                "description": "Disputes over bug severity classification and bounty payout",
                "price": "$0.05 USDC on Base",
                "rules": 8,
                "avg_resolution_time": "< 500ms",
            },
            {
                "id": "sla-monitoring",
                "name": "SLA Violation Dispute",
                "description": "Disputes over service level agreement violations",
                "price": "$0.05 USDC on Base",
                "rules": 10,
                "avg_resolution_time": "< 500ms",
            },
        ],
        "api": "https://api.agentcourt.to/v1/disputes",
        "free_tier": "100 disputes/month free",
    }

    AGENTCOURT_TERMS_MD = """# AgentCourt Terms of Service

## Dispute Resolution Terms

### 1. Acceptance
By submitting a dispute to AgentCourt, both parties agree to these terms.

### 2. Resolution Process
AgentCourt resolves disputes using deterministic policy templates. The same evidence and policy always produce the same ruling.

### 3. Policy Templates
Disputes are resolved under one of the following policies:
- freelance-delivery (7 rules)
- milestone-payment (6 rules)
- bug-bounty (8 rules)
- sla-monitoring (10 rules)

### 4. Fees
- Free tier: 100 disputes per month
- Paid tier: $0.05 USDC per dispute (via x402 on Base Mainnet)

### 5. Evidence Standards
Evidence is weighted by type reliability:
- Payment receipts: High
- Written messages: Medium
- Verbal claims: Low

### 6. Jurisdiction
AgentCourt rulings are advisory. Parties may choose to enforce rulings through their own means (reputation systems, escrow release, marketplace bans).

### 7. No Escrow
AgentCourt does not hold funds. Rulings recommend remedies but do not execute them.

### 8. Confidentiality
Case data is stored on the AgentCourt server. Parties may request deletion.

### 9. No Legal Advice
AgentCourt provides algorithmic dispute resolution, not legal advice.

### 10. Version
Terms Version: 1.0 — June 30, 2026
"""

    AGENTCOURT_DISPUTE_RULES_MD = """# AgentCourt Dispute Resolution Rules

## Overview
AgentCourt resolves disputes using policy-driven templates. Each template contains rules that match against submitted evidence to produce deterministic rulings.

## Resolution Modes
1. **Auto-check**: Rule-based evaluation (< 500ms)
2. **Rubric scoring**: Evidence-weighted fact determination
3. **AI mediation**: LLM-assisted reasoning for complex cases
4. **Arbitration**: Multi-party review
5. **Human fallback**: Escalation to human reviewer

## Evidence Weighting
| Evidence Type | Reliability |
|---|---|
| Payment receipt | High |
| Written message | Medium |
| Code commit | High |
| Screenshot | Low |
| Verbal claim | Low |

## Ruling Format
Each ruling includes:
- Status (upheld / denied / partial)
- Confidence level (high / medium / low)
- Established facts
- Remedy recommendation
- Policy rule applied

## Version: 1.0 — June 30, 2026
"""

    def get_discovery_document(self) -> dict:
        """Get AgentCourt's own LCP discovery document."""
        discovery = self.AGENTCOURT_LCP_DISCOVERY.copy()
        # Compute hash of terms
        terms_bytes = self.AGENTCOURT_TERMS_MD.encode()
        discovery["atrHash"] = "0x" + hashlib.sha256(terms_bytes).hexdigest()

        # Compute dispute clause hash
        rules_bytes = self.AGENTCOURT_DISPUTE_RULES_MD.encode()
        clause_hash = hashlib.sha256(rules_bytes).hexdigest()
        discovery["disputeResolution"]["clauseId"] = f"sha256:0x{clause_hash}"

        return discovery

    def get_dispute_services_catalog(self) -> dict:
        """Get the dispute services catalog for LCP catalog field."""
        return self.AGENTCOURT_DISPUTE_SERVICES

    def get_terms_document(self) -> str:
        """Get the terms markdown document."""
        return self.AGENTCOURT_TERMS_MD

    def get_dispute_rules_document(self) -> str:
        """Get the dispute resolution rules markdown document."""
        return self.AGENTCOURT_DISPUTE_RULES_MD

    @staticmethod
    def check_domain_lcp(domain: str) -> dict:
        """
        Check if a domain implements LCP.
        Returns discovery document or error info.
        """
        try:
            discovery = LCPDiscoveryDocument.fetch(domain)
            return {
                "domain": domain,
                "lcp_enabled": True,
                "terms_url": discovery.terms_url,
                "atr_hash": discovery.atr_hash,
                "acceptance_required": discovery.acceptance_required,
                "has_dispute_resolution": bool(discovery.dispute_resolution),
                "dispute_method": discovery.dispute_resolution.get("method"),
                "jurisdiction": discovery.dispute_resolution.get("jurisdiction"),
                "dispute_contact": discovery.dispute_resolution.get("contact"),
                "dispute_api": discovery.dispute_resolution.get("source"),
                "full_document": discovery.data,
            }
        except urllib.error.HTTPError as e:
            return {
                "domain": domain,
                "lcp_enabled": False,
                "error": f"HTTP {e.code}: LCP discovery not found",
            }
        except Exception as e:
            return {
                "domain": domain,
                "lcp_enabled": False,
                "error": str(e),
            }

    @staticmethod
    def verify_terms(domain: str, terms_content: Optional[bytes] = None) -> dict:
        """
        Verify a domain's LCP terms.
        If terms_content provided, verify hash.
        """
        try:
            discovery = LCPDiscoveryDocument.fetch(domain)
            result = {
                "domain": domain,
                "has_terms": bool(discovery.terms_url),
                "has_hash": bool(discovery.atr_hash),
                "terms_url": discovery.terms_url,
                "atr_hash": discovery.atr_hash,
            }

            if terms_content and discovery.atr_hash:
                result["hash_verified"] = discovery.verify_terms_hash(terms_content)
            elif not discovery.atr_hash:
                result["hash_verified"] = None
                result["note"] = "No atrHash published — terms are Level 1 only"

            return result
        except Exception as e:
            return {"domain": domain, "error": str(e)}
