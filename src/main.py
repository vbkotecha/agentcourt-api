import os
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

"""
AgentCourt v1 — Policy-Driven Dispute Resolution API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import json
import sys
import urllib.request
import urllib.error

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.policy_engine import (
    evaluate_dispute,
    load_policy,
    list_policies,
    score_evidence,
    extract_facts,
    evaluate_rules,
    generate_ruling,
    calculate_confidence,
)

app = FastAPI(
    title="AgentCourt",
    version="1.4.0",
    description="""Policy-driven dispute resolution API for agent commerce.

Submit evidence, apply policy rules, get a deterministic ruling in under 500ms.

**7 policy templates** | **39 rules** | **$0.05/dispute via x402 (USDC on Base)** | **Free tier: 100/month**

When AI agents transact and things go wrong, AgentCourt delivers the ruling.
Same evidence + same policy = same ruling. Every time. No escrow, no courtroom theater.
""",
    servers=[
        {"url": "https://agentcourt-api-production.up.railway.app", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Local development"},
    ],
    tags_metadata=[
        {"name": "Disputes", "description": "File and resolve disputes with structured evidence"},
        {"name": "Policies", "description": "List and inspect available policy templates"},
        {"name": "Cases", "description": "Browse resolved cases and verdicts"},
        {"name": "x402", "description": "x402 payment manifest for agent discovery"},
        {"name": "Health", "description": "Service health and status"},
    ],
    contact={
        "name": "AgentCourt",
        "url": "https://github.com/vbkotecha/agentcourt-api",
        "email": "agentcourt@agentmail.to",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/vbkotecha/agentcourt-api/blob/main/LICENSE",
    },
    terms_of_service="https://github.com/vbkotecha/agentcourt-api/blob/main/LICENSE",
)

# Enable CORS for landing page demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- x402 Payment Protocol (Base Mainnet) ---
# Every /v1/disputes call requires $0.05 USDC payment
X402_WALLET = os.environ.get("X402_WALLET", "0x9863aB6242663FCc84c33632741711dB78f8Fd15")
X402_NETWORK = "eip155:8453"  # Base Mainnet
X402_FACILITATOR_URL = os.environ.get("X402_FACILITATOR_URL", "https://api.cdp.coinbase.com/platform/v2/x402")
X402_PRICE = os.environ.get("X402_PRICE", "$0.05")

try:
    from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption, CreateHeadersAuthProvider
    from x402.http.middleware.fastapi import PaymentMiddlewareASGI
    from x402.http.types import RouteConfig
    from x402.mechanisms.evm.exact import ExactEvmServerScheme
    from x402.server import x402ResourceServer
    from x402_payment import create_cdp_auth_headers, CDP_FACILITATOR_URL

    auth_provider = CreateHeadersAuthProvider(create_cdp_auth_headers)

    facilitator = HTTPFacilitatorClient(
        FacilitatorConfig(
            url=CDP_FACILITATOR_URL,
            auth_provider=auth_provider,
        )
    )
    payment_server = x402ResourceServer(facilitator)
    payment_server.register(X402_NETWORK, ExactEvmServerScheme())

    payment_routes = {
        "POST /v1/disputes": RouteConfig(
            accepts=[
                PaymentOption(
                    scheme="exact",
                    pay_to=X402_WALLET,
                    price=X402_PRICE,
                    network=X402_NETWORK,
                ),
            ],
            mime_type="application/json",
            description="Submit a dispute for policy-driven ruling",
            extensions={
                "bazaar": {
                    "discoverable": True,
                    "category": "dispute-resolution",
                    "tags": ["dispute", "legal", "arbitration", "agent-commerce", "policy"],
                    "serviceName": "AgentCourt Dispute Resolution",
                    "inputSchema": {
                        "bodySchema": {
                            "policy": {"type": "string", "description": "Policy template name"},
                            "plaintiff": {"type": "string", "description": "Plaintiff address or ID"},
                            "respondent": {"type": "string", "description": "Respondent address or ID"},
                            "evidence": {"type": "array", "description": "Evidence items"}
                        }
                    },
                }
            },
        ),
    }

    app.add_middleware(
        PaymentMiddlewareASGI,
        routes=payment_routes,
        server=payment_server,
    )
    print(f"[x402] Payment middleware enabled — POST /v1/disputes costs {X402_PRICE} USDC on Base Mainnet", flush=True)
    X402_ENABLED = True
except ImportError as e:
    print(f"[x402] NOT installed — running in free mode. Error: {e}", flush=True)
    X402_ENABLED = False
except Exception as e:
    import traceback
    print(f"[x402] Failed to initialize — running in free mode. Error: {e}", flush=True)
    traceback.print_exc()
    X402_ENABLED = False

# --- Data directory ---
DATA_DIR = os.environ.get("AGENTCOURT_DATA_DIR", "/root/.letta/agentcourt/data")
os.makedirs(DATA_DIR, exist_ok=True)


# ─── Schemas ─────────────────────────────────────────────────────────────────

class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    type: str  # contract, message, payment, file, log, screenshot, commit, other
    source: str
    timestamp: str
    content_hash: Optional[str] = None
    content_uri: Optional[str] = None
    claimed_fact: str
    excerpt: Optional[str] = None
    reliability: Optional[str] = None  # high / medium / low
    notes: Optional[str] = None


class ContractTerms(BaseModel):
    parties: List[str]
    obligations: List[str]
    deadlines: Optional[List[str]] = None
    deliverables: Optional[List[str]] = None
    payment_terms: Optional[str] = None
    definitions: Optional[dict] = None
    raw_contract: Optional[str] = None


class DisputeRequest(BaseModel):
    case_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    claimant: str
    respondent: str
    contract: ContractTerms
    claim: str
    desired_remedy: str
    evidence: List[EvidenceItem]
    policy: str = "freelance-delivery"  # which policy template to use
    dispute_type: Optional[str] = None
    priority: Optional[str] = "normal"
    metadata: Optional[dict] = None  # for policy-specific facts (progress_pct, severity, etc.)


class RulingResponse(BaseModel):
    case_id: str
    status: str
    confidence: str
    ruling: str
    reasoning: str
    remedy: str
    facts_established: List[dict]
    facts_disputed: List[dict]
    facts_unknown: List[dict]
    matched_rule_id: Optional[str] = None
    policy_name: Optional[str] = None
    policy_version: Optional[str] = None
    evidence_scores: Optional[List[dict]] = None
    ruled_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    engine_version: str = "1.4.0"


# ─── Storage ─────────────────────────────────────────────────────────────────

def save_case(case_id: str, data: dict):
    path = os.path.join(DATA_DIR, f"{case_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_case(case_id: str) -> Optional[dict]:
    path = os.path.join(DATA_DIR, f"{case_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def list_cases(limit: int = 50) -> List[dict]:
    cases = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(DATA_DIR, fname)) as f:
                cases.append(json.load(f))
    return sorted(cases, key=lambda c: c.get("request", {}).get("created_at", ""), reverse=True)[:limit]


# ─── API Endpoints ───────────────────────────────────────────────────────────

@app.post("/v1/disputes", response_model=RulingResponse)
async def create_dispute(dispute: DisputeRequest):
    """Submit a dispute and receive a policy-driven ruling."""
    # Convert to dict for the engine
    dispute_dict = dispute.model_dump()

    # Save the case
    case_data = {
        "case_id": dispute.case_id,
        "claimant": dispute.claimant,
        "respondent": dispute.respondent,
        "claim": dispute.claim,
        "policy": dispute.policy,
        "dispute_type": dispute.dispute_type,
        "evidence_count": len(dispute.evidence),
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending",
    }
    save_case(dispute.case_id, {"request": case_data})

    # Evaluate the dispute through the policy engine
    try:
        ruling = evaluate_dispute(
            dispute=dispute_dict,
            evidence=[e.model_dump() for e in dispute.evidence],
            policy_name=dispute.policy,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")

    # Save the ruling
    case_data["status"] = ruling["status"]
    case_data["ruling"] = ruling
    save_case(dispute.case_id, {"request": case_data, "ruling": ruling})

    return RulingResponse(
        case_id=ruling["case_id"],
        status=ruling["status"],
        confidence=ruling["confidence"],
        ruling=ruling["ruling"],
        reasoning=ruling["reasoning"],
        remedy=ruling["remedy"],
        facts_established=ruling["facts_established"],
        facts_disputed=ruling["facts_disputed"],
        facts_unknown=ruling["facts_unknown"],
        matched_rule_id=ruling.get("matched_rule_id"),
        policy_name=ruling.get("policy_name"),
        policy_version=ruling.get("policy_version"),
        evidence_scores=ruling.get("evidence_scores"),
        ruled_at=ruling["ruled_at"],
        engine_version=ruling["engine_version"],
    )


@app.get("/v1/cases")
async def get_cases(limit: int = Query(50, ge=1, le=200)):
    """List all cases."""
    return list_cases(limit)


@app.get("/v1/cases/{case_id}")
async def get_case(case_id: str):
    """Get a specific case with its ruling."""
    case = load_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/v1/policies")
async def get_policies():
    """List all available policy templates."""
    return list_policies()


@app.get("/v1/policies/{policy_name}")
async def get_policy(policy_name: str):
    """Get details of a specific policy template."""
    try:
        return load_policy(policy_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")


@app.get("/v1/policies/{policy_name}/preview")
async def preview_policy_evaluation(
    policy_name: str,
    # Sample facts as query params for quick testing
    deliverable_accepted: Optional[str] = Query(None, description="true/false/null"),
    on_time: Optional[str] = Query(None, description="true/false"),
    has_delivery_evidence: Optional[str] = Query(None, description="true/false"),
):
    """Preview which rule would match given hypothetical facts."""
    try:
        policy = load_policy(policy_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_name}' not found")

    facts = {}
    if deliverable_accepted is not None:
        facts["deliverable_was_accepted"] = deliverable_accepted == "true" if deliverable_accepted != "null" else None
    if on_time is not None:
        facts["delivery_was_on_time"] = on_time == "true"
    if has_delivery_evidence is not None:
        facts["evidence_of_delivery"] = has_delivery_evidence == "true"

    matched = evaluate_rules(policy, facts)
    return {
        "policy": policy_name,
        "input_facts": facts,
        "matched_rule": matched.get("id"),
        "would_ruling": matched.get("ruling_template"),
        "predicted_confidence": matched.get("confidence"),
        "predicted_remedy": matched.get("remedy"),
    }


@app.get("/")
async def root():
    return {
        "name": "AgentCourt",
        "tagline": "The dispute layer for agent commerce",
        "version": "1.4.0",
        "endpoints": {
            "submit_dispute": "POST /v1/disputes",
            "list_policies": "GET /v1/policies",
            "get_case": "GET /v1/cases/{case_id}",
            "health": "GET /health",
            "docs": "GET /docs",
            "api_docs": "GET /api-docs",
        },
        "live": True,
    }


@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs_page():
    """Developer-friendly API documentation page."""
    docs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing", "docs.html")
    if os.path.exists(docs_path):
        with open(docs_path) as f:
            return f.read()
    return HTMLResponse(content="<h1>API Docs</h1><p>Visit <a href='/docs'>/docs</a> for Swagger.</p>")

@app.get("/demos", response_class=HTMLResponse)
async def demos_page():
    """Interactive dispute resolution demos."""
    demos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing", "demos.html")
    if os.path.exists(demos_path):
        with open(demos_path) as f:
            return f.read()
    return HTMLResponse(content="<h1>Demos</h1><p>Not found.</p>")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.4.0",
        "data_dir": DATA_DIR,
        "engine": "policy-engine-v1",
        "policies": [p["name"] for p in list_policies()],
    }


@app.get("/.well-known/x402")
async def x402_manifest():
    """x402 payment manifest for agent discovery."""
    return {
        "version": "1.0",
        "name": "AgentCourt",
        "description": "Policy-driven dispute resolution API for agent commerce",
        "network": "base-mainnet",
        "chain_id": "eip155:8453",
        "currency": "USDC",
        "endpoints": [
            {
                "path": "/v1/disputes",
                "method": "POST",
                "price": "$0.05",
                "description": "Create a dispute and receive a deterministic ruling",
            },
            {
                "path": "/v1/policies",
                "method": "GET",
                "price": "$0.00",
                "description": "List all available policy templates",
            },
            {
                "path": "/v1/policies/{policy_name}",
                "method": "GET",
                "price": "$0.00",
                "description": "Get details for a specific policy template",
            },
            {
                "path": "/v1/verdicts",
                "method": "GET",
                "price": "$0.00",
                "description": "Browse recent verdicts",
            },
            {
                "path": "/v1/disputes/preview",
                "method": "POST",
                "price": "$0.00",
                "description": "Preview ruling without creating a case (demo mode)",
            },
            {
                "path": "/v1/lcp/disputes",
                "method": "POST",
                "price": "$0.05",
                "description": "File an LCP-compliant dispute with automatic terms verification",
            },
            {
                "path": "/v1/lcp/check/{domain}",
                "method": "GET",
                "price": "$0.00",
                "description": "Check if a domain implements the Legal Context Protocol",
            },
            {
                "path": "/v1/lcp/verify/{domain}",
                "method": "GET",
                "price": "$0.00",
                "description": "Verify a domain's LCP terms hash",
            },
            {
                "path": "/.well-known/legal-context.json",
                "method": "GET",
                "price": "$0.00",
                "description": "AgentCourt's own LCP discovery document (Level 4)",
            },
        ],
        "free_tier": {
            "requests_per_month": 100,
            "description": "100 free disputes per month, then $0.05/dispute via x402",
        },
        "categories": ["Infrastructure & Tooling", "Dispute Resolution"],
        "payTo": "0x9863aB6242663FCc84c33632741711dB78f8Fd15",
        "contact": "https://github.com/vbkotecha/agentcourt-api",
        "website": "https://vbkotecha.github.io/agentcourt-api/",
        "license": "MIT",
    }


@app.get("/openapi.yaml", response_class=PlainTextResponse)
async def get_openapi_spec():
    """Serve the OpenAPI 3.0.3 spec for client generation tools."""
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    if spec_path.exists():
        return PlainTextResponse(spec_path.read_text(), media_type="application/yaml")
    raise HTTPException(status_code=404, detail="OpenAPI spec not found")


@app.get("/swagger", response_class=HTMLResponse)
async def swagger_ui():
    """Interactive Swagger UI for exploring the API."""
    return """<!DOCTYPE html>
