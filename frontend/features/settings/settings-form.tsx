'use client';

import * as React from 'react';

import { zodResolver } from '@hookform/resolvers/zod';
import { Check } from 'lucide-react';
import { useForm } from 'react-hook-form';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { logger } from '@/lib/logger';
import { cn } from '@/lib/utils';
import {
  DEFAULT_SETTINGS,
  SETTINGS_STORAGE_KEY,
  type SettingsFormValues,
  settingsSchema,
} from '@/features/settings/settings-schema';

function loadSettings(): SettingsFormValues {
  if (typeof window === 'undefined') {
    return DEFAULT_SETTINGS;
  }
  try {
    const raw = window.localStorage.getItem(SETTINGS_STORAGE_KEY);
    if (!raw) {
      return DEFAULT_SETTINGS;
    }
    const parsed = settingsSchema.safeParse(JSON.parse(raw));
    return parsed.success ? parsed.data : DEFAULT_SETTINGS;
  } catch (error) {
    logger.warn('Failed to load settings from storage', error);
    return DEFAULT_SETTINGS;
  }
}

const inputClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

/** Local preferences form demonstrating the React Hook Form + Zod pattern. */
export function SettingsForm(): React.JSX.Element {
  const [saved, setSaved] = React.useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: DEFAULT_SETTINGS,
  });

  React.useEffect(() => {
    reset(loadSettings());
  }, [reset]);

  const onSubmit = handleSubmit((values) => {
    window.localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(values));
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  });

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>Preferences</CardTitle>
        <CardDescription>
          Local display preferences, stored in your browser. No data leaves your device.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-5" noValidate>
          <div className="space-y-1.5">
            <label htmlFor="displayName" className="text-sm font-medium">
              Display name
            </label>
            <input id="displayName" className={inputClass} {...register('displayName')} />
            {errors.displayName ? (
              <p className="text-destructive text-xs">{errors.displayName.message}</p>
            ) : null}
          </div>

          <div className="space-y-1.5">
            <label htmlFor="rowsPerPage" className="text-sm font-medium">
              Rows per page
            </label>
            <input
              id="rowsPerPage"
              type="number"
              className={inputClass}
              {...register('rowsPerPage', { valueAsNumber: true })}
            />
            {errors.rowsPerPage ? (
              <p className="text-destructive text-xs">{errors.rowsPerPage.message}</p>
            ) : null}
          </div>

          <div className="space-y-1.5">
            <label htmlFor="defaultCurrency" className="text-sm font-medium">
              Default currency
            </label>
            <select
              id="defaultCurrency"
              className={cn(inputClass, 'cursor-pointer')}
              {...register('defaultCurrency')}
            >
              <option value="USD">USD — US Dollar</option>
              <option value="EUR">EUR — Euro</option>
              <option value="GBP">GBP — British Pound</option>
            </select>
            {errors.defaultCurrency ? (
              <p className="text-destructive text-xs">{errors.defaultCurrency.message}</p>
            ) : null}
          </div>

          <div className="flex items-center gap-3">
            <Button type="submit" disabled={isSubmitting}>
              Save preferences
            </Button>
            {saved ? (
              <span className="text-success inline-flex items-center gap-1 text-sm">
                <Check className="size-4" aria-hidden />
                Saved
              </span>
            ) : null}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
