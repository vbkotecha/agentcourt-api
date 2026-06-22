"""
AgentCourt Policy Engine — Deterministic rule evaluation for dispute resolution.

Evaluates evidence against policy templates to produce structured rulings.
This is the core differentiator: policy-first, not free-form LLM judgment.
"""

import os
import json
import hashlib
import re
from datetime import datetime
from typing import Any, Optional
from pathlib import Path


# ─── Policy Loader ───────────────────────────────────────────────────────────

POLICY_DIR = Path(__file__).parent.parent / "policies"


def load_policy(policy_name: str) -> dict:
    """Load a policy template by name from the policies directory."""
    # Prefer JSON (no yaml dependency needed), fall back to YAML
    json_path = POLICY_DIR / f"{policy_name}.json"
    yaml_path = POLICY_DIR / f"{policy_name}.yaml"

    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    elif yaml_path.exists():
        # Try yaml import (available on Railway/deployment)
        try:
            import yaml
            with open(yaml_path) as f:
                return yaml.safe_load(f)
        except ImportError:
            raise FileNotFoundError(
                f"Policy '{policy_name}' only has YAML but pyyaml not installed. "
                f"Run: bun -e convert script, or pip install pyyaml"
            )
    else:
        raise FileNotFoundError(f"Policy '{policy_name}' not found at {json_path}")


def list_policies() -> list[dict]:
    """List all available policy templates."""
    policies = []
    seen = set()
    # Load JSON files
    for f in POLICY_DIR.glob("*.json"):
        with open(f) as fh:
            data = json.load(fh)
            name = data.get("name", f.stem)
            policies.append({
                "name": name,
                "version": data.get("version"),
                "description": data.get("description"),
                "rules_count": len(data.get("rules", [])),
            })
            seen.add(f.stem)
    # Also check YAML files not yet converted
    for f in POLICY_DIR.glob("*.yaml"):
        if f.stem not in seen:
            try:
                import yaml
                with open(f) as fh:
                    data = yaml.safe_load(fh)
                    policies.append({
                        "name": data.get("name"),
                        "version": data.get("version"),
                        "description": data.get("description"),
                        "rules_count": len(data.get("rules", [])),
                    })
            except ImportError:
                pass
    return policies


# ─── Evidence Scorer ─────────────────────────────────────────────────────────

def score_evidence(evidence: list[dict], policy: dict) -> list[dict]:
    """
    Score each evidence item based on policy weights.
    Returns evidence items with added 'score' field (0.0-1.0).
    """
    weights = policy.get("evidence_weights", {})
    scored = []

    for item in evidence:
        etype = item.get("type", "other")
        base_weight = weights.get(etype, 0.3)

        # Hash verification bonus
        hash_bonus = 0.1 if item.get("content_hash") else 0.0

        # Reliability multiplier
        reliability = item.get("reliability", "medium")
        rel_mult = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(reliability, 0.7)

        # Recency bonus (evidence from last 30 days)
        recency_bonus = 0.0
        if item.get("timestamp"):
            try:
                ts = datetime.fromisoformat(item["timestamp"].replace("Z", ""))
                days_old = (datetime.utcnow() - ts).days
                recency_bonus = max(0, 0.1 * (1 - days_old / 30))
            except (ValueError, TypeError):
                pass

        score = min(1.0, (base_weight * rel_mult) + hash_bonus + recency_bonus)
        item_scored = {**item, "score": round(score, 3)}
        scored.append(item_scored)

    return scored


# ─── Fact Extractor ──────────────────────────────────────────────────────────

