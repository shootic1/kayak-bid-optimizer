/**
 * Centralized, validated access to public environment variables.
 *
 * Components import from here rather than reading `process.env` directly, so
 * configuration has a single, typed entry point. Only `NEXT_PUBLIC_*` variables
 * are available in the browser.
 */

import { API_BASE_PATH } from '@kayak/shared';

const DEFAULT_ORIGIN = 'http://localhost:8000';

/**
 * Resolve the backend HTTP origin (scheme + host, no path).
 *
 * `NEXT_PUBLIC_API_URL` is documented as the API base including `/api`
 * (e.g. `http://localhost:8000/api`). We derive the bare origin so absolute
 * endpoint paths from `@kayak/shared` (e.g. `/api/health`, `/api/v1/version`)
 * can be appended without duplicating the `/api` segment.
 */
function readApiOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  const value = raw && raw.length > 0 ? raw : `${DEFAULT_ORIGIN}${API_BASE_PATH}`;
  return value
    .replace(/\/+$/, '') // strip trailing slashes
    .replace(new RegExp(`${API_BASE_PATH}$`), ''); // strip a trailing "/api"
}

export const env = {
  /** Backend origin, e.g. `http://localhost:8000`. */
  apiOrigin: readApiOrigin(),
  /** Active Node environment. */
  nodeEnv: process.env.NODE_ENV ?? 'development',
} as const;

export type Env = typeof env;
