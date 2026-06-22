#!/usr/bin/env bash
#
# AgentCourt Live Demo Script
# Run this when the API is live to demonstrate all 4 policy templates
# Usage: bash scripts/demo.sh
#
# Requires: curl, jq, python3

set -e

API="https://agentcourt-api-production.up.railway.app"

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          AgentCourt Live Demo                            ║${NC}"
echo -e "${CYAN}║          Dispute Resolution for Agent Commerce           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Health Check ────────────────────────────────────────────────────────────
echo -e "${YELLOW}━━━ 1. Health Check ━━━${NC}"
HEALTH=$(curl -s "$API/health")
echo "  $HEALTH"
echo ""

# ─── List Policies ───────────────────────────────────────────────────────────
echo -e "${YELLOW}━━━ 2. Available Policy Templates ━━━${NC}"
curl -s "$API/v1/policies" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
for p in d.get('policies', []):
    name = p.get('name', '?')
    desc = p.get('description', '')[:60]
    rules = len(p.get('rules', []))
    print(f'  • {name} ({rules} rules): {desc}')
"
echo ""

# ─── Demo 1: Freelance Delivery ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "${YELLOW}━━━ 3. Demo: Freelance Delivery — Non-Delivery ━━━${NC}"
echo -e "  Scenario: Developer was paid but never delivered the app"
echo ""

RESULT=$(curl -s -X POST "$API/v1/disputes" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "freelance-delivery",
    "claimant": "TechCorp",
    "respondent": "DevStudio",
    "claim": "Developer was paid $5,000 but never delivered the mobile app",
    "desired_remedy": "full_refund",
    "contract": {
      "parties": ["TechCorp", "DevStudio"],
      "obligations": ["Build iOS and Android mobile app"],
      "deadlines": ["2026-06-15T23:59:00Z"],
      "deliverables": ["iOS app", "Android app", "Source code"],
      "payment_terms": "$5,000 paid upfront"
    },
    "evidence": [
      {
        "type": "contract",
        "source": "signed_agreement.pdf",
        "timestamp": "2026-05-01T10:00:00Z",
        "claimed_fact": "Developer agreed to deliver iOS and Android app by June 15",
        "reliability": "high"
      },
      {
        "type": "payment_proof",
        "source": "bank_transfer.pdf",
        "timestamp": "2026-05-01T10:05:00Z",
        "claimed_fact": "$5,000 wire transfer completed",
        "reliability": "high"
      },
      {
        "type": "log",
        "source": "github.com/devstudio/app",
        "timestamp": "2026-06-20T12:00:00Z",
        "claimed_fact": "Repository empty, no commits after initial setup",
        "reliability": "medium"
      }
    ]
  }')

echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
ruling = d.get('ruling', d)
print(f'  Matched Rule:  {ruling.get(\"matched_rule_id\", \"?\")}')
print(f'  Remedy:        {ruling.get(\"remedy\", \"?\")}')
print(f'  Confidence:    {ruling.get(\"confidence\", \"?\")}')
print(f'  Status:        {ruling.get(\"status\", \"?\")}')
print(f'  Ruling:')
for line in ruling.get('ruling', 'N/A').split('. '):
    if line.strip():
        print(f'    {line.strip()}.')
" 2>/dev/null || echo "  (API not responding correctly)"
echo ""

# ─── Demo 2: SLA Monitoring ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "${YELLOW}━━━ 4. Demo: SLA Monitoring — Uptime Violation ━━━${NC}"
echo -e "  Scenario: API provider breached 99.9% uptime SLA"
echo ""

RESULT=$(curl -s -X POST "$API/v1/disputes" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "sla-monitoring",
    "claimant": "DataFlow Inc",
    "respondent": "CloudAPI Co",
    "claim": "API uptime was 98.5% in May, breaching the 99.9% SLA",
    "desired_remedy": "service_credit",
    "contract": {
      "parties": ["DataFlow Inc", "CloudAPI Co"],
      "obligations": ["Maintain 99.9% monthly uptime"],
      "sla_terms": {
        "metric": "uptime",
        "threshold": 99.9,
        "period": "monthly",
        "penalty": "10% service credit"
      }
    },
    "evidence": [
      {
        "type": "log",
        "source": "uptime_monitor.json",
        "timestamp": "2026-06-01T00:00:00Z",
        "claimed_fact": "Measured uptime: 98.5% for May 2026",
        "reliability": "high"
      },
      {
        "type": "contract",
        "source": "sla_agreement.pdf",
        "timestamp": "2026-01-01T00:00:00Z",
        "claimed_fact": "SLA requires 99.9% monthly uptime, 10% credit for breach",
        "reliability": "high"
      }
    ]
  }')

echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
ruling = d.get('ruling', d)
print(f'  Matched Rule:  {ruling.get(\"matched_rule_id\", \"?\")}')
print(f'  Remedy:        {ruling.get(\"remedy\", \"?\")}')
print(f'  Confidence:    {ruling.get(\"confidence\", \"?\")}')
print(f'  Status:        {ruling.get(\"status\", \"?\")}')
" 2>/dev/null || echo "  (API not responding correctly)"
echo ""

# ─── Demo 3: Bug Bounty ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "${YELLOW}━━━ 5. Demo: Bug Bounty — Valid Bug ━━━${NC}"
echo -e "  Scenario: Researcher found a critical auth bypass, claims bounty"
echo ""

RESULT=$(curl -s -X POST "$API/v1/disputes" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "bug-bounty",
    "claimant": "SecurityResearcher",
    "respondent": "DeFiProtocol",
    "claim": "Found and reported a critical authentication bypass vulnerability",
    "desired_remedy": "full_payout",
    "contract": {
      "parties": ["SecurityResearcher", "DeFiProtocol"],
      "bounty_terms": {
        "critical": 10000,
        "high": 5000,
        "medium": 1000,
        "low": 250,
        "disclosure_required": true,
        "reproduction_required": true
      }
    },
    "evidence": [
      {
        "type": "commit",
        "source": "github.com/defi/protocol/commit/abc123",
        "timestamp": "2026-06-10T14:00:00Z",
        "claimed_fact": "Commit fixes authentication bypass in login function",
        "reliability": "high"
      },
      {
        "type": "screenshot",
        "source": "poc_video.mp4",
        "timestamp": "2026-06-10T12:00:00Z",
        "claimed_fact": "Proof of concept showing unauthorized access with admin privileges",
        "reliability": "medium"
      },
      {
        "type": "log",
        "source": "bug_tracker.json",
        "timestamp": "2026-06-10T12:30:00Z",
        "claimed_fact": "Bug report submitted before fix was deployed, severity marked critical",
        "reliability": "high"
      }
    ]
  }')

echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
ruling = d.get('ruling', d)
print(f'  Matched Rule:  {ruling.get(\"matched_rule_id\", \"?\")}')
print(f'  Remedy:        {ruling.get(\"remedy\", \"?\")}')
print(f'  Confidence:    {ruling.get(\"confidence\", \"?\")}')
print(f'  Status:        {ruling.get(\"status\", \"?\")}')
" 2>/dev/null || echo "  (API not responding correctly)"
echo ""

# ─── Demo 4: Milestone Payment ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "${YELLOW}━━━ 6. Demo: Milestone Payment — Completed But Unpaid ━━━${NC}"
echo -e "  Scenario: Freelancer completed milestone, client won't pay"
echo ""

RESULT=$(curl -s -X POST "$API/v1/disputes" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "milestone-payment",
    "claimant": "Freelancer",
    "respondent": "StartupCo",
    "claim": "Milestone 2 (API integration) was completed and accepted but payment of $3,000 was never made",
    "desired_remedy": "full_payment",
    "contract": {
      "parties": ["Freelancer", "StartupCo"],
      "milestones": [
        {"id": "m1", "description": "Database schema", "amount": 2000, "status": "completed_paid"},
        {"id": "m2", "description": "API integration", "amount": 3000, "status": "completed_unpaid"},
        {"id": "m3", "description": "Frontend", "amount": 3000, "status": "not_started"}
      ]
    },
    "evidence": [
      {
        "type": "contract",
        "source": "milestone_agreement.pdf",
        "timestamp": "2026-04-01T00:00:00Z",
        "claimed_fact": "Three milestones totaling $8,000, payment due within 7 days of acceptance",
        "reliability": "high"
      },
      {
        "type": "message",
        "source": "email_thread.eml",
        "timestamp": "2026-05-20T15:00:00Z",
        "claimed_fact": "Client confirmed milestone 2 is complete and accepted",
        "reliability": "high"
      },
      {
        "type": "payment_proof",
        "source": "bank_statement.pdf",
        "timestamp": "2026-06-15T00:00:00Z",
        "claimed_fact": "No payment received for milestone 2, 26 days past due",
        "reliability": "high"
      }
    ]
  }')

echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
ruling = d.get('ruling', d)
print(f'  Matched Rule:  {ruling.get(\"matched_rule_id\", \"?\")}')
print(f'  Remedy:        {ruling.get(\"remedy\", \"?\")}')
print(f'  Confidence:    {ruling.get(\"confidence\", \"?\")}')
print(f'  Status:        {ruling.get(\"status\", \"?\")}')
" 2>/dev/null || echo "  (API not responding correctly)"
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Demo Complete. 4 templates × real scenarios = 4 rulings  ║${NC}"
echo -e "${CYAN}║  All deterministic. All <500ms. All API-first.           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Docs:  ${GREEN}$API/docs${NC}"
echo -e "  Swagger: ${GREEN}$API/swagger${NC}"
echo -e "  GitHub: ${GREEN}github.com/vbkotecha/agentcourt-api${NC}"
echo ""