def extract_facts(
    scored_evidence: list[dict],
    dispute: dict,
    policy: dict,
) -> dict:
    """
    Extract structured facts from evidence + dispute context.
    Returns a dict of fact_name → value (true/false/None/number/string).
    """
    facts = {}
    
    # Null-safe accessors
    contract = dispute.get("contract") or {}
    metadata = dispute.get("metadata") or {}

    # --- Delivery facts (freelance/milestone) ---
    delivery_evidence = [e for e in scored_evidence if e.get("type") in ("commit", "file", "screenshot", "log")]
    payment_evidence = [e for e in scored_evidence if e.get("type") in ("payment", "invoice", "receipt", "payment_proof")]
    acceptance_evidence = [e for e in scored_evidence if "accept" in e.get("claimed_fact", "").lower() or "approv" in e.get("claimed_fact", "").lower()]

    # Evidence of delivery requires BOTH: delivery-type evidence AND claimed_fact indicating delivery occurred
    delivery_keywords = ("deliver", "submitted", "committed", "uploaded", "completed", "shipped", "sent", "provided")
    actual_delivery_evidence = [
        e for e in delivery_evidence
        if any(kw in e.get("claimed_fact", "").lower() for kw in delivery_keywords)
    ]
    facts["evidence_of_delivery"] = len(actual_delivery_evidence) > 0
    facts["payment_received"] = any(p.get("score", 0) > 0.5 for p in payment_evidence)

    # Determine acceptance
    accepted_mentions = len(acceptance_evidence)
    rejected_mentions = sum(1 for e in scored_evidence if "reject" in e.get("claimed_fact", "").lower())
    if accepted_mentions > rejected_mentions:
        facts["deliverable_was_accepted"] = True
    elif rejected_mentions > accepted_mentions:
        facts["deliverable_was_accepted"] = False
    elif not actual_delivery_evidence:
        # No delivery evidence at all → can't have been accepted
        facts["deliverable_was_accepted"] = False
    else:
        facts["deliverable_was_accepted"] = None

    # Delivery timing
    deadlines = contract.get("deadlines") or []
    if deadlines and actual_delivery_evidence:
        try:
            deadline = datetime.fromisoformat(deadlines[0].replace("Z", ""))
            delivery_ts = None
            for e in actual_delivery_evidence:
                if e.get("timestamp"):
                    delivery_ts = datetime.fromisoformat(e["timestamp"].replace("Z", ""))
                    break
            if delivery_ts:
                facts["delivery_was_on_time"] = delivery_ts <= deadline
                facts["days_late"] = max(0, (delivery_ts - deadline).days)
            else:
                facts["delivery_was_on_time"] = None
                facts["days_late"] = 0
        except (ValueError, TypeError):
            facts["delivery_was_on_time"] = None
            facts["days_late"] = 0
    else:
        facts["delivery_was_on_time"] = None
        facts["days_late"] = 0

    # Quality issues
    quality_evidence = [e for e in scored_evidence if "quality" in e.get("claimed_fact", "").lower() or "defect" in e.get("claimed_fact", "").lower() or "bug" in e.get("claimed_fact", "").lower()]
    facts["quality_issues_documented"] = len(quality_evidence) > 0

    # --- Milestone facts ---
    progress_evidence = [e for e in scored_evidence if "progress" in e.get("claimed_fact", "").lower() or "%" in e.get("claimed_fact", "")]
    facts["milestone_completed"] = facts.get("deliverable_was_accepted")
    facts["milestone_progress_pct"] = metadata.get("progress_pct", 0)

    # --- Bug bounty facts ---
    repro_evidence = [e for e in scored_evidence if "reproduc" in e.get("claimed_fact", "").lower()]
    non_repro_evidence = [e for e in scored_evidence if "non-reproduc" in e.get("claimed_fact", "").lower() or "cannot reproduce" in e.get("claimed_fact", "").lower()]
    if repro_evidence and not non_repro_evidence:
        facts["bug_is_reproducible"] = True
    elif non_repro_evidence and not repro_evidence:
        facts["bug_is_reproducible"] = False
    else:
        facts["bug_is_reproducible"] = None

    facts["reproduction_attempts"] = metadata.get("reproduction_attempts", 0)
    facts["severity_meets_threshold"] = metadata.get("severity_meets_threshold")
    facts["actual_severity"] = metadata.get("actual_severity")
    facts["disclosure_compliant"] = metadata.get("disclosure_compliant")

    # ─── MERGE METADATA FACTS (highest priority) ────────────────────────────
    # Metadata-provided facts override extracted facts — they're explicit declarations
    # from the submitter (e.g., milestone_completed, days_since_completion, payment_terms_days)
    for key, val in metadata.items():
        if val is not None:
            facts[key] = val

    return facts


