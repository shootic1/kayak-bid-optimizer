import type { Metadata } from 'next';

import { ComingSoon } from '@/components/shared/coming-soon';

export const metadata: Metadata = { title: 'Airports' };

export default function AirportsPage(): React.JSX.Element {
  return <ComingSoon title="Airports" />;
}
