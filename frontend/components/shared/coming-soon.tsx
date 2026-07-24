import type * as React from 'react';

import { Construction } from 'lucide-react';

import { PageHeader } from '@/components/shared/page-header';
import { Card, CardContent } from '@/components/ui/card';

interface ComingSoonProps {
  readonly title: string;
}

/** Placeholder shown for routes reserved for future phases. */
export function ComingSoon({ title }: ComingSoonProps): React.JSX.Element {
  return (
    <div>
      <PageHeader title={title} />
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <span className="bg-muted text-muted-foreground flex size-12 items-center justify-center rounded-full">
            <Construction className="size-6" aria-hidden />
          </span>
          <p className="text-base font-medium">Coming in future phases.</p>
          <p className="text-muted-foreground max-w-sm text-sm">
            This section is reserved and will be delivered in a later phase of KAYAK Bid Optimizer
            Pro.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
