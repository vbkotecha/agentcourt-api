"""
AgentCourt LCP MCP Server.

Exposes LCP checking and dispute filing as MCP tools that any MCP-compatible
agent can use. This makes AgentCourt the reference LCP dispute resolution
implementation for the MCP ecosystem.

Tools exposed:
1. check_lcp_domain — Check if a domain implements LCP
2. verify_lcp_terms — Verify a domain's terms hash
3. file_lcp_dispute — File an LCP-compliant dispute
4. list_dispute_policies — List available AgentCourt policies
5. get_agentcourt_lcp — Get AgentCourt's own LCP discovery document
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sdk-python"))

from lcp_adapter import LCPAdapter
from lcp_client import AgentCourtLCP, Evidence


AGENTCOURT_API = os.environ.get("AGENTCOURT_API", "https://api.agentcourt.to")


TOOLS = [
    {
        "name": "check_lcp_domain",
        "description": "Check if a domain implements the Legal Context Protocol (LCP). "
                       "Fetches /.well-known/legal-context.json and returns terms URL, "
                       "hash, dispute resolution info, and jurisdiction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "The domain to check (e.g., 'api.example.com')",
                },
            },
            "required": ["domain"],
        },
    },
    {
        "name": "verify_lcp_terms",
        "description": "Verify a domain's LCP terms hash. Fetches the terms document "
                       "and checks it against the published atrHash.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "The domain to verify",
                },
            },
            "required": ["domain"],
        },
    },
    {
        "name": "file_lcp_dispute",
        "description": "File an LCP-compliant dispute through AgentCourt. "
                       "Automatically fetches LCP context, maps to appropriate policy, "
                       "and returns a deterministic ruling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_domain": {
                    "type": "string",
                    "description": "Domain of the disputed service",
                },
                "claimant": {
                    "type": "string",
                    "description": "Party filing the dispute",
                },
                "respondent": {
                    "type": "string",
                    "description": "Party being disputed",
                },
                "claim": {
                    "type": "string",
                    "description": "Description of the dispute",
                },
                "desired_remedy": {
                    "type": "string",
                    "description": "What the claimant wants",
                },
                "evidence": {
                    "type": "array",
                    "description": "Evidence items",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "source": {"type": "string"},
                            "timestamp": {"type": "string"},
                            "claimed_fact": {"type": "string"},
                            "content_hash": {"type": "string"},
                            "reliability": {"type": "string"},
                        },
                    },
                },
                "policy_override": {
                    "type": "string",
                    "description": "Override automatic policy selection",
                },
            },
            "required": ["service_domain", "claimant", "respondent", "claim", "desired_remedy", "evidence"],
        },
    },
    {
        "name": "list_dispute_policies",
        "description": "List all available AgentCourt dispute resolution policies.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_agentcourt_lcp",
        "description": "Get AgentCourt's own LCP discovery document, showing how "
                       "AgentCourt implements the Legal Context Protocol.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_tool_call(name: str, arguments: dict) -> str:
    """Handle a tool call and return the result as a string."""
    client = AgentCourtLCP(api_url=AGENTCOURT_API)

    if name == "check_lcp_domain":
        domain = arguments.get("domain", "")
        info = client.check_domain(domain)
        return json.dumps(info.__dict__, indent=2, default=str)

    elif name == "verify_lcp_terms":
        domain = arguments.get("domain", "")
        result = client.verify_terms(domain)
        return json.dumps(result, indent=2, default=str)

    elif name == "file_lcp_dispute":
        evidence_items = [
            Evidence(**e) for e in arguments.get("evidence", [])
        ]
        ruling = client.dispute(
            service_domain=arguments["service_domain"],
            claimant=arguments["claimant"],
            respondent=arguments["respondent"],
            claim=arguments["claim"],
            desired_remedy=arguments["desired_remedy"],
            evidence=evidence_items,
            policy_override=arguments.get("policy_override"),
        )
        return json.dumps(ruling.__dict__, indent=2, default=str)

    elif name == "list_dispute_policies":
        result = client.list_policies()
        return json.dumps(result, indent=2, default=str)

    elif name == "get_agentcourt_lcp":
        adapter = LCPAdapter()
        result = adapter.get_discovery_document()
        return json.dumps(result, indent=2, default=str)

    return json.dumps({"error": f"Unknown tool: {name}"})


# ─── MCP Protocol Handler (stdio) ────────────────────────────────────────────

def handle_mcp_message(msg: dict) -> dict:
    """Handle a single MCP protocol message."""
    method = msg.get("method", "")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "agentcourt-lcp",
                    "version": "1.0.0",
                },
            },
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS},
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        result = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": result}],
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


if __name__ == "__main__":
    """Run as stdio MCP server."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            response = handle_mcp_message(msg)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
