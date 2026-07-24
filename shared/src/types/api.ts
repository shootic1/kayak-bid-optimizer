/**
 * API contract types.
 *
 * Derived from the Zod schemas so validation and types never drift (DRY).
 */

import type { z } from 'zod';

import type {
  dependencyHealthSchema,
  healthResponseSchema,
  healthStatusSchema,
  readinessResponseSchema,
  versionResponseSchema,
} from '../validation/api';

export type HealthStatus = z.infer<typeof healthStatusSchema>;
export type HealthResponse = z.infer<typeof healthResponseSchema>;
export type DependencyHealth = z.infer<typeof dependencyHealthSchema>;
export type ReadinessResponse = z.infer<typeof readinessResponseSchema>;
export type VersionResponse = z.infer<typeof versionResponseSchema>;

/** Reachability state for a monitored system dependency (frontend view model). */
export type ConnectionState = 'online' | 'offline' | 'loading';
