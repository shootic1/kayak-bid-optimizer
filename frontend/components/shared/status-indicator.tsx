import type * as React from 'react';

import type { ConnectionState } from '@kayak/shared';

import { cn } from '@/lib/utils';

const STATE_STYLES: Record<ConnectionState, { dot: string; label: string }> = {
  online: { dot: 'bg-success', label: 'Online' },
  offline: { dot: 'bg-destructive', label: 'Offline' },
  loading: { dot: 'bg-muted-foreground animate-pulse', label: 'Checking…' },
};

interface StatusIndicatorProps {
  readonly state: ConnectionState;
  readonly label?: string;
}

/** A colored dot + text label representing a dependency's connection state. */
export function StatusIndicator({ state, label }: StatusIndicatorProps): React.JSX.Element {
  const style = STATE_STYLES[state];
  return (
    <span className="inline-flex items-center gap-2">
      <span className={cn('size-2.5 rounded-full', style.dot)} aria-hidden />
      <span className="text-sm font-medium">{label ?? style.label}</span>
    </span>
  );
}
