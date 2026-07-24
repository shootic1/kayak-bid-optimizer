import type { Metadata } from 'next';

import { PageHeader } from '@/components/shared/page-header';
import { SettingsForm } from '@/features/settings/settings-form';

export const metadata: Metadata = { title: 'Settings' };

export default function SettingsPage(): React.JSX.Element {
  return (
    <div>
      <PageHeader title="Settings" description="Manage your local application preferences." />
      <SettingsForm />
    </div>
  );
}
