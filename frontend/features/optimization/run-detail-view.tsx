'use client';

import * as React from 'react';

import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

import type {
  ConfidenceLevel,
  MatchStatus,
  OptimizationRun,
  Recommendation,
  RecommendationAction,
  RecommendationDetail,
} from '@kayak/shared';

import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { MatchStatusBadge, RunStatusBadge } from '@/features/optimization/status-badges';
import { cn } from '@/lib/utils';
import { getRecommendation, getRun, listRecommendations } from '@/services/optimization-service';

const STATUS_OPTIONS: { value: MatchStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All statuses' },
  { value: 'matched', label: 'Matched' },
  { value: 'unmatched_no_history', label: 'Unmatched — no history' },
  { value: 'unmatched_non_iata', label: 'Unmatched — non-IATA' },
  { value: 'skipped_excluded', label: 'Skipped — excluded' },
];

const CONFIDENCE_OPTIONS = [
  { value: '', label: 'Any confidence' },
  { value: '0.5', label: 'Medium & up' },
  { value: '0.8', label: 'High only' },
];

const selectClass =
  'h-9 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring';

const ACTION_LABELS: Record<RecommendationAction, string> = {
  keep: 'Keep',
  increase: 'Increase',
  manual_review: 'Manual review',
  insufficient_data: 'Insufficient data',
};

const ACTION_CLASSES: Record<RecommendationAction, string> = {
  keep: 'bg-muted text-muted-foreground',
  increase: 'bg-success/15 text-success',
  manual_review: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  insufficient_data: 'bg-muted text-muted-foreground',
};

const CONFIDENCE_LABELS: Record<ConfidenceLevel, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
};

function ActionBadge({ action }: { action: RecommendationAction }): React.JSX.Element {
  return (
    <span
      className={cn(
        'inline-block rounded-full px-2 py-0.5 text-xs font-medium',
        ACTION_CLASSES[action],
      )}
    >
      {ACTION_LABELS[action]}
    </span>
  );
}

function Stat({ label, value }: { label: string; value: string | number }): React.JSX.Element {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}

function fmt(value: number | null): string {
  return value === null ? '—' : value.toFixed(2);
}

function DetailField({ label, value }: { label: string; value: string }): React.JSX.Element {
  return (
    <div>
      <dt className="text-muted-foreground text-xs">{label}</dt>
      <dd className="tabular-nums">{value}</dd>
    </div>
  );
}

