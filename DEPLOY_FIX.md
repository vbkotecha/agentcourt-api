# AgentCourt API — Deploy Fix Guide

## The Problem
AgentCourt API is down. The Railway service `agentcourt-api` (9e9abcb2) got connected to the wrong GitHub repo (`hustlemode-voice`). It's serving voice server code instead of AgentCourt.

## Fix Option A: Railway CLI Token (30 seconds)

```bash
# 1. Go to railway.app → Settings → API Tokens
# 2. Create a PERSONAL token (not project-scoped)
# 3. Save it here:
echo "YOUR_TOKEN_HERE" > /root/.letta/keys/railway_cli_token.key

# 4. Deploy from local code:
cd /root/.letta/agentcourt
RAILWAY_TOKEN=$(cat /root/.letta/keys/railway_cli_token.key) railway up -s agentcourt-api
```

## Fix Option B: Browser Login (1 minute)

```bash
# Run browserless login and enter code at railway.com/activate
railway login --browserless

# Then deploy
cd /root/.letta/agentcourt
railway up -s agentcourt-api
```

## Fix Option C: Push to GitHub + Auto-Deploy (5 minutes)

```bash
# 1. Create empty repo: github.com/new → "agentcourt-api" (private)
# 2. Push local code:
cd /root/.letta/agentcourt
git remote add origin git@github.com:vbkotecha/agentcourt-api.git
git push -u origin main

# 3. On Railway dashboard:
#    - Go to agentcourt-api service
#    - Settings → Connect Repo → select agentcourt-api
#    - Auto-deploy will trigger
```

## Verify It Worked

```bash
curl https://agentcourt-api-production.up.railway.app/health
# Should return: {"status":"ok","version":"1.0.0",...}
# NOT: {"status":"ok","service":"hustlemode-voice"}
```

## Railway Service Details
- Project ID: cf922045-2612-49d4-b0b6-fef9c63bdb57
- Service ID: 9e9abcb2-c57e-4df8-b9cd-0d160ce2fd0d
- Environment ID: ac26fe55-88a1-4f24-9777-a142af59373b
- Domain: agentcourt-api-production.up.railway.app
- Current token: project-scoped (works for GraphQL API, not CLI)
