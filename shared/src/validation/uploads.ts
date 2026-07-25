/**
 * Zod schemas for the upload API. The wire format mirrors the backend Pydantic
 * schemas exactly (snake_case).
 */

import { z } from 'zod';

export const fileTypeSchema = z.enum(['xlsx', 'csv', 'tsv']);

export const uploadStatusSchema = z.enum(['pending', 'processing', 'completed', 'failed']);

export const uploadValidationErrorSchema = z.object({
  row: z.number(),
  field: z.string(),
  message: z.string(),
});

const uploadBaseShape = {
  id: z.number(),
  original_filename: z.string(),
  file_type: fileTypeSchema,
  file_size: z.number(),
  checksum: z.string(),
  upload_status: uploadStatusSchema,
  report_type: z.string().nullable(),
  imported_rows: z.number(),
  skipped_rows: z.number(),
  error_count: z.number(),
  processing_ms: z.number().nullable(),
  uploaded_at: z.string(),
  processed_at: z.string().nullable(),
};

export const uploadListItemSchema = z.object(uploadBaseShape);

export const uploadDetailSchema = z.object({
  ...uploadBaseShape,
  error_message: z.string().nullable(),
  validation_errors: z.array(uploadValidationErrorSchema),
});

export const uploadListResponseSchema = z.object({
  items: z.array(uploadListItemSchema),
  total: z.number(),
  limit: z.number(),
  offset: z.number(),
});