# ─── Rule Evaluator ──────────────────────────────────────────────────────────

def _resolve_value(expr: str, facts: dict) -> Any:
    """Resolve a value expression — either a fact reference or literal."""
    expr = expr.strip()
    if expr in facts:
        return facts[expr]
    # Try parsing as literal
    if expr.lower() == "true":
        return True
    if expr.lower() == "false":
        return False
    if expr.lower() == "null" or expr.lower() == "none":
        return None
    try:
        return int(expr)
    except ValueError:
        try:
            return float(expr)
        except ValueError:
            return expr.strip("'\"")


def _evaluate_condition(condition: str, facts: dict) -> bool:
    """
    Evaluate a policy rule condition against extracted facts.
    Supports: ==, !=, >, <, >=, <=, AND, OR, null checks.
    Handles multiline conditions (newlines from YAML formatting).
    """
    if not condition or not condition.strip():
        return False

    # Normalize: replace newlines with spaces, collapse whitespace
    condition = ' '.join(condition.split())

    # Split on AND / OR (simple approach — evaluate AND clauses first)
    if " OR " in condition:
        return any(_evaluate_condition(c.strip(), facts) for c in condition.split(" OR "))
    if " AND " in condition:
        return all(_evaluate_condition(c.strip(), facts) for c in condition.split(" AND "))

    # Parse comparison operators
    for op in ["==", "!=", ">=", "<=", ">", "<"]:
        if op in condition:
            left, right = condition.split(op, 1)
            left_val = _resolve_value(left.strip(), facts)
            right_val = _resolve_value(right.strip(), facts)

            if left_val is None or right_val is None:
                if op == "==" and left_val == right_val:
                    return True
                if op == "!=" and left_val != right_val:
                    return True
                return False

            try:
                if op == "==":
                    return left_val == right_val
                if op == "!=":
                    return left_val != right_val
                if op == ">=":
                    return float(left_val) >= float(right_val)
                if op == "<=":
                    return float(left_val) <= float(right_val)
                if op == ">":
                    return float(left_val) > float(right_val)
                if op == "<":
                    return float(left_val) < float(right_val)
            except (ValueError, TypeError):
                return False

    # Bare fact reference — truthy check
    val = _resolve_value(condition, facts)
    return bool(val)


def evaluate_rules(policy: dict, facts: dict) -> Optional[dict]:
    """
    Evaluate policy rules in order. Return the first matching rule.
    Each rule has: id, condition, ruling_template, confidence, remedy.
    """
    for rule in policy.get("rules", []):
        condition = rule.get("condition", "")
        if _evaluate_condition(condition, facts):
            return rule

    # No rule matched — return default
    return {
        "id": "default-no-match",
        "ruling_template": "No policy rule matched the presented evidence. Case requires escalation.",
        "confidence": "low",
        "remedy": "escalate",
        "facts_required": [],
    }


# ─── Confidence Calculator ───────────────────────────────────────────────────

def calculate_confidence(
    matched_rule: dict,
    scored_evidence: list[dict],
    facts: dict,
    policy: dict,
) -> str:
    """
    Determine confidence band based on rule match + evidence quality.
    """
    base_confidence = matched_rule.get("confidence", "low")

    # Check if required facts are actually known (not None)
    # A fact that is False is still "known" — only None means unknown
    required = matched_rule.get("facts_required", [])
    unknown_count = sum(1 for f in required if facts.get(f) is None)

    if unknown_count > len(required) / 2:
        # More than half the required facts are unknown → low confidence
        return "low"
    elif unknown_count > 0:
        # Some required facts unknown → downgrade by one level
        if base_confidence == "high":
            return "medium"

    # Average evidence score
    scores = [e.get("score", 0) for e in scored_evidence]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Adjust confidence based on evidence quality
    if base_confidence == "high" and avg_score < 0.5:
        return "medium"

    return base_confidence


