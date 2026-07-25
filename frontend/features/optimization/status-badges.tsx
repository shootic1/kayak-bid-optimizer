import type * as React from 'react';

import type { MatchStatus, RunStatus } from '@kayak/shared';

import { Badge } from '@/components/ui/badge';

type Variant = 'success' | 'warning' | 'destructive' | 'secondary' | 'outline';

const MATCH: Record<MatchStatus, { variant: Variant; label: string }> = {
  matched: { variant: 'success', label: 'Matched' },
  unmatched_no_history: { variant: 'warning', label: 'No history' },
  unmatched_non_iata: { variant: 'secondary', label: 'Non-IATA' },
  skipped_excluded: { variant: 'outline', label: 'Excluded' },
};

const RUN: Record<RunStatus, { variant: Variant; label: string }> = {
  completed: { variant: 'success', label: 'Completed' },
  running: { variant: 'warning', label: 'Running' },
  pending: { variant: 'secondary', label: 'Pending' },
  failed: { variant: 'destructive', label: 'Failed' },
};

export function MatchStatusBadge({ status }: { status: MatchStatus }): React.JSX.Element {
  const { variant, label } = MATCH[status];
  return <Badge variant={variant}>{label}</Badge>;
}

export function RunStatusBadge({ status }: { status: RunStatus }): React.JSX.Element {
  const { variant, label } = RUN[status];
  return <Badge variant={variant}>{label}</Badge>;
}
