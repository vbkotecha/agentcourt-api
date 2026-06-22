/**
 * AgentCourt SDK — Type definitions
 */

export interface AgentCourtOptions {
  baseUrl?: string;
  timeout?: number;
}

export interface EvidenceItem {
  type: string;
  source: string;
  timestamp?: string;
  claimedFact: string;
  reliability?: 'high' | 'medium' | 'low';
  excerpt?: string;
}

export interface ContractTerms {
  parties: string[];
  obligations: string[];
  deadlines?: string[];
  deliverables?: string[];
  payment_terms?: string;
  definitions?: Record<string, unknown>;
}

export interface ResolveParams {
  policy?: 'freelance-delivery' | 'milestone-payment' | 'bug-bounty';
  claimant: string;
  respondent: string;
  claim: string;
  desiredRemedy: string;
  contract?: ContractTerms;
  evidence: EvidenceItem[];
}

export interface Fact {
  fact: string;
  value: string | boolean | number | null;
  reason?: string;
}

export interface EvidenceScore {
  id: string;
  type: string;
  score: number;
}

export interface Ruling {
  case_id: string;
  status: 'ruled' | 'needs_more_info';
  confidence: 'high' | 'medium' | 'low';
  ruling: string;
  reasoning: string;
  remedy: string;
  matched_rule_id: string;
  policy_name: string;
  policy_version: string;
  facts_established: Fact[];
  facts_disputed: Fact[];
  facts_unknown: Fact[];
  evidence_scores: EvidenceScore[];
  ruled_at: string;
  engine_version: string;
}

export interface Policy {
  name: string;
  version: string;
  description: string;
  rules_count: number;
  rules: PolicyRule[];
}

export interface PolicyRule {
  id: string;
  name: string;
  condition: string;
  remedy: string;
  confidence: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  data_dir: string;
  engine: string;
  policies: string[];
}

export declare class AgentCourt {
  constructor(options?: AgentCourtOptions);
  resolve(params: ResolveParams): Promise<Ruling>;
  listPolicies(): Promise<Policy[]>;
  getPolicy(name: string): Promise<Policy>;
  getCase(caseId: string): Promise<Ruling>;
  health(): Promise<HealthStatus>;
}
