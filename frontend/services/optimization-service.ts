/** Optimization API service: bid files, runs, and recommendations. */

import {
  API_ENDPOINTS,
  type BidFile,
  type BidFileListResponse,
  bidFileListResponseSchema,
  bidFileSchema,
  type MatchStatus,
  type OptimizationRun,
  type OptimizationRunListResponse,
  optimizationRunListResponseSchema,
  optimizationRunPath,
  optimizationRunSchema,
  type RecommendationDetail,
  type RecommendationListResponse,
  recommendationDetailSchema,
  recommendationListResponseSchema,
  recommendationPath,
} from '@kayak/shared';

import { env } from '@/lib/env';
import { apiGet, type ApiResult } from '@/services/api-client';

export function listBidFiles(signal?: AbortSignal): Promise<ApiResult<BidFileListResponse>> {
  return apiGet(`${API_ENDPOINTS.bidFiles}?limit=100`, bidFileListResponseSchema, { signal });
}

export function listRuns(signal?: AbortSignal): Promise<ApiResult<OptimizationRunListResponse>> {
  return apiGet(`${API_ENDPOINTS.optimizationRuns}?limit=100`, optimizationRunListResponseSchema, {
    signal,
  });
}

export function getRun(id: number, signal?: AbortSignal): Promise<ApiResult<OptimizationRun>> {
  return apiGet(optimizationRunPath(id), optimizationRunSchema, { signal });
}

export function getRecommendation(
  id: number,
  signal?: AbortSignal,
): Promise<ApiResult<RecommendationDetail>> {
  return apiGet(recommendationPath(id), recommendationDetailSchema, { signal });
}

export function listRecommendations(
  params: {
    runId: number;
    status?: MatchStatus;
    minConfidence?: number;
    limit?: number;
    offset?: number;
  },
  signal?: AbortSignal,
): Promise<ApiResult<RecommendationListResponse>> {
  const query = new URLSearchParams({
    run_id: String(params.runId),
    limit: String(params.limit ?? 100),
    offset: String(params.offset ?? 0),
  });
  if (params.status) query.set('status', params.status);
  if (params.minConfidence !== undefined) query.set('min_confidence', String(params.minConfidence));
  return apiGet(
    `${API_ENDPOINTS.recommendations}?${query.toString()}`,
    recommendationListResponseSchema,
    { signal },
  );
}

export async function uploadBidFile(file: File): Promise<ApiResult<BidFile>> {
  const form = new FormData();
  form.append('file', file);
  try {
    const response = await fetch(`${env.apiOrigin}${API_ENDPOINTS.bidFiles}`, {
      method: 'POST',
      body: form,
    });
    const body: unknown = await response.json();
    if (response.status === 201) {
      const parsed = bidFileSchema.safeParse(body);
      return parsed.success
        ? { ok: true, data: parsed.data }
        : { ok: false, error: 'Unexpected response shape' };
    }
    return { ok: false, error: extractError(body, response.status) };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'Network error' };
  }
}

export async function startRun(bidFileId: number): Promise<ApiResult<OptimizationRun>> {
  try {
    const response = await fetch(`${env.apiOrigin}${API_ENDPOINTS.optimizationRun}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bid_file_id: bidFileId }),
    });
    const body: unknown = await response.json();
    if (response.status === 201) {
      const parsed = optimizationRunSchema.safeParse(body);
      return parsed.success
        ? { ok: true, data: parsed.data }
        : { ok: false, error: 'Unexpected response shape' };
    }
    return { ok: false, error: extractError(body, response.status) };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'Network error' };
  }
}

function extractError(body: unknown, status: number): string {
  if (
    body &&
    typeof body === 'object' &&
    'error' in body &&
    body.error &&
    typeof body.error === 'object' &&
    'message' in body.error &&
    typeof body.error.message === 'string'
  ) {
    return body.error.message;
  }
  return `Request failed with status ${status}`;
}
