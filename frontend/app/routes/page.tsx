import type { Metadata } from 'next';

import { ComingSoon } from '@/components/shared/coming-soon';

export const metadata: Metadata = { title: 'Routes' };

export default function RoutesPage(): React.JSX.Element {
  return <ComingSoon title="Routes" />;
}
