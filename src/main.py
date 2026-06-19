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
AgentCourt v1 — Ruling API
A single-endpoint dispute resolution system for autonomous agents.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

app = FastAPI(title="AgentCourt", version="0.1.0")

# --- x402 Payment Middleware ---
# Every dispute ruling costs USDC. Revenue model: $0.50 per ruling.
# Set X402_PAY_TO (your Base wallet) and X402_NETWORK (eip155:8453 for Base mainnet)
# to enable payments. Without these env vars, the middleware is skipped (free tier).

X402_PAY_TO = os.environ.get("X402_PAY_TO", "")
X402_NETWORK = os.environ.get("X402_NETWORK", "eip155:84532")  # Base Sepolia testnet default
X402_PRICE = os.environ.get("X402_PRICE", "$0.50")

if X402_PAY_TO:
    try:
        from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
        from x402.http.middleware.fastapi import PaymentMiddlewareASGI
        from x402.http.types import RouteConfig
        from x402.mechanisms.evm.exact import ExactEvmServerScheme
        from x402.server import x402ResourceServer

        facilitator = HTTPFacilitatorClient(
            FacilitatorConfig(url="https://x402.org/facilitator")
        )
        server = x402ResourceServer(facilitator)
        server.register(X402_NETWORK, ExactEvmServerScheme())

        routes = {
            "POST /dispute": RouteConfig(
                accepts=[
                    PaymentOption(
                        scheme="exact",
                        pay_to=X402_PAY_TO,
                        price=X402_PRICE,
                        network=X402_NETWORK,
                    ),
                ],
                mime_type="application/json",
                description="Submit a dispute and receive an AI-generated ruling",
            ),
        }
        app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)
        print(f"x402 payment middleware active: {X402_PRICE} per dispute → {X402_PAY_TO[:10]}...")
    except ImportError:
        print("x402 package not installed — payment middleware disabled")
    except Exception as e:
        print(f"x402 middleware setup failed: {e}")
else:
    print("X402_PAY_TO not set — dispute rulings are free")

# --- Data directory (persistent on Railway) ---
DATA_DIR = os.environ.get("AGENTCOURT_DATA_DIR", "/root/.letta/agentcourt/data")
os.makedirs(DATA_DIR, exist_ok=True)


# --- Schemas ---

class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    type: str  # contract, message, payment, file, log, screenshot, commit, other
    source: str  # who submitted this
    timestamp: str  # ISO 8601
    content_hash: Optional[str] = None  # SHA-256 of the evidence content
    content_uri: Optional[str] = None  # where the actual content lives
    claimed_fact: str  # what fact does this evidence support or refute
    excerpt: Optional[str] = None  # relevant snippet
    reliability: Optional[str] = None  # high / medium / low
    notes: Optional[str] = None


class ContractTerms(BaseModel):
    parties: List[str]  # agent IDs or names
    obligations: List[str]  # what was promised
    deadlines: Optional[List[str]] = None  # ISO 8601 timestamps
    deliverables: Optional[List[str]] = None  # what should be delivered
    payment_terms: Optional[str] = None
    definitions: Optional[dict] = None
    raw_contract: Optional[str] = None  # original contract text


class DisputeRequest(BaseModel):
    """POST /dispute — the single input endpoint"""
    case_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    claimant: str  # agent filing the dispute
    respondent: str  # agent being disputed against
    contract: ContractTerms  # the agreement in question
    claim: str  # what went wrong, in plain language
    desired_remedy: str  # what the claimant wants
    evidence: List[EvidenceItem]  # supporting evidence
    dispute_type: Optional[str] = None  # milestone, quality, delivery, scope, payment, other
    priority: Optional[str] = "normal"  # low, normal, high, critical


class RulingResponse(BaseModel):
    """The output — what AgentCourt returns"""
    case_id: str
    status: str  # ruled, needs_more_info, escalated
    confidence: str  # high, medium, low
    ruling: str  # the decision in plain language
    reasoning: str  # why this ruling was made
    remedy: str  # what should happen
    facts_established: List[dict]  # facts the judge found established
    facts_disputed: List[dict]  # facts still in dispute
    facts_unknown: List[dict]  # facts that couldn't be determined
    precedent_refs: Optional[List[str]] = None  # references to similar past cases
    alternative_ruling: Optional[str] = None  # "why not the alternative" section
    ruled_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    judge_model: Optional[str] = None  # which model produced this ruling
    version: str = "0.1.0"


# --- Judge Agent Prompt ---