<html><head>
<title>AgentCourt — Swagger UI</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css">
<style>body { margin: 0; }</style>
</head><body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
<script>
window.onload = function() {
  SwaggerUIBundle({
    url: '/openapi.yaml',
    dom_id: '#swagger-ui',
    deepLinking: true,
    tryItOutEnabled: true,
  });
};
</script>
</body></html>"""


@app.get("/v1/verdicts")
async def list_verdicts(limit: int = 50):
    """Public verdict dashboard — returns all resolved cases."""
    cases = list_cases(limit)
    verdicts = []
    for c in cases:
        r = c.get("ruling", {})
        req = c.get("request", {})
        verdicts.append({
            "case_id": r.get("case_id", req.get("case_id", "")),
            "policy": r.get("policy_name", req.get("policy", "")),
            "ruling": r.get("ruling", "")[:200],
            "confidence": r.get("confidence", ""),
            "remedy": r.get("remedy", ""),
            "matched_rule": r.get("matched_rule_id", ""),
            "claimant": req.get("claimant", ""),
            "respondent": req.get("respondent", ""),
            "facts_established": len(r.get("facts_established", [])),
            "evidence_count": len(r.get("evidence_scores", [])),
            "ruled_at": r.get("ruled_at", ""),
        })
    return {
        "total": len(verdicts),
        "verdicts": verdicts,
    }


# ─── LCP (Legal Context Protocol) Endpoints ──────────────────────────────────

from lcp_adapter import LCPAdapter, LCPDisputeRequest, LCPDiscoveryDocument

_lcp = LCPAdapter()


@app.get("/.well-known/legal-context.json")
async def lcp_discovery():
    """LCP Level 4 Discovery Document for AgentCourt.

    Makes AgentCourt's legal terms discoverable at the standardized LCP URL.
    Any agent can find our terms, verify them, and know how to file disputes.
    """
    return _lcp.get_discovery_document()


@app.get("/.well-known/dispute-services.json")
async def lcp_dispute_catalog():
    """LCP dispute services catalog.

    Programmatic catalog of AgentCourt dispute resolution offerings.
    Allows agents to browse policies, parameters, and pricing.
    """
    return _lcp.get_dispute_services_catalog()


@app.get("/terms.md", response_class=PlainTextResponse)
async def lcp_terms_document():
    """AgentCourt terms document (referenced by LCP discovery)."""
    return PlainTextResponse(_lcp.get_terms_document(), media_type="text/markdown")


@app.get("/dispute-resolution-rules.md", response_class=PlainTextResponse)
async def lcp_dispute_rules():
    """AgentCourt dispute resolution rules (referenced by LCP discovery)."""
    return PlainTextResponse(_lcp.get_dispute_rules_document(), media_type="text/markdown")


class LCPDisputeBody(BaseModel):
    """Request body for filing an LCP-compliant dispute."""
    service_domain: str = Field(..., description="Domain of the service being disputed (LCP discovery will be fetched)")
    claimant: str
    respondent: str
    claim: str
    desired_remedy: str
    evidence: List[EvidenceItem]
    terms_content: Optional[str] = Field(None, description="Raw terms document content for hash verification")
    policy_override: Optional[str] = Field(None, description="Override automatic policy selection")
    metadata: Optional[dict] = None


@app.post("/v1/lcp/disputes")
async def file_lcp_dispute(body: LCPDisputeBody):
    """File a dispute using LCP context.

    Fetches the LCP discovery document from the service domain,
    verifies terms hash if provided, maps to appropriate AgentCourt policy,
    and resolves the dispute with full LCP metadata.
    """
    terms_bytes = body.terms_content.encode() if body.terms_content else None

    try:
        lcp_request = LCPDisputeRequest(
            service_domain=body.service_domain,
            claimant=body.claimant,
            respondent=body.respondent,
            claim=body.claim,
            desired_remedy=body.desired_remedy,
            evidence=[e.model_dump() for e in body.evidence],
            terms_content=terms_bytes,
            policy_override=body.policy_override,
            metadata=body.metadata,
        )
        dispute_dict = lcp_request.resolve()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LCP resolution failed: {str(e)}")

    # Evaluate through the policy engine
    try:
        ruling = evaluate_dispute(
            dispute=dispute_dict,
            evidence=dispute_dict["evidence"],
            policy_name=dispute_dict["policy"],
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")

    # Save case with LCP metadata
    case_id = str(uuid.uuid4())[:12]
    case_data = {
        "case_id": case_id,
        "claimant": body.claimant,
        "respondent": body.respondent,
        "claim": body.claim,
        "policy": dispute_dict["policy"],
        "dispute_type": "lcp-compliant",
        "evidence_count": len(body.evidence),
        "created_at": datetime.utcnow().isoformat(),
        "status": ruling["status"],
        "lcp_metadata": dispute_dict.get("metadata", {}),
    }
    save_case(case_id, {"request": case_data, "ruling": ruling})

    return {
        **ruling,
        "case_id": case_id,
        "lcp_verified": dispute_dict.get("metadata", {}).get("lcp_terms_verified", False),
        "lcp_domain": body.service_domain,
        "lcp_policy_selected": dispute_dict["policy"],
    }


@app.get("/v1/lcp/check/{domain}")
async def check_domain_lcp(domain: str):
    """Check if a domain implements LCP and inspect its discovery document.

    Useful for agents to verify a counterparty's legal context before transacting.
    """
    return LCPAdapter.check_domain_lcp(domain)


@app.get("/v1/lcp/verify/{domain}")
async def verify_domain_terms(
    domain: str,
    terms_url: Optional[str] = Query(None, description="Override terms URL to verify"),
):
    """Verify a domain's LCP terms hash.

    Fetches the terms document and checks it against the published atrHash.
    """
    discovery = LCPDiscoveryDocument.fetch(domain)
    result = {
        "domain": domain,
        "has_hash": bool(discovery.atr_hash),
        "atr_hash": discovery.atr_hash,
        "terms_url": terms_url or discovery.terms_url,
    }

    if discovery.atr_hash and (terms_url or discovery.terms_url):
        try:
            req = urllib.request.Request(terms_url or discovery.terms_url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                terms_content = resp.read()
            result["hash_verified"] = discovery.verify_terms_hash(terms_content)
            result["terms_size_bytes"] = len(terms_content)
        except Exception as e:
            result["hash_verified"] = False
            result["error"] = f"Could not fetch terms: {e}"
    else:
        result["hash_verified"] = None
        result["note"] = "No atrHash to verify against"

    return result


@app.get("/.well-known/agent.json")
async def agent_json():
    """Agent discovery manifest for AgentCourt."""
    return {
        "name": "AgentCourt",
        "version": "1.4.0",
        "description": "Policy-driven dispute resolution API for agent commerce",
        "url": "https://api.agentcourt.to",
        "capabilities": ["dispute-resolution", "policy-evaluation", "verdict-tracking"],
        "payment": {"protocol": "x402", "currency": "USDC", "chain": "base-mainnet"},
        "endpoints": {
            "dispute": "/v1/disputes",
            "policies": "/v1/policies",
            "verdicts": "/v1/verdicts",
            "lcp_dispute": "/v1/lcp/disputes"
        },
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """LLM-friendly service description."""
    return PlainTextResponse("""# AgentCourt
