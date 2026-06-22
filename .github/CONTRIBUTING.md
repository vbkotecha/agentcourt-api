# Contributing to AgentCourt

Thank you for your interest in contributing! AgentCourt is open source (MIT) and welcomes all contributions.

## Ways to Contribute

### 1. Policy Templates
The most impactful way to contribute. Create a new JSON policy template for a dispute domain we don't cover.

**Steps:**
1. Study existing templates in `src/policies/`
2. Create a new `.json` file with rules, conditions, remedies, and confidence bands
3. Test locally: `python3 -c "from src.engine.policy_engine import evaluate_dispute; ..."`
4. Test against live API: `POST https://agentcourt-api-production.up.railway.app/v1/disputes`
5. Submit a PR

**Template structure:**
```json
{
  "name": "your-template",
  "version": "1.0",
  "description": "...",
  "rules": [
    {
      "id": "rule-name",
      "condition": "fact == value AND other_fact == true",
      "ruling_template": "Description of what happened...",
      "confidence": "high",
      "remedy": "full_refund",
      "facts_required": ["fact", "other_fact"]
    }
  ],
  "evidence_weights": { "contract": 1.0, "log": 0.6, "testimony": 0.3 },
  "thresholds": { ... }
}
```

### 2. Bug Reports
Use the Bug Report issue template. Include the dispute payload and expected vs actual ruling.

### 3. SDK Improvements
The SDKs in `sdk/` are zero-dependency by design. If you add features, keep them stdlib-only (Python) or browser-compatible (JS).

### 4. Documentation
Found a typo? Instructions unclear? PRs welcome.

## Development Setup

```bash
git clone https://github.com/vbkotecha/agentcourt-api.git
cd agentcourt-api
pip install fastapi uvicorn pydantic  # only deps needed
python3 -m uvicorn src.main:app --reload
```

## Testing

```bash
# Run all tests
python3 -m pytest tests/

# Test against live API
python3 examples/agentcash_integration_demo.py
```

## Code Style

- Python: PEP 8, type hints encouraged
- JavaScript: ESM preferred, CommonJS fallback
- JSON: 2-space indent, no trailing commas
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, etc.)

## License

By contributing, you agree that your contributions are licensed under the MIT License.
