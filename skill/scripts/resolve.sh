#!/usr/bin/env bash
# AgentCourt CLI helper — resolve a dispute from a JSON file
# Usage: ./resolve.sh <dispute.json>

set -euo pipefail

API_URL="${AGENTCOURT_API_URL:-https://api.agentcourt.to}"

if [ $# -eq 0 ]; then
  echo "Usage: resolve.sh <dispute.json>"
  echo "Example: resolve.sh examples/freelance_dispute.json"
  exit 1
fi

DISPUTE_FILE="$1"

if [ ! -f "$DISPUTE_FILE" ]; then
  echo "Error: File not found: $DISPUTE_FILE"
  exit 1
fi

echo "Submitting dispute to AgentCourt..."
RESPONSE=$(curl -s -X POST "${API_URL}/v1/disputes" \
  -H "Content-Type: application/json" \
  -d @"$DISPUTE_FILE")

CASE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('case_id','unknown'))")
STATUS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
RULING=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ruling','no ruling')[:200])")

echo ""
echo "Case ID: $CASE_ID"
echo "Status:  $STATUS"
echo "Ruling:  $RULING"
echo ""
echo "Full response saved to last_ruling.json"
echo "$RESPONSE" | python3 -m json.tool > last_ruling.json
