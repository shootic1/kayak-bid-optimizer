import type * as React from 'react';

import { Skeleton } from '@/components/ui/skeleton';

/** Route-level loading fallback (Suspense boundary). */
export default function Loading(): React.JSX.Element {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
      </div>
      <Skeleton className="h-64 w-full" />
    </div>
  );
}
