/**
 * System-status service — fetches backend liveness, readiness, and version
 * using the typed API client and shared contracts.
 */

import {
  API_ENDPOINTS,
  type HealthResponse,
  healthResponseSchema,
  type ReadinessResponse,
  readinessResponseSchema,
  type VersionResponse,
  versionResponseSchema,
} from '@kayak/shared';

import { apiGet, type ApiResult } from '@/services/api-client';

export function fetchHealth(signal?: AbortSignal): Promise<ApiResult<HealthResponse>> {
  return apiGet(API_ENDPOINTS.health, healthResponseSchema, { signal });
}

export function fetchReadiness(signal?: AbortSignal): Promise<ApiResult<ReadinessResponse>> {
  return apiGet(API_ENDPOINTS.ready, readinessResponseSchema, { signal });
}

export function fetchVersion(signal?: AbortSignal): Promise<ApiResult<VersionResponse>> {
  return apiGet(API_ENDPOINTS.version, versionResponseSchema, { signal });
}