JUDGE_SYSTEM_PROMPT = """You are a neutral, evidence-driven dispute judge for AgentCourt.

Your job: read the contract, evidence, and claim. Produce a fair ruling.

RULES:
1. The contract is king. Apply its terms as written.
2. Evidence beats assertion. Require proof, not vibes.
3. If evidence is ambiguous, say so. Never pretend certainty.
4. Apply the same rubric to every case:
   a. Was the obligation clearly defined?
   b. Was the obligation fulfilled?
   c. If not, was the failure material or minor?
   d. What remedy does the contract specify?
   e. If no remedy specified, what's fair and proportional?
5. You MUST explain your reasoning step by step.
6. You MUST state your confidence level: high, medium, or low.
7. You MUST provide the "alternative ruling" — why the other side might be right.
8. If confidence is low, recommend escalation or more evidence.
9. Never speculate beyond what the evidence supports.
10. Be consistent: similar cases should get similar rulings.

OUTPUT FORMAT (JSON):
{
  "confidence": "high|medium|low",
  "ruling": "one clear sentence: what is decided",
  "reasoning": "step by step: what facts you found, what rules you applied, why",
  "remedy": "what should happen: payment, partial refund, rework, apology, etc",
  "facts_established": [{"fact": "...", "evidence_ids": ["..."]}],
  "facts_disputed": [{"fact": "...", "evidence_for": ["..."], "evidence_against": ["..."]}],
  "facts_unknown": [{"fact": "...", "reason": "insufficient evidence"}],
  "alternative_ruling": "if the respondent is right, what would change and why"
}
"""

JUDGE_USER_PROMPT_TEMPLATE = """## DISPUTE CASE {case_id}

### PARTIES
- Claimant: {claimant}
- Respondent: {respondent}

### CONTRACT
Obligations: {obligations}
Deliverables: {deliverables}
Deadlines: {deadlines}
Payment terms: {payment_terms}

### CLAIM
{claim}

### DESIRED REMEDY
{desired_remedy}

### EVIDENCE
{evidence_formatted}

---

Produce your ruling in the required JSON format."""


# --- Case Storage (simple JSON files, persistent) ---

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


def list_cases() -> List[dict]:
    cases = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(DATA_DIR, fname)) as f:
                cases.append(json.load(f))
    return sorted(cases, key=lambda c: c.get("created_at", ""), reverse=True)


# --- Judge Execution ---

def format_evidence(evidence: List[EvidenceItem]) -> str:
    lines = []
    for i, e in enumerate(evidence, 1):
        lines.append(f"""Evidence #{i} [{e.type}]:
  ID: {e.id}
  Source: {e.source}
  Time: {e.timestamp}
  Claimed fact: {e.claimed_fact}
  Reliability: {e.reliability or "unrated"}
  Excerpt: {e.excerpt or "(see content_uri)"}
  Content hash: {e.content_hash or "none"}""")
    return "\n".join(lines)


