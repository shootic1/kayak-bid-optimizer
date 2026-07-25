import type * as React from 'react';

import type { UploadStatus } from '@kayak/shared';

import { Badge } from '@/components/ui/badge';

const STATUS_VARIANT: Record<
  UploadStatus,
  { variant: 'success' | 'warning' | 'destructive' | 'secondary'; label: string }
> = {
  completed: { variant: 'success', label: 'Completed' },
  processing: { variant: 'warning', label: 'Processing' },
  pending: { variant: 'secondary', label: 'Pending' },
  failed: { variant: 'destructive', label: 'Failed' },
};

export function UploadStatusBadge({ status }: { status: UploadStatus }): React.JSX.Element {
  const { variant, label } = STATUS_VARIANT[status];
  return <Badge variant={variant}>{label}</Badge>;
}
