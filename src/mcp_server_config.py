"""
AgentCourt MCP Server Configuration

This makes AgentCourt discoverable as an MCP tool for Claude, Cursor,
Claude Code, and any agent that uses the Model Context Protocol.

Agents can then call agentcourt_resolve_dispute() directly without
needing to know the REST API.

To deploy:
1. Add this to the agent's MCP config:
   {
     "agentcourt": {
       "url": "https://agentcourt-api-production.up.railway.app/mcp",
       "transport": "http"
     }
   }

2. Agent discovers the tool and can call it:
   agentcourt_resolve_dispute(
     policy="freelance-delivery",
     claim="Work never delivered",
     claimant="my_agent",
     respondent="freelancer",
     evidence=[...]
   )
"""

# MCP Tool Definition (what agents see)
MCP_TOOLS = [
    {
        "name": "agentcourt_resolve_dispute",
        "description": (
            "Resolve an agent commerce dispute using deterministic policy rules. "
            "Returns a ruling with remedy (full_refund, partial_refund, etc.), "
            "confidence level, and evidence scores. Supports 6 policy templates: "
            "freelance-delivery, milestone-payment, bug-bounty, sla-monitoring, "
            "api-quality, physical-commerce."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "policy": {
                    "type": "string",
                    "enum": [
                        "freelance-delivery",
                        "milestone-payment",
                        "bug-bounty",
                        "sla-monitoring",
                        "api-quality",
                        "physical-commerce",
                    ],
                    "description": "The dispute policy template to apply",
                },
                "claim": {
                    "type": "string",
                    "description": "Description of the dispute / what happened",
                },
                "claimant": {
                    "type": "string",
                    "description": "Name or ID of the party filing the claim",
                },
                "respondent": {
                    "type": "string",
                    "description": "Name or ID of the party being claimed against",
                },
                "desired_remedy": {
                    "type": "string",
                    "enum": [
                        "full_refund",
                        "partial_refund",
                        "full_payment",
                        "service_credit",
                        "full_payout",
                    ],
                    "description": "What the claimant wants",
                },
                "metadata": {
                    "type": "object",
                    "description": (
                        "Structured facts about the dispute. "
                        "This is the PRIMARY input for rule matching. "
                        "See policy template docs for required fields."
                    ),
                    "additionalProperties": True,
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": [
                                "contract", "log", "testimony", "payment_proof",
                                "assessment", "screenshot", "commit", "file",
                            ]},
                            "source": {"type": "string"},
                            "timestamp": {"type": "string"},
                            "claimed_fact": {"type": "string"},
                        },
                        "required": ["type", "claimed_fact"],
                    },
                    "description": "Evidence items supporting the claim",
                },
            },
            "required": ["policy", "claim", "claimant", "respondent"],
        },
    },
    {
        "name": "agentcourt_list_policies",
        "description": (
            "List all available dispute resolution policy templates. "
            "Returns template name, description, and rule count."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "agentcourt_get_verdict",
        "description": "Look up a previous verdict by case ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The unique case identifier",
                },
            },
            "required": ["case_id"],
        },
    },
]

# MCP client configuration examples
MCP_CLIENT_CONFIGS = {
    "claude_desktop": {
        "mcpServers": {
            "agentcourt": {
                "url": "https://agentcourt-api-production.up.railway.app/mcp",
                "transport": "http",
            }
        }
    },
    "cursor": {
        "mcp.servers": {
            "agentcourt": {
                "url": "https://agentcourt-api-production.up.railway.app/mcp",
            }
        }
    },
    "claude_code": {
        "mcp": {
            "agentcourt": {
                "type": "http",
                "url": "https://agentcourt-api-production.up.railway.app/mcp",
            }
        }
    },
}

# Example agent prompt that uses AgentCourt
EXAMPLE_AGENT_PROMPT = """
When a transaction dispute occurs:
1. Gather evidence (receipts, logs, screenshots, communications)
2. Determine the dispute type:
   - Freelance work not delivered → policy: "freelance-delivery"
   - Milestone not paid → policy: "milestone-payment"
   - Bug bounty rejected → policy: "bug-bounty"
   - Service downtime → policy: "sla-monitoring"
   - API returned bad data → policy: "api-quality"
   - Wrong product delivered → policy: "physical-commerce"
3. Call agentcourt_resolve_dispute with policy, claim, evidence, and metadata
4. Use the ruling to execute the remedy (refund, hold, escalate)
"""


if __name__ == "__main__":
    # Print MCP tool definitions for debugging
    import json
    print("AgentCourt MCP Tools:")
    for tool in MCP_TOOLS:
        print(f"\n  {tool['name']}:")
        print(f"    {tool['description'][:100]}...")
        props = tool.get("inputSchema", {}).get("properties", {})
        print(f"    Parameters: {list(props.keys())}")

    print("\n\nClient Configurations:")
    for client, config in MCP_CLIENT_CONFIGS.items():
        print(f"\n  {client}:")
        print(f"    {json.dumps(config, indent=2)}")
