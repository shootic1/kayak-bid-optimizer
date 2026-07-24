import type * as React from 'react';

import { APP_NAME, APP_VERSION, type VersionResponse } from '@kayak/shared';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { env } from '@/lib/env';

interface ProjectInfoPanelProps {
  readonly version: VersionResponse | null;
}

interface InfoRow {
  readonly label: string;
  readonly value: string;
}

/** Static project/system information — real values only, no analytics. */
export function ProjectInfoPanel({ version }: ProjectInfoPanelProps): React.JSX.Element {
  const rows: readonly InfoRow[] = [
    { label: 'Application', value: APP_NAME },
    { label: 'Frontend version', value: `v${APP_VERSION}` },
    { label: 'Backend version', value: version ? `v${version.version}` : '—' },
    { label: 'Environment', value: version?.environment ?? env.nodeEnv },
    { label: 'Phase', value: 'Phase 1 — Project Foundation' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Project information</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="divide-y">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between py-2.5 text-sm">
              <dt className="text-muted-foreground">{row.label}</dt>
              <dd className="font-medium">{row.value}</dd>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
}
