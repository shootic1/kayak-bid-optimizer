'use client';

import * as React from 'react';

import { Play, RefreshCw, Upload } from 'lucide-react';
import Link from 'next/link';

import type { BidFile, OptimizationRun } from '@kayak/shared';

import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RunStatusBadge } from '@/features/optimization/status-badges';
import { formatBytes, formatDateTime } from '@/lib/format';
import { listBidFiles, listRuns, startRun, uploadBidFile } from '@/services/optimization-service';

export function OptimizationView(): React.JSX.Element {
  const [bidFiles, setBidFiles] = React.useState<BidFile[]>([]);
  const [runs, setRuns] = React.useState<OptimizationRun[]>([]);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [nonce, setNonce] = React.useState(0);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const refresh = React.useCallback(() => setNonce((n) => n + 1), []);

  React.useEffect(() => {
    const controller = new AbortController();
    void (async () => {
      const [files, runList] = await Promise.all([
        listBidFiles(controller.signal),
        listRuns(controller.signal),
      ]);
      if (controller.signal.aborted) return;
      if (files.ok) setBidFiles(files.data.items);
      if (runList.ok) setRuns(runList.data.items);
    })();
    return () => controller.abort();
  }, [nonce]);

  const onUpload = async (file: File): Promise<void> => {
    setError(null);
    setBusy(true);
    const result = await uploadBidFile(file);
    setBusy(false);
    if (result.ok) refresh();
    else setError(result.error);
  };

  const onRun = async (bidFileId: number): Promise<void> => {
    setError(null);
    setBusy(true);
    const result = await startRun(bidFileId);
    setBusy(false);
    if (result.ok) refresh();
    else setError(result.error);
  };

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <PageHeader
          title="Optimization"
          description="Upload KAYAK bid files, match routes to history, and generate recommendations."
        />
        <Button variant="outline" size="sm" onClick={refresh}>
          <RefreshCw className="size-4" aria-hidden />
          Refresh
        </Button>
      </div>

      {error ? <p className="text-destructive mb-4 text-sm">{error}</p> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Bid files</CardTitle>
            <Button
              size="sm"
              variant="outline"
              disabled={busy}
              onClick={() => inputRef.current?.click()}
            >
              <Upload className="size-4" aria-hidden />
              Upload .xlsx
            </Button>
            <input
              ref={inputRef}
              type="file"
              accept=".xlsx"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void onUpload(file);
                e.target.value = '';
              }}
            />
          </CardHeader>
          <CardContent>
            {bidFiles.length === 0 ? (
              <p className="text-muted-foreground py-6 text-center text-sm">No bid files yet.</p>
            ) : (
              <ul className="divide-y">
                {bidFiles.map((f) => (
                  <li key={f.id} className="flex items-center justify-between gap-3 py-2.5">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{f.provider_code}</p>
                      <p className="text-muted-foreground text-xs">
                        {f.route_count} routes · {formatBytes(f.file_size)} · {f.mode}
                      </p>
                    </div>
                    <Button size="sm" disabled={busy} onClick={() => void onRun(f.id)}>
                      <Play className="size-4" aria-hidden />
                      Run
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Optimization runs</CardTitle>
          </CardHeader>
          <CardContent>
            {runs.length === 0 ? (
              <p className="text-muted-foreground py-6 text-center text-sm">No runs yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[420px] text-sm">
                  <thead className="text-muted-foreground border-b">
                    <tr className="[&>th]:px-2 [&>th]:py-2 [&>th]:text-left [&>th]:font-medium">
                      <th>Run</th>
                      <th>Status</th>
                      <th className="text-right">Matched</th>
                      <th className="text-right">Recs</th>
                      <th>Started</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((r) => (
                      <tr key={r.id} className="hover:bg-muted/50 border-b [&>td]:px-2 [&>td]:py-2">
                        <td>
                          <Link
                            href={`/optimization/runs/${r.id}`}
                            className="font-medium underline-offset-2 hover:underline"
                          >
                            #{r.id}
                          </Link>
                        </td>
                        <td>
                          <RunStatusBadge status={r.status} />
                        </td>
                        <td className="text-right tabular-nums">
                          {r.matched_count}/{r.total_routes}
                        </td>
                        <td className="text-right tabular-nums">{r.recommendation_count}</td>
                        <td className="text-muted-foreground whitespace-nowrap">
                          {formatDateTime(r.started_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
