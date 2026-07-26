'use client';

import * as React from 'react';

import { AlertCircle, Download, FileSpreadsheet, Loader2, RefreshCw } from 'lucide-react';

import type { ExportSummary, OptimizationRun } from '@kayak/shared';

import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { RunStatusBadge } from '@/features/optimization/status-badges';
import { formatDateTime } from '@/lib/format';
import { cn } from '@/lib/utils';
import {
  downloadExportWorkbook,
  getExportSummary,
  listRuns,
} from '@/services/optimization-service';

interface ExportState {
  readonly loading: boolean;
  readonly error: string | null;
  readonly summary: ExportSummary | null;
}

const IDLE: ExportState = { loading: false, error: null, summary: null };

function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function formatDelta(value: number): string {
  if (value === 0) return '$0.00';
  const sign = value > 0 ? '+' : '−';
  return `${sign}$${Math.abs(value).toFixed(2)}`;
}

function Stat({
  label,
  value,
  emphasis = false,
}: {
  label: string;
  value: string | number;
  emphasis?: boolean;
}): React.JSX.Element {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className={cn('text-lg font-semibold tabular-nums', emphasis && 'text-success')}>
        {value}
      </p>
    </div>
  );
}

function ExportSummaryPanel({ summary }: { summary: ExportSummary }): React.JSX.Element {
  return (
    <div className="mt-4 border-t pt-4">
      <div className="mb-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
        <FileSpreadsheet className="text-muted-foreground size-4 shrink-0" aria-hidden />
        <span className="font-medium break-all">{summary.output_filename}</span>
        <span className="text-muted-foreground text-xs">· {formatDateTime(summary.timestamp)}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <Stat label="Routes processed" value={summary.routes_processed} />
        <Stat
          label="Routes updated"
          value={summary.routes_updated}
          emphasis={summary.routes_updated > 0}
        />
        <Stat label="Routes unchanged" value={summary.routes_unchanged} />
        <Stat label="Manual review" value={summary.manual_review_count} />
        <Stat label="Insufficient data" value={summary.insufficient_data_count} />
        <Stat label="Avg bid increase" value={formatDelta(summary.average_bid_increase)} />
        <Stat label="Max bid increase" value={formatDelta(summary.maximum_bid_increase)} />
      </div>
      <p className="text-muted-foreground mt-3 text-xs">
        Strategy version: <span className="font-medium">{summary.strategy_version}</span>
      </p>
      {summary.skipped_routes.length > 0 ? (
        <p className="text-warning mt-2 text-xs">
          {summary.skipped_routes.length} route(s) skipped:{' '}
          {summary.skipped_routes.map((r) => `${r.origin}→${r.destination}`).join(', ')}
        </p>
      ) : null}
    </div>
  );
}

export function ExportsView(): React.JSX.Element {
  const [runs, setRuns] = React.useState<OptimizationRun[] | null>(null);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [exportState, setExportState] = React.useState<Record<number, ExportState>>({});
  const [nonce, setNonce] = React.useState(0);

  const refresh = React.useCallback(() => {
    setRuns(null);
    setLoadError(null);
    setNonce((n) => n + 1);
  }, []);

  React.useEffect(() => {
    const controller = new AbortController();
    void (async () => {
      const result = await listRuns(controller.signal);
      if (controller.signal.aborted) return;
      if (result.ok) {
        setRuns(result.data.items.filter((r) => r.status === 'completed'));
      } else {
        setRuns([]);
        setLoadError(result.error);
      }
    })();
    return () => controller.abort();
  }, [nonce]);

  const onExport = async (runId: number): Promise<void> => {
    setExportState((prev) => ({
      ...prev,
      [runId]: { loading: true, error: null, summary: prev[runId]?.summary ?? null },
    }));
    const [summaryResult, fileResult] = await Promise.all([
      getExportSummary(runId),
      downloadExportWorkbook(runId),
    ]);
    if (!summaryResult.ok) {
      setExportState((prev) => ({
        ...prev,
        [runId]: { loading: false, error: summaryResult.error, summary: null },
      }));
      return;
    }
    if (!fileResult.ok) {
      setExportState((prev) => ({
        ...prev,
        [runId]: { loading: false, error: fileResult.error, summary: summaryResult.data },
      }));
      return;
    }
    // Prefer the summary's filename: it is readable cross-origin, whereas the
    // Content-Disposition header is not exposed to the browser by default.
    const filename = summaryResult.data.output_filename || fileResult.data.filename;
    triggerBrowserDownload(fileResult.data.blob, filename);
    setExportState((prev) => ({
      ...prev,
      [runId]: { loading: false, error: null, summary: summaryResult.data },
    }));
  };

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <PageHeader
          title="Exports"
          description="Generate KAYAK upload workbooks from completed optimization runs. Only the Override CPC of increased routes is changed; everything else is preserved."
        />
        <Button variant="outline" size="sm" onClick={refresh}>
          <RefreshCw className="size-4" aria-hidden />
          Refresh
        </Button>
      </div>

      {loadError ? (
        <div className="text-destructive mb-4 flex items-center gap-2 text-sm">
          <AlertCircle className="size-4" aria-hidden />
          {loadError}
        </div>
      ) : null}

      {runs === null ? (
        <div className="space-y-3">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      ) : runs.length === 0 ? (
        <Card>
          <CardContent className="text-muted-foreground p-10 text-center text-sm">
            No completed optimization runs yet. Run an optimization first, then return here to
            export the optimized workbook.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {runs.map((run) => {
            const state = exportState[run.id] ?? IDLE;
            return (
              <Card key={run.id}>
                <CardContent className="p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Run #{run.id}</span>
                        <RunStatusBadge status={run.status} />
                      </div>
                      <p className="text-muted-foreground mt-0.5 text-xs">
                        {run.recommendation_count} recommendations · {run.matched_count}/
                        {run.total_routes} matched ·{' '}
                        {formatDateTime(run.finished_at ?? run.started_at)}
                      </p>
                    </div>
                    <Button onClick={() => void onExport(run.id)} disabled={state.loading}>
                      {state.loading ? (
                        <Loader2 className="size-4 animate-spin" aria-hidden />
                      ) : (
                        <Download className="size-4" aria-hidden />
                      )}
                      Export Optimized Workbook
                    </Button>
                  </div>

                  {state.error ? (
                    <div className="text-destructive mt-3 flex items-center gap-2 text-sm">
                      <AlertCircle className="size-4 shrink-0" aria-hidden />
                      {state.error}
                    </div>
                  ) : null}

                  {state.summary ? <ExportSummaryPanel summary={state.summary} /> : null}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
