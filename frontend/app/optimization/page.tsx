import type { Metadata } from 'next';

import { OptimizationView } from '@/features/optimization/optimization-view';

export const metadata: Metadata = { title: 'Optimization' };

export default function OptimizationPage(): React.JSX.Element {
  return <OptimizationView />;
}
