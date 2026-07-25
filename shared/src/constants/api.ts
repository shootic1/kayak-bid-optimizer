/**
 * API path constants.
 *
 * Infrastructure endpoints (`/api/health`, `/api/health/ready`) are UNVERSIONED
 * and stable across API versions. Application endpoints live under the versioned
 * `/api/v1` namespace. See ADR-0004.
 */

export const API_BASE_PATH = '/api' as const;
export const API_V1_PATH = '/api/v1' as const;

/** Endpoint paths relative to the API host origin. */
export const API_ENDPOINTS = {
  /** Unversioned liveness probe. */
  health: `${API_BASE_PATH}/health`,
  /** Unversioned readiness probe (includes database check). */
  ready: `${API_BASE_PATH}/health/ready`,
  /** Versioned application version/metadata. */
  version: `${API_V1_PATH}/version`,
  /** Uploads collection (POST to create, GET to list). */
  uploads: `${API_V1_PATH}/uploads`,
} as const;

/** Build the URL path for a single upload. */
export function uploadPath(id: number): string {
  return `${API_V1_PATH}/uploads/${id}`;
}

export type ApiEndpoint = (typeof API_ENDPOINTS)[keyof typeof API_ENDPOINTS];
