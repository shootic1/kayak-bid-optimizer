/**
 * Uploads API service.
 *
 * List/get/delete reuse the typed `apiGet`; the create endpoint uses
 * XMLHttpRequest so the UI can report real upload progress (fetch cannot).
 */

import {
  API_ENDPOINTS,
  type UploadDetail,
  uploadDetailSchema,
  type UploadListResponse,
  uploadListResponseSchema,
  uploadPath,
} from '@kayak/shared';

import { env } from '@/lib/env';
import { apiGet, type ApiResult } from '@/services/api-client';

export function listUploads(
  params: { limit?: number; offset?: number } = {},
  signal?: AbortSignal,
): Promise<ApiResult<UploadListResponse>> {
  const query = new URLSearchParams({
    limit: String(params.limit ?? 50),
    offset: String(params.offset ?? 0),
  });
  return apiGet(`${API_ENDPOINTS.uploads}?${query.toString()}`, uploadListResponseSchema, {
    signal,
  });
}

export function getUpload(id: number, signal?: AbortSignal): Promise<ApiResult<UploadDetail>> {
  return apiGet(uploadPath(id), uploadDetailSchema, { signal });
}

export async function deleteUpload(id: number): Promise<ApiResult<null>> {
  try {
    const response = await fetch(`${env.apiOrigin}${uploadPath(id)}`, { method: 'DELETE' });
    if (!response.ok && response.status !== 204) {
      return { ok: false, error: `Delete failed with status ${response.status}` };
    }
    return { ok: true, data: null };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'Network error' };
  }
}

export interface UploadProgress {
  readonly loaded: number;
  readonly total: number;
  readonly percent: number;
}

/**
 * Upload a file, reporting progress. Resolves with the parsed {@link UploadDetail}
 * (which includes the import outcome) or an error message.
 */
export function uploadFile(
  file: File,
  onProgress?: (progress: UploadProgress) => void,
): Promise<ApiResult<UploadDetail>> {
  return new Promise((resolve) => {
    const form = new FormData();
    form.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${env.apiOrigin}${API_ENDPOINTS.uploads}`);
    xhr.responseType = 'json';

    xhr.upload.onprogress = (event) => {
      if (onProgress && event.lengthComputable) {
        onProgress({
          loaded: event.loaded,
          total: event.total,
          percent: Math.round((event.loaded / event.total) * 100),
        });
      }
    };

    xhr.onload = () => {
      const body: unknown = xhr.response;
      if (xhr.status === 201) {
        const parsed = uploadDetailSchema.safeParse(body);
        resolve(
          parsed.success
            ? { ok: true, data: parsed.data }
            : { ok: false, error: 'Unexpected response shape' },
        );
        return;
      }
      resolve({ ok: false, error: extractError(body, xhr.status) });
    };

    xhr.onerror = () => resolve({ ok: false, error: 'Network error during upload' });
    xhr.send(form);
  });
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
  return `Upload failed with status ${status}`;
}
