import type * as React from 'react';

import Link from 'next/link';

import { APP_ROUTES } from '@kayak/shared';

import { Button } from '@/components/ui/button';

/** 404 page. */
export default function NotFound(): React.JSX.Element {
  return (
    <div className="flex min-h-[60svh] flex-col items-center justify-center gap-4 text-center">
      <p className="text-muted-foreground text-5xl font-bold">404</p>
      <div className="space-y-1">
        <h1 className="text-xl font-semibold">Page not found</h1>
        <p className="text-muted-foreground text-sm">
          The page you are looking for does not exist or has moved.
        </p>
      </div>
      <Button asChild>
        <Link href={APP_ROUTES.dashboard}>Back to dashboard</Link>
      </Button>
    </div>
  );
}
