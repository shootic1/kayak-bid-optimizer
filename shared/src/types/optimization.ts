/** Optimization contract types, derived from the Zod schemas (DRY). */

import type { z } from 'zod';

import type {
  bidFileListResponseSchema,
  bidFileSchema,
  confidenceLevelSchema,
  deviceTypeSchema,
  matchStatusSchema,
  optimizationRunListResponseSchema,
  optimizationRunSchema,
  recommendationActionSchema,
  recommendationDetailSchema,
  recommendationListResponseSchema,
  recommendationSchema,
  ruleResultSchema,
  runStatusSchema,
} from '../validation/optimization';

export type MatchStatus = z.infer<typeof matchStatusSchema>;
export type RunStatus = z.infer<typeof runStatusSchema>;
export type DeviceType = z.infer<typeof deviceTypeSchema>;
export type RecommendationAction = z.infer<typeof recommendationActionSchema>;
export type ConfidenceLevel = z.infer<typeof confidenceLevelSchema>;
export type BidFile = z.infer<typeof bidFileSchema>;
export type BidFileListResponse = z.infer<typeof bidFileListResponseSchema>;
export type OptimizationRun = z.infer<typeof optimizationRunSchema>;
export type OptimizationRunListResponse = z.infer<typeof optimizationRunListResponseSchema>;
export type RuleResult = z.infer<typeof ruleResultSchema>;
export type Recommendation = z.infer<typeof recommendationSchema>;
export type RecommendationDetail = z.infer<typeof recommendationDetailSchema>;
export type RecommendationListResponse = z.infer<typeof recommendationListResponseSchema>;
