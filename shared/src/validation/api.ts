/**
 * Zod schemas for backend API responses.
 *
 * These are the single source of truth for both runtime validation and the
 * derived TypeScript types (see `../types/api.ts`). The wire format mirrors the
 * backend Pydantic schemas exactly (snake_case where applicable).
 */

import { z } from 'zod';

export const healthStatusSchema = z.enum(['healthy', 'degraded', 'unhealthy']);

export const healthResponseSchema = z.object({
  status: healthStatusSchema,
  service: z.string(),
  version: z.string(),
});

export const dependencyHealthSchema = z.object({
  name: z.string(),
  status: healthStatusSchema,
  detail: z.string().nullish(),
  latency_ms: z.number().nullish(),
});

export const readinessResponseSchema = z.object({
  status: healthStatusSchema,
  service: z.string(),
  version: z.string(),
  dependencies: z.array(dependencyHealthSchema),
});

export const versionResponseSchema = z.object({
  name: z.string(),
  version: z.string(),
  environment: z.string(),
});
