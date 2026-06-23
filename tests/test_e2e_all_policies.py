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
    {"n":"freelance: non-delivery","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"No delivery","desired_remedy":"full_refund","policy":"freelance-delivery","evidence":EV("no delivery"),"metadata":{"deliverable_was_accepted":False,"evidence_of_delivery":False}},"e":"non-delivery"},
    {"n":"freelance: late","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"Late","desired_remedy":"partial_refund","policy":"freelance-delivery","evidence":EV("late"),"metadata":{"deliverable_was_accepted":True,"delivery_was_on_time":False}},"e":"late-delivery"},
    {"n":"freelance: on time","r":{"claimant":"a","respondent":"b","contract":CONTRACT,"claim":"OK","desired_remedy":"no_refund","policy":"freelance-delivery","evidence":EV("on time"),"metadata":{"deliverable_was_accepted":True,"delivery_was_on_time":True}},"e":"delivery-on-time"},
    {"n":"milestone: unpaid","r":{"claimant":"b","respondent":"a","contract":CONTRACT,"claim":"Unpaid 45 days","desired_remedy":"full_payment","policy":"milestone-payment","evidence":EV("unpaid"),"metadata":{"milestone_completed":True,"payment_received":False,"days_since_completion":45,"payment_terms_days":30}},"e":"unpaid"},
    {"n":"bugbounty: valid","r":{"claimant":"r","respondent":"c","contract":CONTRACT,"claim":"SQLi","desired_remedy":"full_payout","policy":"bug-bounty","evidence":EV("sqli"),"metadata":{"bug_is_reproducible":True,"severity_meets_threshold":True,"disclosure_compliant":True}},"e":"full-payout"},
    {"n":"bugbounty: not repro","r":{"claimant":"r","respondent":"c","contract":CONTRACT,"claim":"Bug","desired_remedy":"full_payout","policy":"bug-bounty","evidence":EV("not repro"),"metadata":{"bug_is_reproducible":False,"reproduction_attempts":5}},"e":"non-reproducible"},
    {"n":"sla: uptime","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Low","desired_remedy":"service_credit","policy":"sla-monitoring","evidence":EV("95%"),"metadata":{"actual_uptime":95.0,"required_uptime":99.9,"monitoring_period_confirmed":True}},"e":"uptime"},
    {"n":"sla: latency","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Slow","desired_remedy":"service_credit","policy":"sla-monitoring","evidence":EV("slow"),"metadata":{"actual_latency":2000,"max_latency":500,"monitoring_period_confirmed":True}},"e":"latency"},
    {"n":"apiquality: schema","r":{"claimant":"c","respondent":"p","contract":CONTRACT,"claim":"Schema","desired_remedy":"full_refund","policy":"api-quality","evidence":EV("schema"),"metadata":{"response_received":True,"schema_matches":False}},"e":"schema-mismatch"},
    {"n":"commerce: non-delivery","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Never","desired_remedy":"full_refund","policy":"physical-commerce","evidence":EV("none"),"metadata":{"delivery_confirmed":False,"days_since_order":30,"delivery_window_days":7}},"e":"non-delivery"},
    {"n":"commerce: wrong","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Wrong","desired_remedy":"replacement","policy":"physical-commerce","evidence":EV("wrong"),"metadata":{"delivery_confirmed":True,"received_matches_order":False}},"e":"wrong-product"},
    {"n":"commerce: damaged","r":{"claimant":"b","respondent":"s","contract":CONTRACT,"claim":"Damaged","desired_remedy":"replacement","policy":"physical-commerce","evidence":EV("damaged"),"metadata":{"delivery_confirmed":True,"shipping_damage":True}},"e":"damaged"},
]

def run():
    print("=" * 60)
    print("AgentCourt E2E Integration Tests — All Policies")
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
