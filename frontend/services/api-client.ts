/**
 * Typed API client.
 *
 * A thin fetch wrapper that validates responses against the shared Zod schemas
 * and normalizes failures into a discriminated `ApiResult`, so callers never
 * deal with raw fetch errors or unvalidated JSON.
 */

import type { z } from 'zod';

import { env } from '@/lib/env';

export type ApiResult<T> =
  { readonly ok: true; readonly data: T } | { readonly ok: false; readonly error: string };

const DEFAULT_TIMEOUT_MS = 5000;

/**
 * Perform a GET request to `path` (an absolute API path such as
 * `/api/health`) and validate the JSON body with `schema`.
 */
export async function apiGet<TSchema extends z.ZodTypeAny>(
  path: string,
  schema: TSchema,
  init?: { readonly timeoutMs?: number; readonly signal?: AbortSignal },
): Promise<ApiResult<z.infer<TSchema>>> {
  const url = `${env.apiOrigin}${path}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), init?.timeoutMs ?? DEFAULT_TIMEOUT_MS);

  if (init?.signal) {
    init.signal.addEventListener('abort', () => controller.abort(), { once: true });
  }

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller.signal,
    });

    if (!response.ok) {
      return { ok: false, error: `Request failed with status ${response.status}` };
    }

    const json: unknown = await response.json();
    const parsed = schema.safeParse(json);
    if (!parsed.success) {
      return { ok: false, error: 'Unexpected response shape' };
    }
    return { ok: true, data: parsed.data as z.infer<TSchema> };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Network error';
    return { ok: false, error: message };
  } finally {
    clearTimeout(timeout);
  }
}
