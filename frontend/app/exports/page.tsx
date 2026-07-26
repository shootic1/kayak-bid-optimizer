import type { Metadata } from 'next';

import { ExportsView } from '@/features/optimization/exports-view';

export const metadata: Metadata = { title: 'Exports' };

export default function ExportsPage(): React.JSX.Element {
  return <ExportsView />;
}
