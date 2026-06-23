# AgentCourt MCP Server

Model Context Protocol server exposing AgentCourt dispute resolution tools to Claude, Cursor, and any MCP client.

## Tools

| Tool | Description |
|------|-------------|
| `file_dispute` | File a dispute and get a deterministic ruling in <500ms |
| `list_policies` | List all 7 policy templates |
| `get_policy_details` | Get rules for a specific policy |
| `get_case` | Retrieve a filed case by ID |
| `list_verdicts` | Browse recent verdicts |
| `health_check` | Check API status |

## Quick Start

```bash
# Install
pip install mcp httpx

# Run
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "agentcourt": {
      "command": "python",
      "args": ["/path/to/agentcourt/mcp-server/server.py"]
    }
  }
}
```

## Example: File a Dispute

Ask Claude: "The API I paid for returned XML instead of JSON. File a dispute."

Claude will call `file_dispute` with:
- policy: `api-quality`
- delivered: true
- meets_spec: false

And return: `{"ruling": "full_refund", "confidence": 0.95, ...}`

## Policies

- `api-quality`: Schema mismatch, wrong response formats (7 rules)
- `freelance-delivery`: Non-delivery, late delivery (5 rules)
- `milestone-payment`: Unpaid milestones (6 rules)
- `bug-bounty`: Severity disputes (5 rules)
- `sla-monitoring`: Uptime violations (6 rules)
- `scope-dispute`: Budget exceedance (4 rules)
- `physical-commerce`: Damaged goods (6 rules)

## Links

- [AgentCourt API](https://agentcourt-api-production.up.railway.app/docs)
- [GitHub](https://github.com/vbkotecha/agentcourt-api)
- [Full Integration Guide](https://github.com/vbkotecha/agentcourt-api/discussions/3)