> Policy-driven dispute resolution API for agent commerce

## Overview
AgentCourt resolves disputes between AI agents using deterministic policy templates. Submit a dispute, receive a ruling with confidence score, reasoning, and remedy.

## Authentication
No API keys. Uses x402 payment protocol — agents pay per request in USDC on Base.

## Endpoints
- POST /v1/disputes — Submit a dispute ($0.05)
- GET /v1/policies — List policy templates (free)
- GET /v1/policies/{name} — Get policy details (free)
- GET /v1/verdicts — Browse verdicts (free)
- POST /v1/disputes/preview — Preview ruling (free)
- POST /v1/lcp/disputes — File LCP-compliant dispute ($0.05)
- GET /.well-known/legal-context.json — LCP discovery (free)
- GET /.well-known/dispute-services.json — Dispute catalog (free)
- GET /health — Service health (free)
- GET /docs — OpenAPI docs (free)

## Pricing
$0.05 per dispute filing. Free for policy browsing, verdicts, and previews.

## Payment
x402 protocol with CDP Facilitator. USDC on Base mainnet (chain 8453).
""", media_type="text/plain")


@app.get("/schema.json")
async def schema_json():
    """JSON schema for AgentCourt API."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AgentCourt API",
        "version": "1.4.0",
        "description": "Dispute resolution API for agent commerce",
        "base_url": "https://api.agentcourt.to",
        "endpoints": [
            {
                "path": "/v1/disputes",
                "method": "POST",
                "price": "$0.05",
                "description": "Create a dispute and receive a deterministic ruling",
                "request_schema": {
                    "type": "object",
                    "required": ["claimant", "respondent", "claim", "desired_remedy", "evidence"],
                    "properties": {
                        "claimant": {"type": "string"},
                        "respondent": {"type": "string"},
                        "claim": {"type": "string"},
                        "desired_remedy": {"type": "string"},
                        "evidence": {"type": "array", "items": {"type": "object"}},
                        "policy": {"type": "string", "description": "Optional policy override"}
                    }
                }
            },
            {
                "path": "/v1/policies",
                "method": "GET",
                "price": "$0.00",
                "description": "List all available policy templates"
            }
        ]
    }


