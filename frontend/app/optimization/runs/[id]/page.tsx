import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import { RunDetailView } from '@/features/optimization/run-detail-view';

export const metadata: Metadata = { title: 'Optimization run' };

export default async function OptimizationRunPage({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<React.JSX.Element> {
  const { id } = await params;
  const runId = Number(id);
  if (!Number.isInteger(runId) || runId <= 0) {
    notFound();
  }
  return <RunDetailView runId={runId} />;
}
