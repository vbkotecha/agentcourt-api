"""
AgentCourt MCP Server — Exposes dispute resolution as MCP tools.

Usage by agents:
  - resolve_dispute: Submit a dispute and get a ruling
  - list_policies: See available policy templates
  - get_policy: Read the rules of a specific policy
  - get_case: Retrieve a past case by ID

Transport: stdio (for local agents) or HTTP (for remote agents)
"""

import json
import sys
import urllib.request
import urllib.error

# AgentCourt API base URL
API_BASE = "https://agentcourt-api-production.up.railway.app"

# ─── MCP Protocol Implementation ──────────────────────────────────────────────

def handle_initialize(params):
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "agentcourt",
            "version": "1.0.0"
        }
    }

def handle_tools_list(params):
    return {
        "tools": [
            {
                "name": "resolve_dispute",
                "description": "Submit a dispute to AgentCourt for policy-driven resolution. Returns ruling, confidence band (high/medium/low), remedy, reasoning, and full audit trail.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "policy": {
                            "type": "string",
                            "description": "Policy template: 'freelance-delivery', 'milestone-payment', or 'bug-bounty'",
                            "default": "freelance-delivery"
                        },
                        "claimant": {
                            "type": "string",
                            "description": "Name/ID of the party filing the dispute"
                        },
                        "respondent": {
                            "type": "string",
                            "description": "Name/ID of the party being disputed against"
                        },
                        "claim": {
                            "type": "string",
                            "description": "Description of what went wrong"
                        },
                        "desired_remedy": {
                            "type": "string",
                            "description": "What the claimant wants: 'full_refund', 'partial_refund', 'payment', 'deny', etc."
                        },
                        "contract_parties": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Parties involved in the contract"
                        },
                        "contract_obligations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Obligations defined in the contract"
                        },
                        "contract_deadlines": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Deadlines in ISO format (e.g., '2026-06-15')"
                        },
                        "contract_deliverables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Expected deliverables"
                        },
                        "contract_payment_terms": {
                            "type": "string",
                            "description": "Payment terms (e.g., '5 USDC on delivery')"
                        },
                        "evidence": {
                            "type": "array",
                            "description": "Evidence items supporting the claim",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "description": "contract, payment_proof, message, commit, log, screenshot, file, other"},
                                    "source": {"type": "string", "description": "Where the evidence comes from"},
                                    "timestamp": {"type": "string", "description": "ISO format timestamp"},
                                    "claimed_fact": {"type": "string", "description": "What this evidence proves"},
                                    "reliability": {"type": "string", "description": "high, medium, or low"},
                                    "excerpt": {"type": "string", "description": "Optional relevant excerpt"}
                                },
                                "required": ["type", "source", "claimed_fact"]
                            }
                        }
                    },
                    "required": ["claimant", "respondent", "claim", "desired_remedy", "evidence"]
                }
            },
            {
                "name": "list_policies",
                "description": "List all available AgentCourt policy templates with their rules.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_policy",
                "description": "Get details of a specific policy template including all rules.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "policy_name": {"type": "string", "description": "Policy template name"}
                    },
                    "required": ["policy_name"]
                }
            },
            {
                "name": "get_case",
                "description": "Retrieve a past dispute case by its ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "case_id": {"type": "string", "description": "The case ID returned from resolve_dispute"}
                    },
                    "required": ["case_id"]
                }
            },
            {
                "name": "health_check",
                "description": "Check if the AgentCourt API is online and healthy.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
    }

def handle_tools_call(params):
    tool_name = params.get("name")
    args = params.get("arguments", {})
    
    if tool_name == "resolve_dispute":
        contract = {}
        if args.get("contract_parties"):
            contract["parties"] = args["contract_parties"]
        if args.get("contract_obligations"):
            contract["obligations"] = args["contract_obligations"]
        if args.get("contract_deadlines"):
            contract["deadlines"] = args["contract_deadlines"]
        if args.get("contract_deliverables"):
            contract["deliverables"] = args["contract_deliverables"]
        if args.get("contract_payment_terms"):
            contract["payment_terms"] = args["contract_payment_terms"]
        
        return call_api("POST", "/v1/disputes", {
            "policy": args.get("policy", "freelance-delivery"),
            "claimant": args.get("claimant", "unknown"),
            "respondent": args.get("respondent", "unknown"),
            "contract": contract,
            "claim": args.get("claim", ""),
            "desired_remedy": args.get("desired_remedy", ""),
            "evidence": [
                {
                    "type": e.get("type", "other"),
                    "source": e.get("source", ""),
                    "timestamp": e.get("timestamp", ""),
                    "claimed_fact": e.get("claimed_fact", ""),
                    "reliability": e.get("reliability"),
                    "excerpt": e.get("excerpt")
                }
                for e in args.get("evidence", [])
            ]
        })
    
    elif tool_name == "list_policies":
        return call_api("GET", "/v1/policies")
    
    elif tool_name == "get_policy":
        name = args.get("policy_name", "")
        return call_api("GET", f"/v1/policies/{name}")
    
    elif tool_name == "get_case":
        case_id = args.get("case_id", "")
        return call_api("GET", f"/cases/{case_id}")
    
    elif tool_name == "health_check":
        return call_api("GET", "/health")
    
    else:
        return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}], "isError": True}

def call_api(method, path, body=None):
    try:
        url = f"{API_BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"} if data else {},
            method=method
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            "isError": False
        }
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {
            "content": [{"type": "text", "text": f"API Error {e.code}: {body}"}],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }

# ─── stdio Transport ─────────────────────────────────────────────────────────

def main():
    """Run the MCP server over stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            msg = json.loads(line)
            method = msg.get("method")
            msg_id = msg.get("id")
            params = msg.get("params", {})
            
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "tools/list":
                result = handle_tools_list(params)
            elif method == "tools/call":
                result = handle_tools_call(params)
            elif method == "notifications/initialized":
                continue  # No response needed
            else:
                result = {"error": {"code": -32601, "message": f"Unknown method: {method}"}}
            
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            if msg_id:
                response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(e)}}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
