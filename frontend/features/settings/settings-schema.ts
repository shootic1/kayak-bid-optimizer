import { z } from 'zod';

/**
 * Local UI preferences schema. Phase 1 persists only to the browser
 * (localStorage) — there is no backend settings store yet.
 */
export const settingsSchema = z.object({
  displayName: z
    .string()
    .trim()
    .min(2, 'Display name must be at least 2 characters.')
    .max(60, 'Display name must be at most 60 characters.'),
  rowsPerPage: z
    .number({ error: 'Enter a number between 10 and 100.' })
    .int('Must be a whole number.')
    .min(10, 'Minimum is 10.')
    .max(100, 'Maximum is 100.'),
  defaultCurrency: z.enum(['USD', 'EUR', 'GBP']),
});

export type SettingsFormValues = z.infer<typeof settingsSchema>;

export const DEFAULT_SETTINGS: SettingsFormValues = {
  displayName: 'Analyst',
  rowsPerPage: 25,
  defaultCurrency: 'USD',
};

export const SETTINGS_STORAGE_KEY = 'kayak.settings.v1';
