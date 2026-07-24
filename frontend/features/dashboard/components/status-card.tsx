import type * as React from 'react';

import type { ConnectionState } from '@kayak/shared';

import { StatusIndicator } from '@/components/shared/status-indicator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StatusCardProps {
  readonly title: string;
  readonly state: ConnectionState;
  readonly icon: React.ReactNode;
  readonly detail?: string;
}

/** A single system-dependency status card (e.g. Backend, Database). */
export function StatusCard({ title, state, icon, detail }: StatusCardProps): React.JSX.Element {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-muted-foreground text-sm font-medium">{title}</CardTitle>
        <span className="text-muted-foreground">{icon}</span>
      </CardHeader>
      <CardContent className="space-y-1">
        <StatusIndicator state={state} />
        {detail ? <p className="text-muted-foreground text-xs">{detail}</p> : null}
      </CardContent>
    </Card>
  );
}
