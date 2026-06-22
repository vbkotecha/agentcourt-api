"""
AgentCash + AgentCourt Integration Demo
========================================
Shows the complete flow of an agent paying for an API via x402,
getting a bad response, and resolving the dispute via AgentCourt.

Requirements:
    - Python 3.10+
    - No external dependencies (stdlib only)

Run:
    python3 agentcash_integration_demo.py
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk'))
from agentcourt_python_sdk import AgentCourt

# ─── Setup ──────────────────────────────────────────────────────────────────

COURT = AgentCourt()
API_URL = "https://agentcourt-api-production.up.railway.app"


def simulate_api_call():
    """
    Simulate an agent calling a paid weather API via x402.

    In real life:
    1. Agent sends GET /weather to weather-api.example.com
    2. API returns HTTP 402 with payment requirements ($0.028 USDC)
    3. Agent's wallet signs the payment
    4. Agent retries with X-Payment header
    5. API returns the data

    For this demo, we simulate step 5 returning BAD data.
    """
    print("═══════════════════════════════════════════════════════════════")
    print("  AgentCash + AgentCourt Integration Demo")
    print("═══════════════════════════════════════════════════════════════\n")

    # Step 1: Agent pays for API call
    print("STEP 1: Agent pays 0.028 USDC for weather data (x402)")
    print("  → wallet.send(usdc=0.028, chain=base, to=weather_api)")
    print("  → payment confirmed on-chain\n")

    # Step 2: API returns response
    print("STEP 2: API responds with weather data")
    api_response = {"temperature": "72.5", "unit": "fahrenheit", "city": "SF"}
    print(f"  Response: {json.dumps(api_response)}")

    # The OpenAPI schema for this API says temperature is an integer
    openapi_schema = {
        "temperature": {"type": "integer"},
        "unit": {"type": "string"},
        "city": {"type": "string"},
    }
    print(f"  Schema says: temperature = {openapi_schema['temperature']['type']}")
    print(f"  Got: temperature = {type(api_response['temperature']).__name__} = '{api_response['temperature']}'")
    print("  ⚠️  SCHEMA MISMATCH!\n")

    # Step 3: Agent disputes via AgentCourt
    print("STEP 3: Agent submits dispute to AgentCourt")
    print("  → POST /v1/disputes (policy: api-quality)\n")

    ruling = COURT.resolve(
        policy="api-quality",
        claim="API returned wrong data type for 'temperature' field",
        claimant="buyer_agent",
        respondent="weather_api_provider",
        desired_remedy="full_refund",
        contract={
            "parties": ["buyer_agent", "weather_api_provider"],
            "obligations": ["Return weather data matching OpenAPI schema"],
            "deadlines": ["2026-06-22"],
        },
        metadata={
            "response_received": True,
            "schema_matches": False,
            "mismatched_field": "temperature",
            "expected_type": "integer",
            "actual_type": "string",
        },
        evidence=[
            {
                "type": "contract",
                "source": "openapi.json",
                "timestamp": "2026-06-01",
                "claimed_fact": "Schema declares temperature as integer",
            },
            {
                "type": "log",
                "source": "api_response.json",
                "timestamp": "2026-06-22",
                "claimed_fact": "API returned temperature as string '72.5'",
            },
        ],
    )

    # Step 4: Ruling
    print("═══════════════════════════════════════════════════════════════")
    print("  AGENTCOURT RULING")
    print("═══════════════════════════════════════════════════════════════")
    print(f"  Case ID:       {ruling.case_id}")
    print(f"  Status:        {ruling.status}")
    print(f"  Matched Rule:  {ruling.matched_rule}")
    print(f"  Remedy:        {ruling.remedy}")
    print(f"  Confidence:    {ruling.confidence}")
    print(f"  Policy:        {ruling.policy_name}")
    print()

    if ruling.facts_established:
        print("  Facts Established:")
        for f in ruling.facts_established:
            print(f"    ✓ {f.get('fact','?')}: {f.get('value','?')}")
        print()

    if ruling.evidence_scores:
        print("  Evidence Scores:")
        for e in ruling.evidence_scores:
            print(f"    {e.get('type','?'):12s} → {e.get('score','?'):.1f} pts")
        print()

    print(f"  Reasoning: {ruling.reasoning[:200]}")
    print()

    # Step 5: Outcome
    print("═══════════════════════════════════════════════════════════════")
    print("  OUTCOME")
    print("═══════════════════════════════════════════════════════════════")
    print(f"  Agent receives: {ruling.remedy} (0.028 USDC returned)")
    print(f"  Total dispute cost: $0.05 USDC (AgentCourt fee)")
    print(f"  Resolution time: <500ms")
    print(f"  Human involvement: 0")
    print()

    # Step 6: Show the full API integration pattern
    print("═══════════════════════════════════════════════════════════════")
    print("  PRODUCTION INTEGRATION PATTERN")
    print("═══════════════════════════════════════════════════════════════")
    print("""
    async function callPaidAPI(url, schema) {
        // 1. Pay via x402
        const response = await x402Fetch(url);

        // 2. Validate response against schema
        if (!validateSchema(response, schema)) {
            // 3. Dispute via AgentCourt
            const ruling = await court.resolve({
                policy: 'api-quality',
                claim: 'Schema mismatch',
                claimant: agentId,
                respondent: apiUrl,
                metadata: {
                    schema_matches: false,
                    mismatched_field: identifyMismatch(response, schema),
                },
                evidence: [
                    { type: 'contract', source: 'openapi.json',
                      claimed_fact: 'Expected schema' },
                    { type: 'log', source: 'response.json',
                      claimed_fact: 'Actual response' },
                ],
            });

            // 4. If ruling favors agent, process refund
            if (ruling.remedy === 'full_refund') {
                await processRefund(response.paymentId, ruling.caseId);
            }
            return null;
        }
        return response.data;
    }
    """)
    print("  → Every paid API call is automatically protected.")
    print("  → Bad responses trigger disputes instantly.")
    print("  → No human intervention needed.")
    print()


if __name__ == "__main__":
    simulate_api_call()
