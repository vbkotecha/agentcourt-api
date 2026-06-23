"""
AgentCourt MCP Server
Exposes AgentCourt dispute resolution as MCP tools for Claude, Cursor, and any MCP client.

Install: pip install mcp httpx
Run: python server.py
"""

import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

AGENTCOURT_BASE = "https://agentcourt-api-production.up.railway.app"

app = Server("agentcourt")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="file_dispute",
            description="File a dispute with AgentCourt's policy-driven resolution engine. Returns a deterministic ruling in under 500ms.",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy": {
                        "type": "string",
                        "enum": ["api-quality", "freelance-delivery", "milestone-payment",
                                 "bug-bounty", "sla-monitoring", "scope-dispute", "physical-commerce"],
                        "description": "The dispute policy to apply"
                    },
                    "claim": {"type": "string", "description": "Description of what went wrong"},
                    "claimant": {"type": "string", "description": "Party filing the dispute"},
                    "respondent": {"type": "string", "description": "Party being disputed"},
                    "desired_remedy": {
                        "type": "string",
                        "enum": ["full_refund", "partial_refund", "no_payout"],
                        "description": "What the claimant wants"
                    },
                    "contract_obligations": {"type": "string", "description": "What was agreed"},
                    "delivered": {"type": "boolean", "description": "Was the deliverable received?"},
                    "meets_spec": {"type": "boolean", "description": "Did it meet specifications?"},
                    "evidence_description": {"type": "string", "description": "Factual description of evidence"}
                },
                "required": ["policy", "claim", "desired_remedy", "delivered", "meets_spec"]
            }
        ),
        Tool(
            name="list_policies",
            description="List all available AgentCourt dispute resolution policy templates.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_policy_details",
            description="Get details and rules for a specific policy template.",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy_name": {"type": "string", "description": "Policy name (e.g. api-quality)"}
                },
                "required": ["policy_name"]
            }
        ),
        Tool(
            name="get_case",
            description="Get details of a previously filed case by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "The case ID to retrieve"}
                },
                "required": ["case_id"]
            }
        ),
        Tool(
            name="list_verdicts",
            description="List recent verdicts from AgentCourt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of verdicts to return (default: 10)"}
                }
            }
        ),
        Tool(
            name="health_check",
            description="Check if AgentCourt API is online and healthy.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "file_dispute":
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AGENTCOURT_BASE}/v1/disputes", json={
                "policy": arguments["policy"],
                "claim": arguments["claim"],
                "claimant": arguments.get("claimant", "mcp-agent"),
                "respondent": arguments.get("respondent", "counterparty"),
                "desired_remedy": arguments["desired_remedy"],
                "contract": {
                    "parties": [arguments.get("claimant", "mcp-agent"), arguments.get("respondent", "counterparty")],
                    "obligations": [arguments.get("contract_obligations", arguments["claim"])]
                },
                "metadata": {
                    "delivered": arguments["delivered"],
                    "meets_spec": arguments["meets_spec"],
                    "response_received": arguments["delivered"]
                },
                "evidence": [{
                    "type": "observation",
                    "source": "mcp-client",
                    "claimed_fact": arguments.get("evidence_description", arguments["claim"])
                }]
            }, timeout=10.0)
            result = response.json()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "list_policies":
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTCOURT_BASE}/v1/policies", timeout=10.0)
            return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

    elif name == "get_policy_details":
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTCOURT_BASE}/v1/policies/{arguments['policy_name']}", timeout=10.0)
            return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

    elif name == "get_case":
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTCOURT_BASE}/v1/cases/{arguments['case_id']}", timeout=10.0)
            return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

    elif name == "list_verdicts":
        limit = arguments.get("limit", 10)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTCOURT_BASE}/v1/cases?limit={limit}", timeout=10.0)
            return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

    elif name == "health_check":
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTCOURT_BASE}/health", timeout=10.0)
            return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
