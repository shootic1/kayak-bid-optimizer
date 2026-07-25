import type * as React from 'react';

import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

import type { UploadDetail } from '@kayak/shared';

import { UploadStatusBadge } from '@/features/uploads/status-badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDuration } from '@/lib/format';

interface StatProps {
  readonly label: string;
  readonly value: string | number;
}

function Stat({ label, value }: StatProps): React.JSX.Element {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

/** Detailed outcome of the most recent import. */
export function ImportSummary({ upload }: { upload: UploadDetail }): React.JSX.Element {
  const failed = upload.upload_status === 'failed';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2 text-base">
          {failed ? (
            <XCircle className="text-destructive size-5" aria-hidden />
          ) : (
            <CheckCircle2 className="text-success size-5" aria-hidden />
          )}
          Import summary — {upload.original_filename}
        </CardTitle>
        <UploadStatusBadge status={upload.upload_status} />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Imported rows" value={upload.imported_rows} />
          <Stat label="Skipped rows" value={upload.skipped_rows} />
          <Stat label="Errors" value={upload.error_count} />
          <Stat label="Duration" value={formatDuration(upload.processing_ms)} />
        </div>

        {upload.report_type ? (
          <p className="text-muted-foreground text-sm">
            Detected report type: <span className="font-medium">{upload.report_type}</span>
          </p>
        ) : null}

        {upload.error_message ? (
          <p className="text-destructive flex items-start gap-2 text-sm">
            <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
            {upload.error_message}
          </p>
        ) : null}

        {upload.validation_errors.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium">Validation errors</p>
            <div className="max-h-48 overflow-y-auto rounded-md border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 text-muted-foreground">
                  <tr>
                    <th className="px-3 py-1.5 text-left font-medium">Row</th>
                    <th className="px-3 py-1.5 text-left font-medium">Field</th>
                    <th className="px-3 py-1.5 text-left font-medium">Message</th>
                  </tr>
                </thead>
                <tbody>
                  {upload.validation_errors.map((err, index) => (
                    <tr key={`${err.row}-${err.field}-${index}`} className="border-t">
                      <td className="px-3 py-1.5">{err.row}</td>
                      <td className="px-3 py-1.5 font-mono text-xs">{err.field}</td>
                      <td className="px-3 py-1.5">{err.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
