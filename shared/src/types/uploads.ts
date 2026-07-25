/** Upload contract types, derived from the Zod schemas (DRY). */

import type { z } from 'zod';

import type {
  fileTypeSchema,
  uploadDetailSchema,
  uploadListItemSchema,
  uploadListResponseSchema,
  uploadStatusSchema,
  uploadValidationErrorSchema,
} from '../validation/uploads';

export type FileType = z.infer<typeof fileTypeSchema>;
export type UploadStatus = z.infer<typeof uploadStatusSchema>;
export type UploadValidationError = z.infer<typeof uploadValidationErrorSchema>;
export type UploadListItem = z.infer<typeof uploadListItemSchema>;
export type UploadDetail = z.infer<typeof uploadDetailSchema>;
export type UploadListResponse = z.infer<typeof uploadListResponseSchema>;
