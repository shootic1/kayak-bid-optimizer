'use client';

import { useCallback, useEffect, useState } from 'react';

import type { UploadListItem } from '@kayak/shared';

import { deleteUpload, listUploads } from '@/services/uploads-service';

interface UploadsState {
  readonly items: UploadListItem[];
  readonly total: number;
  readonly loading: boolean;
  readonly error: string | null;
}

const INITIAL: UploadsState = { items: [], total: 0, loading: true, error: null };

export function useUploads(): {
  state: UploadsState;
  refresh: () => void;
  remove: (id: number) => Promise<boolean>;
} {
  const [state, setState] = useState<UploadsState>(INITIAL);
  const [nonce, setNonce] = useState(0);

  const refresh = useCallback(() => setNonce((n) => n + 1), []);

  const remove = useCallback(
    async (id: number): Promise<boolean> => {
      const result = await deleteUpload(id);
      if (result.ok) {
        refresh();
        return true;
      }
      setState((prev) => ({ ...prev, error: result.error }));
      return false;
    },
    [refresh],
  );

  useEffect(() => {
    const controller = new AbortController();

    async function load(): Promise<void> {
      setState((prev) => ({ ...prev, loading: true }));
      const result = await listUploads({ limit: 100 }, controller.signal);
      if (controller.signal.aborted) return;
      if (result.ok) {
        setState({
          items: result.data.items,
          total: result.data.total,
          loading: false,
          error: null,
        });
      } else {
        setState({ items: [], total: 0, loading: false, error: result.error });
      }
    }

    void load();
    return () => controller.abort();
  }, [nonce]);

  return { state, refresh, remove };
}