export function RunDetailView({ runId }: { runId: number }): React.JSX.Element {
  const [run, setRun] = React.useState<OptimizationRun | null>(null);
  const [items, setItems] = React.useState<Recommendation[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [status, setStatus] = React.useState<MatchStatus | 'all'>('all');
  const [minConfidence, setMinConfidence] = React.useState('');
  const [selected, setSelected] = React.useState<RecommendationDetail | null>(null);

  React.useEffect(() => {
    const controller = new AbortController();
    void getRun(runId, controller.signal).then((r) => {
      if (r.ok) setRun(r.data);
    });
    return () => controller.abort();
  }, [runId]);

  React.useEffect(() => {
    const controller = new AbortController();
    void (async () => {
      setLoading(true);
      const result = await listRecommendations(
        {
          runId,
          status: status === 'all' ? undefined : status,
          minConfidence: minConfidence ? Number(minConfidence) : undefined,
          limit: 200,
        },
        controller.signal,
      );
      if (controller.signal.aborted) return;
      if (result.ok) {
        setItems(result.data.items);
        setTotal(result.data.total);
      }
      setLoading(false);
    })();
    return () => controller.abort();
  }, [runId, status, minConfidence]);

  const onSelect = async (id: number): Promise<void> => {
    if (selected?.id === id) {
      setSelected(null);
      return;
    }
    const result = await getRecommendation(id);
    if (result.ok) setSelected(result.data);
  };

  return (
    <div>
      <div className="mb-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/optimization">
            <ArrowLeft className="size-4" aria-hidden />
            Back to optimization
          </Link>
        </Button>
      </div>

      <div className="mb-6 flex items-center gap-3">
        <PageHeader title={`Optimization run #${runId}`} />
        {run ? <RunStatusBadge status={run.status} /> : null}
      </div>

      {/* Status summary */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <Stat label="Total routes" value={run?.total_routes ?? '—'} />
        <Stat label="Matched" value={run?.matched_count ?? '—'} />
        <Stat label="Unmatched" value={run?.unmatched_count ?? '—'} />
        <Stat label="Skipped" value={run?.skipped_count ?? '—'} />
        <Stat label="Recommendations" value={run?.recommendation_count ?? '—'} />
      </div>

      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="text-base">Recommendations ({total})</CardTitle>
          <div className="flex flex-wrap gap-2">
            <select
              className={selectClass}
              value={status}
              onChange={(e) => setStatus(e.target.value as MatchStatus | 'all')}
            >
              {STATUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
            <select
              className={selectClass}
              value={minConfidence}
              onChange={(e) => setMinConfidence(e.target.value)}
            >
              {CONFIDENCE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-9 w-full" />
              <Skeleton className="h-9 w-full" />
              <Skeleton className="h-9 w-full" />
            </div>
          ) : items.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center text-sm">
              No recommendations match these filters.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[680px] text-sm">
                <thead className="text-muted-foreground border-b">
                  <tr className="[&>th]:px-2 [&>th]:py-2 [&>th]:text-left [&>th]:font-medium">
                    <th>Route</th>
                    <th>Status</th>
                    <th>Action</th>
                    <th className="text-right">Current</th>
                    <th className="text-right">Recommended</th>
                    <th className="text-right">Δ</th>
                    <th className="text-right">%</th>
                    <th className="text-right">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((r) => (
                    <React.Fragment key={r.id}>
                      <tr
                        onClick={() => void onSelect(r.id)}
                        className={cn(
                          'hover:bg-muted/50 cursor-pointer border-b [&>td]:px-2 [&>td]:py-2',
                          selected?.id === r.id && 'bg-muted/50',
                        )}
                      >
                        <td className="font-medium">
                          {r.origin} → {r.destination}
                        </td>
                        <td>
                          <MatchStatusBadge status={r.match_status} />
                        </td>
                        <td>
                          <ActionBadge action={r.action} />
                        </td>
                        <td className="text-right tabular-nums">{fmt(r.current_bid)}</td>
                        <td className="text-right tabular-nums">{fmt(r.recommended_bid)}</td>
                        <td
                          className={cn(
                            'text-right tabular-nums',
                            r.difference !== null && r.difference > 0 && 'text-success',
                            r.difference !== null && r.difference < 0 && 'text-destructive',
                          )}
                        >
                          {r.difference === null ? '—' : r.difference.toFixed(2)}
                        </td>
                        <td className="text-right tabular-nums">
                          {r.pct_change === null ? '—' : `${(r.pct_change * 100).toFixed(1)}%`}
                        </td>
                        <td className="text-right tabular-nums">
                          {r.confidence_level === null
                            ? '—'
                            : CONFIDENCE_LABELS[r.confidence_level]}
                        </td>
                      </tr>
                      {selected?.id === r.id ? (
                        <tr className="bg-muted/30">
                          <td colSpan={8} className="px-3 py-3">
                            <div className="mb-3 flex flex-wrap items-center gap-2">
                              <ActionBadge action={selected.action} />
                              {selected.rule_triggered ? (
                                <span className="text-muted-foreground text-xs">
                                  Rule:{' '}
                                  <span className="font-medium">{selected.rule_triggered}</span>
                                </span>
                              ) : null}
                              {selected.manual_review ? (
                                <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-medium text-amber-600 dark:text-amber-400">
                                  Needs manual review
                                </span>
                              ) : null}
                            </div>
                            <p className="mb-3 text-sm">{selected.reason}</p>
                            <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
                              <DetailField
                                label="Device"
                                value={selected.device ? selected.device : '—'}
                              />
                              <DetailField
                                label="Position"
                                value={fmt(selected.current_position)}
                              />
                              <DetailField
                                label="CTR"
                                value={
                                  selected.ctr === null
                                    ? '—'
                                    : `${(selected.ctr * 100).toFixed(2)}%`
                                }
                              />
                              <DetailField
                                label="Confidence"
                                value={
                                  selected.confidence_level === null
                                    ? '—'
                                    : CONFIDENCE_LABELS[selected.confidence_level]
                                }
                              />
                              <DetailField
                                label="Clicks"
                                value={selected.clicks === null ? '—' : String(selected.clicks)}
                              />
                              <DetailField
                                label="Impressions"
                                value={
                                  selected.impressions === null ? '—' : String(selected.impressions)
                                }
                              />
                              <DetailField label="Spend" value={fmt(selected.spend)} />
                            </dl>
                          </td>
                        </tr>
                      ) : null}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
