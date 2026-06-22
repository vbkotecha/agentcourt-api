/**
 * AgentCourt SDK — Policy-driven dispute resolution for AI agent commerce.
 *
 * Zero-dependency. Works in Node.js and browsers.
 *
 * @example
 * const { AgentCourt } = require('@agentcourt/sdk');
 * const court = new AgentCourt();
 * const ruling = await court.resolve({
 *   policy: 'freelance-delivery',
 *   claimant: 'buyer_agent',
 *   respondent: 'seller_agent',
 *   claim: 'Deliverable never received',
 *   desiredRemedy: 'full_refund',
 *   contract: { parties: ['buyer_agent', 'seller_agent'], ... },
 *   evidence: [{ type: 'contract', source: 'agreement.json', claimedFact: 'Deadline: June 15' }]
 * });
 * console.log(ruling.confidence); // 'high' | 'medium' | 'low'
 * console.log(ruling.remedy);     // 'full_refund' | 'partial_refund' | ...
 */

const DEFAULT_BASE_URL = 'https://agentcourt-api-production.up.railway.app';

class AgentCourt {
  /**
   * @param {Object} options
   * @param {string} [options.baseUrl] - Override the API base URL
   * @param {number} [options.timeout=10000] - Request timeout in ms
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || DEFAULT_BASE_URL;
    this.timeout = options.timeout || 10000;
  }

  /**
   * Submit a dispute for resolution.
   * @param {Object} params
   * @param {string} params.policy - Policy template: 'freelance-delivery', 'milestone-payment', 'bug-bounty'
   * @param {string} params.claimant - Name/ID of the party filing the dispute
   * @param {string} params.respondent - Name/ID of the party being disputed
   * @param {string} params.claim - Description of what went wrong
   * @param {string} params.desiredRemedy - What the claimant wants
   * @param {Object} params.contract - Contract terms
   * @param {Array} params.evidence - Evidence items
   * @returns {Promise<Ruling>} The ruling
   */
  async resolve(params) {
    const body = {
      policy: params.policy || 'freelance-delivery',
      claimant: params.claimant,
      respondent: params.respondent,
      contract: params.contract || {},
      claim: params.claim,
      desired_remedy: params.desiredRemedy,
      evidence: (params.evidence || []).map(e => ({
        type: e.type || 'other',
        source: e.source || '',
        timestamp: e.timestamp || '',
        claimed_fact: e.claimedFact || e.claimed_fact || '',
        reliability: e.reliability || null,
        excerpt: e.excerpt || null,
      })),
    };

    return this._request('POST', '/v1/disputes', body);
  }

  /**
   * List all available policy templates.
   * @returns {Promise<Array>} Array of policy templates
   */
  async listPolicies() {
    return this._request('GET', '/v1/policies');
  }

  /**
   * Get details of a specific policy template.
   * @param {string} name - Policy template name
   * @returns {Promise<Object>} Policy details
   */
  async getPolicy(name) {
    return this._request('GET', `/v1/policies/${name}`);
  }

  /**
   * Retrieve a past case by ID.
   * @param {string} caseId - Case ID
   * @returns {Promise<Object>} Case details
   */
  async getCase(caseId) {
    return this._request('GET', `/cases/${caseId}`);
  }

  /**
   * Check API health.
   * @returns {Promise<Object>} Health status
   */
  async health() {
    return this._request('GET', '/health');
  }

  /**
   * @private
   */
  async _request(method, path, body) {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const options = {
      method,
      signal: controller.signal,
      headers: {},
    };

    if (body) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }

    try {
      // Use global fetch (Node 18+ / browser)
      const fetchFn = typeof fetch !== 'undefined' ? fetch : require('node-fetch');
      const resp = await fetchFn(url, options);
      const data = await resp.json();

      if (!resp.ok) {
        const err = new Error(`AgentCourt API Error ${resp.status}: ${JSON.stringify(data)}`);
        err.status = resp.status;
        err.body = data;
        throw err;
      }

      clearTimeout(timeoutId);
      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error(`Request timed out after ${this.timeout}ms`);
      }
      throw err;
    }
  }
}

/**
 * @typedef {Object} Ruling
 * @property {string} case_id - Unique case identifier
 * @property {string} status - Case status ('ruled', 'needs_more_info')
 * @property {string} confidence - Confidence band ('high', 'medium', 'low')
 * @property {string} ruling - Human-readable ruling text
 * @property {string} reasoning - Reasoning chain
 * @property {string} remedy - Recommended remedy
 * @property {string} matched_rule_id - Policy rule that matched
 * @property {string} policy_name - Policy template used
 * @property {Array} facts_established - Facts established from evidence
 * @property {Array} facts_disputed - Facts that are contested
 * @property {Array} facts_unknown - Facts that couldn't be determined
 * @property {Array} evidence_scores - Per-evidence scoring
 * @property {string} ruled_at - ISO timestamp
 * @property {string} engine_version - Engine version
 */

module.exports = { AgentCourt };
