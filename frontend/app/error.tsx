'use client';

import * as React from 'react';

import { AlertTriangle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { logger } from '@/lib/logger';

/** Route-segment error boundary. */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.JSX.Element {
  React.useEffect(() => {
    logger.error('Route error', error);
  }, [error]);

  return (
    <Card className="mx-auto mt-10 max-w-lg">
      <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
        <span className="bg-destructive/10 text-destructive flex size-12 items-center justify-center rounded-full">
          <AlertTriangle className="size-6" aria-hidden />
        </span>
        <div className="space-y-1">
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <p className="text-muted-foreground text-sm">
            An unexpected error occurred while rendering this page.
          </p>
        </div>
        <Button onClick={reset}>Try again</Button>
      </CardContent>
    </Card>
  );
}
