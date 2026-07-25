'use client';

import * as React from 'react';

import { RefreshCw } from 'lucide-react';

import type { UploadDetail } from '@kayak/shared';

import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';
import { ImportSummary } from '@/features/uploads/import-summary';
import { UploadDropzone } from '@/features/uploads/upload-dropzone';
import { UploadHistoryTable } from '@/features/uploads/upload-history-table';
import { useUploads } from '@/features/uploads/use-uploads';
import { getUpload } from '@/services/uploads-service';

export function UploadsView(): React.JSX.Element {
  const { state, refresh, remove } = useUploads();
  const [selected, setSelected] = React.useState<UploadDetail | null>(null);

  const handleUploaded = React.useCallback(
    (upload: UploadDetail) => {
      setSelected(upload);
      refresh();
    },
    [refresh],
  );

  const handleSelect = React.useCallback(async (id: number) => {
    const result = await getUpload(id);
    if (result.ok) setSelected(result.data);
  }, []);

  const handleDelete = React.useCallback(
    async (id: number) => {
      await remove(id);
      setSelected((current) => (current?.id === id ? null : current));
    },
    [remove],
  );

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-4">
        <PageHeader
          title="Uploads"
          description="Import KAYAK Inline and Dynamic Inline performance reports."
        />
        <Button variant="outline" size="sm" onClick={refresh}>
          <RefreshCw className="size-4" aria-hidden />
          Refresh
        </Button>
      </div>

      <div className="space-y-4">
        <UploadDropzone onUploaded={handleUploaded} />

        {selected ? <ImportSummary upload={selected} /> : null}

        {state.error ? <p className="text-destructive text-sm">{state.error}</p> : null}

        <UploadHistoryTable
          items={state.items}
          loading={state.loading}
          onDelete={(id) => void handleDelete(id)}
          onSelect={(id) => void handleSelect(id)}
        />
      </div>
    </div>
  );
}
