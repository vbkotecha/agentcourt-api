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
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import json
import sys

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
    version="1.0.0",
    description="Policy-driven dispute resolution protocol for agent commerce",
)

# Enable CORS for landing page demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

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
    engine_version: str = "1.0.0"


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
        "version": "1.0.0",
        "endpoints": {
            "submit_dispute": "POST /v1/disputes",
            "list_policies": "GET /v1/policies",
            "get_case": "GET /v1/cases/{case_id}",
            "health": "GET /health",
            "docs": "GET /docs",
        },
        "live": True,
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "data_dir": DATA_DIR,
        "engine": "policy-engine-v1",
        "policies": [p["name"] for p in list_policies()],
    }


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


from fastapi.responses import HTMLResponse

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
