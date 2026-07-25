import type { Metadata } from 'next';

import { UploadsView } from '@/features/uploads/uploads-view';

export const metadata: Metadata = { title: 'Uploads' };

export default function UploadsPage(): React.JSX.Element {
  return <UploadsView />;
}
