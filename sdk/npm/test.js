/**
 * AgentCourt SDK — Test suite
 * Run: node test.js
 */

const { AgentCourt } = require('./index.js');

async function runTests() {
  const court = new AgentCourt();
  let passed = 0;
  let failed = 0;

  function assert(condition, name) {
    if (condition) {
      console.log(`  ✅ ${name}`);
      passed++;
    } else {
      console.log(`  ❌ ${name}`);
      failed++;
    }
  }

  console.log('AgentCourt SDK Tests\n');

  // Test 1: Health check
  console.log('Test 1: Health Check');
  try {
    const health = await court.health();
    assert(health.status === 'ok', 'Health returns ok');
    assert(health.policies.length === 3, 'Has 3 policy templates');
    assert(health.engine === 'policy-engine-v1', 'Engine is policy-engine-v1');
  } catch (e) {
    console.log(`  ❌ Health check failed: ${e.message}`);
    failed++;
  }

  // Test 2: List policies
  console.log('\nTest 2: List Policies');
  try {
    const policies = await court.listPolicies();
    assert(Array.isArray(policies), 'Returns array');
    assert(policies.length === 3, 'Has 3 policies');
    assert(policies.some(p => p.name === 'freelance-delivery'), 'Has freelance-delivery');
    assert(policies.some(p => p.name === 'milestone-payment'), 'Has milestone-payment');
    assert(policies.some(p => p.name === 'bug-bounty'), 'Has bug-bounty');
  } catch (e) {
    console.log(`  ❌ List policies failed: ${e.message}`);
    failed++;
  }

  // Test 3: Get specific policy
  console.log('\nTest 3: Get Policy Detail');
  try {
    const policy = await court.getPolicy('freelance-delivery');
    assert(policy.name === 'freelance-delivery', 'Returns correct policy');
    assert(policy.rules && policy.rules.length > 0, 'Has rules');
  } catch (e) {
    console.log(`  ❌ Get policy failed: ${e.message}`);
    failed++;
  }

  // Test 4: Resolve dispute (non-delivery)
  console.log('\nTest 4: Resolve Dispute (Non-Delivery)');
  try {
    const ruling = await court.resolve({
      policy: 'freelance-delivery',
      claimant: 'test_buyer',
      respondent: 'test_seller',
      claim: 'Deliverable was never received',
      desiredRemedy: 'full_refund',
      contract: {
        parties: ['test_buyer', 'test_seller'],
        obligations: ['Deliver API code by June 15'],
        deadlines: ['2026-06-15'],
        deliverables: ['API integration code'],
        payment_terms: '5 USDC on delivery',
      },
      evidence: [
        { type: 'contract', source: 'agreement.json', timestamp: '2026-06-10', claimedFact: 'Seller must deliver by June 15' },
        { type: 'payment_proof', source: 'receipt', timestamp: '2026-06-10', claimedFact: 'Buyer paid 5 USDC' },
        { type: 'log', source: 'git_history', timestamp: '2026-06-20', claimedFact: 'No commits after June 10' },
      ],
    });
    assert(ruling.case_id, 'Returns case_id');
    assert(ruling.confidence, 'Returns confidence');
    assert(ruling.remedy, 'Returns remedy');
    assert(ruling.matched_rule_id === 'non-delivery', 'Matches non-delivery rule');
    assert(Array.isArray(ruling.facts_established), 'Returns facts_established');
  } catch (e) {
    console.log(`  ❌ Resolve dispute failed: ${e.message}`);
    failed++;
  }

  // Summary
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(e => {
  console.error('Test suite crashed:', e);
  process.exit(1);
});