async def execute_judge(dispute: DisputeRequest) -> RulingResponse:
    """Run the judge agent via the Letta Cloud API or direct LLM call."""
    import urllib.request

    # Format the evidence
    evidence_formatted = format_evidence(dispute.evidence)

    # Build the judge prompt
    user_prompt = JUDGE_USER_PROMPT_TEMPLATE.format(
        case_id=dispute.case_id,
        claimant=dispute.claimant,
        respondent=dispute.respondent,
        obligations=", ".join(dispute.contract.obligations),
        deliverables=", ".join(dispute.contract.deliverables or ["not specified"]),
        deadlines=", ".join(dispute.contract.deadlines or ["not specified"]),
        payment_terms=dispute.contract.payment_terms or "not specified",
        claim=dispute.claim,
        desired_remedy=dispute.desired_remedy,
        evidence_formatted=evidence_formatted,
    )

    # Call the LLM (using Letta Cloud API for now)
    letta_api_key = os.environ.get("LETTA_API_KEY", "")
    letta_base = os.environ.get("LETTA_BASE_URL", "https://api.letta.com")

    # We'll use a dedicated judge agent or call the LLM directly
    # For v1, we use the current agent's LLM via a simple completion
    # This will be replaced with a dedicated judge agent later

    # Use OpenRouter API (OpenAI-compatible) for the judge LLM
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_model = os.environ.get("JUDGE_MODEL", "anthropic/claude-sonnet-4")
    openrouter_base = "https://openrouter.ai/api/v1"

    if openrouter_key:
        # OpenRouter uses OpenAI-compatible chat completions
        payload = {
            "model": openrouter_model,
            "messages": [
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{openrouter_base}/chat/completions",
            data=data,
            method="POST",
        )
        req.add_header("Authorization", f"Bearer {openrouter_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("HTTP-Referer", "https://agentcourt.ai")
        req.add_header("X-Title", "AgentCourt Judge")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())
                content = result["choices"][0]["message"]["content"]
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        ruling_data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        ruling_data = {
                            "confidence": "medium",
                            "ruling": content[:300],
                            "reasoning": "LLM response was not valid JSON",
                            "remedy": "Review raw response",
                            "facts_established": [],
                            "facts_disputed": [],
                            "facts_unknown": [],
                            "alternative_ruling": "See raw response",
                        }
                else:
                    ruling_data = {
                        "confidence": "medium",
                        "ruling": content[:300] if content else "No ruling generated",
                        "reasoning": "Raw LLM response could not be parsed as JSON",
                        "remedy": "Review raw response",
                        "facts_established": [],
                        "facts_disputed": [],
                        "facts_unknown": [],
                        "alternative_ruling": "See raw response",
                    }
        except Exception as e:
            ruling_data = {
                "confidence": "low",
                "ruling": f"Judge API call failed: {str(e)[:200]}",
                "reasoning": "Error calling OpenRouter LLM backend",
                "remedy": "Fix API connection and resubmit",
                "facts_established": [],
                "facts_disputed": [],
                "facts_unknown": [{"fact": "all", "reason": "API error"}],
                "alternative_ruling": "N/A",
            }
    else:
        # Fallback: return a placeholder ruling
        ruling_data = {
            "confidence": "low",
            "ruling": "Judge agent not yet connected to LLM — configure OPENAI_API_KEY",
            "reasoning": "The ruling engine requires an LLM backend. Set OPENAI_API_KEY environment variable.",
            "remedy": "Configure LLM access and resubmit",
            "facts_established": [],
            "facts_disputed": [],
            "facts_unknown": [{"fact": "all", "reason": "LLM not configured"}],
            "alternative_ruling": "N/A — no LLM available",
        }

    return RulingResponse(
        case_id=dispute.case_id,
        status="ruled" if ruling_data.get("confidence") != "low" else "needs_more_info",
        confidence=ruling_data.get("confidence", "low"),
        ruling=ruling_data.get("ruling", ""),
        reasoning=ruling_data.get("reasoning", ""),
        remedy=ruling_data.get("remedy", ""),
        facts_established=ruling_data.get("facts_established", []),
        facts_disputed=ruling_data.get("facts_disputed", []),
        facts_unknown=ruling_data.get("facts_unknown", []),
        precedent_refs=ruling_data.get("precedent_refs"),
        alternative_ruling=ruling_data.get("alternative_ruling"),
        judge_model=openrouter_model if openrouter_key else "none",
    )


# --- API Endpoints ---

@app.post("/dispute", response_model=RulingResponse)
async def create_dispute(dispute: DisputeRequest):
    """The single core endpoint: submit a dispute, get a ruling."""
    # Save the case
    case_data = {
        "case_id": dispute.case_id,
        "claimant": dispute.claimant,
        "respondent": dispute.respondent,
        "claim": dispute.claim,
        "desired_remedy": dispute.desired_remedy,
        "dispute_type": dispute.dispute_type,
        "priority": dispute.priority,
        "evidence_count": len(dispute.evidence),
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending",
    }
    save_case(dispute.case_id, {"request": case_data})

    # Execute the judge
    ruling = await execute_judge(dispute)

    # Save the ruling
    case_data["status"] = ruling.status
    case_data["ruling"] = ruling.ruling
    case_data["confidence"] = ruling.confidence
    case_data["ruled_at"] = ruling.ruled_at
    save_case(dispute.case_id, {"request": case_data, "ruling": ruling.dict()})

    return ruling


@app.get("/cases")
async def list_all_cases():
    """List all cases."""
    return list_cases()


@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get a specific case."""
    case = load_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case



@app.get("/debug/env")
async def debug_env():
    import os
    return {
        "OPENROUTER_API_KEY_set": bool(os.environ.get("OPENROUTER_API_KEY")),
        "JUDGE_MODEL": os.environ.get("JUDGE_MODEL", "anthropic/claude-sonnet-4"),
        "AGENT_ID": os.environ.get("AGENT_ID", "not set"),
    }

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0", "data_dir": DATA_DIR}
