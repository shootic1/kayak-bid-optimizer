/** Zod schemas for bid files, optimization runs, and recommendations. */

import { z } from 'zod';

export const matchStatusSchema = z.enum([
  'matched',
  'unmatched_no_history',
  'unmatched_non_iata',
  'skipped_excluded',
]);

export const runStatusSchema = z.enum(['pending', 'running', 'completed', 'failed']);

export const deviceTypeSchema = z.enum(['all', 'desktop', 'mobile']);

export const recommendationActionSchema = z.enum([
  'keep',
  'increase',
  'manual_review',
  'insufficient_data',
]);

export const confidenceLevelSchema = z.enum(['high', 'medium', 'low']);

export const bidFileSchema = z.object({
  id: z.number(),
  provider_code: z.string(),
  mode: z.string(),
  original_filename: z.string(),
  file_type: z.string(),
  file_size: z.number(),
  route_count: z.number(),
  uploaded_at: z.string(),
});

export const bidFileListResponseSchema = z.object({
  items: z.array(bidFileSchema),
  total: z.number(),
  limit: z.number(),
  offset: z.number(),
});

export const optimizationRunSchema = z.object({
  id: z.number(),
  bid_file_id: z.number(),
  status: runStatusSchema,
  ruleset_version: z.string(),
  total_routes: z.number(),
  matched_count: z.number(),
  unmatched_count: z.number(),
  skipped_count: z.number(),
  recommendation_count: z.number(),
  error_message: z.string().nullable(),
  started_at: z.string(),
  finished_at: z.string().nullable(),
});

export const optimizationRunListResponseSchema = z.object({
  items: z.array(optimizationRunSchema),
  total: z.number(),
  limit: z.number(),
  offset: z.number(),
});

export const ruleResultSchema = z.object({
  rule_key: z.string(),
  rule_version: z.string(),
  triggered: z.boolean(),
  weight: z.number(),
  signal: z.number(),
  detail: z.record(z.string(), z.unknown()),
});

export const recommendationSchema = z.object({
  id: z.number(),
  optimization_run_id: z.number(),
  bid_file_route_id: z.number(),
  route_summary_id: z.number().nullable(),
  match_status: matchStatusSchema,
  origin: z.string(),
  destination: z.string(),
  device: deviceTypeSchema.nullable(),
  action: recommendationActionSchema,
  rule_triggered: z.string().nullable(),
  confidence_level: confidenceLevelSchema.nullable(),
  manual_review: z.boolean(),
  current_bid: z.number().nullable(),
  recommended_bid: z.number().nullable(),
  difference: z.number().nullable(),
  pct_change: z.number().nullable(),
  current_position: z.number().nullable(),
  ctr: z.number().nullable(),
  clicks: z.number().nullable(),
  impressions: z.number().nullable(),
  spend: z.number().nullable(),
  confidence: z.number().nullable(),
  reason: z.string().nullable(),
  created_at: z.string(),
});

export const recommendationDetailSchema = recommendationSchema.extend({
  rule_results: z.array(ruleResultSchema),
});

export const recommendationListResponseSchema = z.object({
  items: z.array(recommendationSchema),
  total: z.number(),
  limit: z.number(),
  offset: z.number(),
});

export const exportSkippedRouteSchema = z.object({
  origin: z.string(),
  destination: z.string(),
  reason: z.string(),
});

export const exportSummarySchema = z.object({
  output_filename: z.string(),
  routes_processed: z.number(),
  routes_updated: z.number(),
  routes_unchanged: z.number(),
  manual_review_count: z.number(),
  insufficient_data_count: z.number(),
  average_bid_increase: z.number(),
  maximum_bid_increase: z.number(),
  skipped_routes: z.array(exportSkippedRouteSchema),
  strategy_version: z.string(),
  timestamp: z.string(),
});
