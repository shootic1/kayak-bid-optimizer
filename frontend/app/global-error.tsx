'use client';

import * as React from 'react';

import { logger } from '@/lib/logger';

import '@/styles/globals.css';

/** Root error boundary — replaces the whole document when the root layout throws. */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.JSX.Element {
  React.useEffect(() => {
    logger.error('Global error', error);
  }, [error]);

  return (
    <html lang="en">
      <body className="bg-background text-foreground min-h-svh antialiased">
        <div className="flex min-h-svh flex-col items-center justify-center gap-4 px-6 text-center">
          <h1 className="text-2xl font-semibold">Application error</h1>
          <p className="text-muted-foreground max-w-md text-sm">
            A critical error occurred. Please try reloading the application.
          </p>
          <button
            type="button"
            onClick={reset}
            className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium"
          >
            Reload
          </button>
        </div>
      </body>
    </html>
  );
}
