'use client';

import type * as React from 'react';

import { Trash2 } from 'lucide-react';

import type { UploadListItem } from '@kayak/shared';

import { UploadStatusBadge } from '@/features/uploads/status-badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { formatBytes, formatDateTime, formatDuration } from '@/lib/format';

interface UploadHistoryTableProps {
  readonly items: readonly UploadListItem[];
  readonly loading: boolean;
  readonly onDelete: (id: number) => void;
  readonly onSelect: (id: number) => void;
}

export function UploadHistoryTable({
  items,
  loading,
  onDelete,
  onSelect,
}: UploadHistoryTableProps): React.JSX.Element {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Upload history</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-muted-foreground py-8 text-center text-sm">No uploads yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="text-muted-foreground border-b">
                <tr className="[&>th]:px-3 [&>th]:py-2 [&>th]:text-left [&>th]:font-medium">
                  <th>File</th>
                  <th>Status</th>
                  <th>Type</th>
                  <th className="text-right">Imported</th>
                  <th className="text-right">Skipped</th>
                  <th className="text-right">Errors</th>
                  <th className="text-right">Duration</th>
                  <th>Uploaded</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => onSelect(item.id)}
                    className="hover:bg-muted/50 cursor-pointer border-b [&>td]:px-3 [&>td]:py-2"
                  >
                    <td className="max-w-[220px] truncate">
                      <span className="font-medium">{item.original_filename}</span>
                      <span className="text-muted-foreground block text-xs">
                        {item.file_type.toUpperCase()} · {formatBytes(item.file_size)}
                      </span>
                    </td>
                    <td>
                      <UploadStatusBadge status={item.upload_status} />
                    </td>
                    <td className="text-muted-foreground">{item.report_type ?? '—'}</td>
                    <td className="text-right tabular-nums">{item.imported_rows}</td>
                    <td className="text-right tabular-nums">{item.skipped_rows}</td>
                    <td className="text-right tabular-nums">{item.error_count}</td>
                    <td className="text-right tabular-nums">
                      {formatDuration(item.processing_ms)}
                    </td>
                    <td className="text-muted-foreground whitespace-nowrap">
                      {formatDateTime(item.uploaded_at)}
                    </td>
                    <td className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Delete ${item.original_filename}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(item.id);
                        }}
                      >
                        <Trash2 className="text-muted-foreground size-4" aria-hidden />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
