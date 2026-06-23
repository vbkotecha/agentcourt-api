#!/usr/bin/env python3
"""
AgentCourt E2E Integration Tests — validates all policies against live API.
Run: python3 tests/test_e2e_all_policies.py
"""
import json, sys, time, urllib.request, urllib.error

API = "https://agentcourt-api-production.up.railway.app"
CONTRACT = {"parties": ["a","b"], "obligations": ["deliver"]}
EV = lambda f: [{"type":"log","source":"sys","timestamp":"2026-06-23T00:00:00Z","claimed_fact":f}]

TESTS = [
    {"n":"freelance: non-delivery","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"No delivery","desired_remedy":"full_refund","policy":"freelance-delivery","evidence":EV("none"),"metadata":{"deadline_passed":True,"deliverable_received":False,"payment_made":True}},"e":"non-delivery"},
    {"n":"freelance: late","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"Late","desired_remedy":"partial_refund","policy":"freelance-delivery","evidence":EV("late"),"metadata":{"deadline_passed":True,"deliverable_received":True,"payment_made":True}},"e":"late"},
    {"n":"freelance: on time","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"OK","desired_remedy":"no_refund","policy":"freelance-delivery","evidence":EV("ok"),"metadata":{"deadline_passed":False,"deliverable_received":True,"payment_made":True}},"e":"no-violation"},
    {"n":"milestone: unpaid","r":{"claimant":"b","respondent":"a","contract":CONTRACT,"claim":"Unpaid","desired_remedy":"full_payment","policy":"milestone-payment","evidence":EV("unpaid"),"metadata":{"milestone_completed":True,"payment_received":False,"milestone_approved":True}},"e":"unpaid"},
    {"n":"milestone: overdue","r":{"claimant":"b","respondent":"a","contract":CONTRACT,"claim":"Overdue","desired_remedy":"full_payment_plus_penalty","policy":"milestone-payment","evidence":EV("overdue"),"metadata":{"milestone_completed":True,"payment_received":False,"days_overdue":30}},"e":"overdue"},
    {"n":"bugbounty: critical","r":{"claimant":"r","respondent":"c","contract":CONTRACT,"claim":"SQLi","desired_remedy":"full_payout","policy":"bug-bounty","evidence":EV("sqli"),"metadata":{"bug_reproducible":True,"bug_severity":"critical","followed_disclosure":True}},"e":"full-payout"},
    {"n":"bugbounty: not repro","r":{"claimant":"r","respondent":"c","contract":CONTRACT,"claim":"Bug","desired_remedy":"full_payout","policy":"bug-bounty","evidence":EV("norepro"),"metadata":{"bug_reproducible":False,"bug_severity":"medium","followed_disclosure":True}},"e":"not-reproducible"},
    {"n":"bugbounty: low","r":{"claimant":"r","respondent":"c","contract":CONTRACT,"claim":"UI","desired_remedy":"full_payout","policy":"bug-bounty","evidence":EV("ui"),"metadata":{"bug_reproducible":True,"bug_severity":"low","followed_disclosure":True}},"e":"low-severity"},
    {"n":"sla: uptime","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Low","desired_remedy":"service_credit","policy":"sla-monitoring","evidence":EV("95%"),"metadata":{"uptime_percentage":95.0,"sla_threshold":99.9}},"e":"uptime"},
    {"n":"sla: latency","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Slow","desired_remedy":"service_credit","policy":"sla-monitoring","evidence":EV("2000ms"),"metadata":{"p99_latency_ms":2000,"sla_latency_ms":500,"uptime_percentage":99.95}},"e":"latency"},
    {"n":"sla: ok","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Fine","desired_remedy":"service_credit","policy":"sla-monitoring","evidence":EV("99.98%"),"metadata":{"uptime_percentage":99.98,"sla_threshold":99.9,"p99_latency_ms":300,"sla_latency_ms":500}},"e":"no-violation"},
    {"n":"apiquality: schema","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Schema","desired_remedy":"full_refund","policy":"api-quality","evidence":EV("schema"),"metadata":{"response_received":True,"schema_matches":False}},"e":"schema"},
    {"n":"apiquality: stale","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Stale","desired_remedy":"partial_refund","policy":"api-quality","evidence":EV("stale"),"metadata":{"response_received":True,"schema_matches":True,"data_age_hours":168,"freshness_sla_hours":1}},"e":"stale"},
    {"n":"apiquality: ok","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Fine","desired_remedy":"full_refund","policy":"api-quality","evidence":EV("ok"),"metadata":{"response_received":True,"schema_matches":True}},"e":"no-violation"},
    {"n":"commerce: wrong","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Wrong","desired_remedy":"replacement","policy":"physical-commerce","evidence":EV("wrong"),"metadata":{"item_received":True,"item_matches_description":False,"wrong_item":True}},"e":"wrong-item"},
    {"n":"commerce: damaged","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Damaged","desired_remedy":"replacement","policy":"physical-commerce","evidence":EV("damaged"),"metadata":{"item_received":True,"item_matches_description":False,"damaged":True}},"e":"damaged"},
    {"n":"commerce: non-delivery","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Never","desired_remedy":"full_refund","policy":"physical-commerce","evidence":EV("none"),"metadata":{"item_received":False,"delivery_deadline_passed":True,"payment_made":True}},"e":"non-delivery"},
]

def run():
    print("=" * 60)
    print("AgentCourt E2E Integration Tests")
    print("=" * 60)
    try:
        r = urllib.request.urlopen(f"{API}/health", timeout=5)
        h = json.loads(r.read())
        print(f"\nHealth: {h['status']} | {len(h['policies'])} policies\n")
    except: print("\nFATAL: API unreachable\n"); sys.exit(1)

    passed, latencies = 0, []
    for t in TESTS:
        try:
            data = json.dumps(t["r"]).encode()
            req = urllib.request.Request(f"{API}/v1/disputes", data=data,
                headers={"Content-Type":"application/json"}, method="POST")
            start = time.time()
            resp = urllib.request.urlopen(req, timeout=10)
            ms = int((time.time() - start) * 1000)
            result = json.loads(resp.read())
            matched = result.get("matched_rule_id","")
            ok = t["e"].lower() in matched.lower()
            print(f"  [{'PASS' if ok else 'FAIL'}] {t['n']} -> {matched} ({ms}ms)")
            if ok: passed += 1; latencies.append(ms)
        except urllib.error.HTTPError as e:
            print(f"  [ERR] {t['n']} -> {e.code}: {e.read().decode()[:80]}")
        except Exception as e:
            print(f"  [ERR] {t['n']} -> {str(e)[:50]}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(TESTS)} passed")
    if latencies:
        print(f"Latency: avg={sum(latencies)//len(latencies)}ms min={min(latencies)}ms max={max(latencies)}ms")
    print("=" * 60)

if __name__ == "__main__":
    run()
