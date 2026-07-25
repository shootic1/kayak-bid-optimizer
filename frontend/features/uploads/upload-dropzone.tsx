'use client';

import * as React from 'react';

import { CloudUpload, Loader2 } from 'lucide-react';

import type { UploadDetail } from '@kayak/shared';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { uploadFile, type UploadProgress } from '@/services/uploads-service';

const ACCEPTED_EXTENSIONS = ['.xlsx', '.csv', '.tsv'] as const;

function hasAcceptedExtension(name: string): boolean {
  const lower = name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

interface UploadDropzoneProps {
  readonly onUploaded: (upload: UploadDetail) => void;
}

/** Drag-and-drop + browse upload control with progress reporting. */
export function UploadDropzone({ onUploaded }: UploadDropzoneProps): React.JSX.Element {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = React.useState(false);
  const [uploading, setUploading] = React.useState(false);
  const [progress, setProgress] = React.useState<UploadProgress | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handleFile = React.useCallback(
    async (file: File) => {
      setError(null);
      if (!hasAcceptedExtension(file.name)) {
        setError('Unsupported file type. Please upload a .xlsx, .csv, or .tsv file.');
        return;
      }
      setUploading(true);
      setProgress({ loaded: 0, total: file.size, percent: 0 });

      const result = await uploadFile(file, setProgress);

      setUploading(false);
      setProgress(null);
      if (result.ok) {
        onUploaded(result.data);
      } else {
        setError(result.error);
      }
    },
    [onUploaded],
  );

  const onDrop = (event: React.DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) void handleFile(file);
  };

  const onSelect = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (file) void handleFile(file);
    event.target.value = '';
  };

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          'flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors',
          dragging ? 'border-primary bg-primary/5' : 'border-input',
          uploading && 'pointer-events-none opacity-70',
        )}
      >
        <span className="bg-muted text-muted-foreground flex size-12 items-center justify-center rounded-full">
          {uploading ? (
            <Loader2 className="size-6 animate-spin" aria-hidden />
          ) : (
            <CloudUpload className="size-6" aria-hidden />
          )}
        </span>
        <div className="space-y-1">
          <p className="text-sm font-medium">
            {uploading ? 'Uploading…' : 'Drag & drop a report file here'}
          </p>
          <p className="text-muted-foreground text-xs">Accepted formats: .xlsx, .csv, .tsv</p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={uploading}
          onClick={() => inputRef.current?.click()}
        >
          Browse files
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          className="hidden"
          onChange={onSelect}
        />
      </div>

      {progress ? (
        <div className="space-y-1">
          <div className="bg-muted h-2 w-full overflow-hidden rounded-full">
            <div
              className="bg-primary h-full transition-[width]"
              style={{ width: `${progress.percent}%` }}
            />
          </div>
          <p className="text-muted-foreground text-right text-xs">{progress.percent}%</p>
        </div>
      ) : null}

      {error ? <p className="text-destructive text-sm">{error}</p> : null}
    </div>
  );
}