# ─── Ruling Generator ────────────────────────────────────────────────────────

def generate_ruling(
    dispute: dict,
    scored_evidence: list[dict],
    facts: dict,
    matched_rule: dict,
    policy: dict,
) -> dict:
    """Generate the full structured ruling."""
    # Null-safe metadata for template variable lookup
    local_metadata = dispute.get("metadata") or {}
    # Format the ruling template with fact values
    template = matched_rule.get("ruling_template", "Ruling could not be generated.")
    # Replace {var} placeholders — fill with fact value or "N/A"
    def _replace_var(m):
        var = m.group(1)
        val = facts.get(var, local_metadata.get(var))
        if val is not None:
            return str(val)
        return "N/A"
    import re as _re
    ruling_text = _re.sub(r'\{(\w+)\}', _replace_var, template)

    # Build fact tables
    facts_established = [
        {"fact": k, "value": str(v)}
        for k, v in facts.items()
        if v is not None and v is not False
    ]
    facts_disputed = [
        {"fact": k, "value": "contested"}
        for k, v in facts.items()
        if v is False
    ]
    facts_unknown = [
        {"fact": k, "reason": "insufficient evidence"}
        for k, v in facts.items()
        if v is None
    ]

    # Get confidence
    confidence = calculate_confidence(matched_rule, scored_evidence, facts, policy)

    # Determine status
    if confidence == "low" or matched_rule.get("remedy") == "escalate":
        status = "needs_more_info"
    else:
        status = "ruled"

    return {
        "ruling": ruling_text,
        "reasoning": f"Matched policy rule '{matched_rule.get('id')}' from template '{policy.get('name')}'. "
                     f"Evidence evaluated with {len(scored_evidence)} items. "
                     f"Average evidence score: {sum(e.get('score', 0) for e in scored_evidence) / max(1, len(scored_evidence)):.2f}",
        "remedy": matched_rule.get("remedy", "none"),
        "confidence": confidence,
        "status": status,
        "facts_established": facts_established,
        "facts_disputed": facts_disputed,
        "facts_unknown": facts_unknown,
        "matched_rule_id": matched_rule.get("id"),
        "policy_name": policy.get("name"),
        "policy_version": policy.get("version"),
        "evidence_scores": [
            {"id": e.get("id", "?"), "type": e.get("type", "?"), "score": e.get("score", 0)}
            for e in scored_evidence
        ],
    }


# ─── Main Engine Entry Point ─────────────────────────────────────────────────

def evaluate_dispute(
    dispute: dict,
    evidence: list[dict],
    policy_name: str = "freelance-delivery",
) -> dict:
    """
    Full dispute evaluation pipeline.
    
    Args:
        dispute: Dict with claimant, respondent, contract, claim, metadata
        evidence: List of evidence item dicts
        policy_name: Which policy template to use
    
    Returns:
        Full structured ruling dict
    """
    # 1. Load policy
    policy = load_policy(policy_name)

    # 2. Score evidence
    scored_evidence = score_evidence(evidence, policy)

    # 3. Extract facts
    facts = extract_facts(scored_evidence, dispute, policy)

    # 4. Evaluate rules
    matched_rule = evaluate_rules(policy, facts)

    # 5. Generate ruling
    ruling = generate_ruling(dispute, scored_evidence, facts, matched_rule, policy)

    # 6. Add metadata
    ruling["case_id"] = dispute.get("case_id", "unknown")
    ruling["ruled_at"] = datetime.utcnow().isoformat()
    ruling["engine_version"] = "1.0.0"

    return ruling
