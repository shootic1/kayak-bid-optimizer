import type { Metadata } from 'next';

import { ComingSoon } from '@/components/shared/coming-soon';

export const metadata: Metadata = { title: 'Optimization' };

export default function OptimizationPage(): React.JSX.Element {
  return <ComingSoon title="Optimization" />;
}