@app.get("/manifest.json")
async def manifest_json():
    """Service manifest for discovery platforms."""
    return {
        "name": "AgentCourt",
        "version": "1.4.0",
        "description": "Policy-driven dispute resolution API for agent commerce on Base",
        "base_url": "https://api.agentcourt.to",
        "payment": {
            "protocol": "x402",
            "price_per_dispute": "$0.05",
            "currency": "USDC",
            "chain": "base-mainnet",
            "chain_id": 8453
        },
        "discovery": {
            "agent_json": "/.well-known/agent.json",
            "llms_txt": "/llms.txt",
            "x402_manifest": "/.well-known/x402",
            "lcp_discovery": "/.well-known/legal-context.json",
            "schema": "/schema.json",
            "openapi": "/docs"
        }
    }


@app.get("/verdicts", response_class=HTMLResponse)
async def verdict_dashboard():
    """Public verdict dashboard HTML page."""
    cases = list_cases(50)
    rows = ""
    for c in cases:
        r = c.get("ruling", {})
        req = c.get("request", {})
        conf = r.get("confidence", "")
        conf_color = {"high": "#6ee7b7", "medium": "#fbbf24", "low": "#f87171"}.get(conf, "#9aa9c7")
        cid = r.get("case_id", req.get("case_id", ""))
        pol = r.get("policy_name", req.get("policy", ""))
        claimant = req.get("claimant", "")
        respondent = req.get("respondent", "")
        rule = r.get("matched_rule_id", "")
        remedy = r.get("remedy", "")
        ruled = r.get("ruled_at", "")[:19]
        rows += f"""
        <tr>
          <td><code>{cid[:12] if cid else ''}</code></td>
          <td>{pol}</td>
          <td>{claimant}</td>
          <td>{respondent}</td>
          <td style="color:{conf_color};font-weight:600">{conf.upper()}</td>
          <td>{rule}</td>
          <td>{remedy}</td>
          <td style="color:var(--muted);font-size:13px">{ruled}</td>
        </tr>"""

    if not cases:
        rows = """<tr><td colspan="8" style="text-align:center;padding:60px;color:#9aa9c7">
            No disputes resolved yet. Be the first — POST to /v1/disputes
        </td></tr>"""

    high_count = len([c for c in cases if c.get("ruling", {}).get("confidence") == "high"])
    rules_set = set(c.get("ruling", {}).get("matched_rule_id", "") for c in cases if c.get("ruling", {}).get("matched_rule_id"))
    policies_set = set(c.get("ruling", {}).get("policy_name", c.get("request", {}).get("policy", "")) for c in cases)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentCourt — Verdict Dashboard</title>
  <style>
    :root {{ --bg:#07111f; --panel:rgba(13,23,41,.88); --border:rgba(143,168,255,.16); --text:#e8edf8; --muted:#9aa9c7; --accent:#7c5cff; --accent-2:#31d0ff; }}
    * {{ box-sizing:border-box; }}
    body {{ background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:40px 20px; }}
    .container {{ max-width:1200px; margin:0 auto; }}
    h1 {{ font-size:32px; margin:0 0 8px; }}
    h1 span {{ color:var(--accent-2); }}
    .subtitle {{ color:var(--muted); margin:0 0 32px; font-size:16px; }}
    .stats {{ display:flex; gap:24px; margin-bottom:32px; flex-wrap:wrap; }}
    .stat {{ background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:20px 28px; }}
    .stat-value {{ font-size:28px; font-weight:700; color:var(--accent-2); }}
    .stat-label {{ color:var(--muted); font-size:13px; text-transform:uppercase; letter-spacing:1px; }}
    table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:14px; overflow:hidden; border:1px solid var(--border); }}
    th {{ text-align:left; padding:14px 16px; background:rgba(124,92,255,.08); color:var(--accent); font-size:13px; text-transform:uppercase; letter-spacing:.5px; }}
    td {{ padding:12px 16px; border-top:1px solid var(--border); font-size:14px; }}
    tr:hover td {{ background:rgba(124,92,255,.04); }}
    .header-link {{ display:inline-block; margin-top:16px; color:var(--accent-2); text-decoration:none; font-size:14px; }}
    .header-link:hover {{ text-decoration:underline; }}
    code {{ background:rgba(0,0,0,.3); padding:2px 6px; border-radius:4px; font-size:12px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>AgentCourt <span>Verdict Dashboard</span></h1>
    <p class="subtitle">Every ruling is public. Every decision is auditable. Policy-driven, not prediction-driven.</p>
    <div class="stats">
      <div class="stat">
        <div class="stat-value">{len(cases)}</div>
        <div class="stat-label">Total Cases</div>
      </div>
      <div class="stat">
        <div class="stat-value">{high_count}</div>
        <div class="stat-label">High Confidence</div>
      </div>
      <div class="stat">
        <div class="stat-value">{len(rules_set)}</div>
        <div class="stat-label">Rules Triggered</div>
      </div>
      <div class="stat">
        <div class="stat-value">{len(policies_set)}</div>
        <div class="stat-label">Policies Used</div>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Case ID</th>
          <th>Policy</th>
          <th>Claimant</th>
          <th>Respondent</th>
          <th>Confidence</th>
          <th>Rule</th>
          <th>Remedy</th>
          <th>Ruled At</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>
    <a class="header-link" href="/docs">API Docs →</a>
    &nbsp;&nbsp;
    <a class="header-link" href="/health">Health Check →</a>
  </div>
</body>
</html>"""
