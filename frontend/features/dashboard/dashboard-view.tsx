'use client';

import type * as React from 'react';

import { Database, RefreshCw, Server } from 'lucide-react';

import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { StatusCard } from '@/features/dashboard/components/status-card';
import { ProjectInfoPanel } from '@/features/dashboard/components/project-info-panel';
import { useSystemStatus } from '@/features/system-status/use-system-status';

/** Dashboard: live system status + project information (no mock analytics). */
export function DashboardView(): React.JSX.Element {
  const { status, refresh } = useSystemStatus();

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <PageHeader
          title="Dashboard"
          description="System overview and connectivity for KAYAK Bid Optimizer Pro."
        />
        <Button variant="outline" size="sm" onClick={refresh}>
          <RefreshCw className="size-4" aria-hidden />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <StatusCard
          title="Backend API"
          state={status.backend}
          icon={<Server className="size-4" aria-hidden />}
          detail="FastAPI service — /api/health"
        />
        <StatusCard
          title="Database"
          state={status.database}
          icon={<Database className="size-4" aria-hidden />}
          detail="PostgreSQL — readiness probe"
        />
      </div>

      <div className="mt-4">
        <ProjectInfoPanel version={status.version} />
      </div>
    </div>
  );
}
