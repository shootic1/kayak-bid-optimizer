'use client';

import { useCallback, useEffect, useState } from 'react';

import type { ConnectionState, VersionResponse } from '@kayak/shared';

import { fetchHealth, fetchReadiness, fetchVersion } from './system-status-service';

export interface SystemStatus {
  readonly backend: ConnectionState;
  readonly database: ConnectionState;
  readonly version: VersionResponse | null;
  readonly lastCheckedAt: Date | null;
}

const INITIAL_STATUS: SystemStatus = {
  backend: 'loading',
  database: 'loading',
  version: null,
  lastCheckedAt: null,
};

/**
 * Poll backend liveness, database readiness, and version metadata.
 *
 * Returns the current status plus a manual `refresh` callback. All requests are
 * abortable and cleaned up on unmount.
 */
export function useSystemStatus(): { status: SystemStatus; refresh: () => void } {
  const [status, setStatus] = useState<SystemStatus>(INITIAL_STATUS);
  const [nonce, setNonce] = useState(0);

  const refresh = useCallback(() => {
    setStatus((prev) => ({ ...prev, backend: 'loading', database: 'loading' }));
    setNonce((value) => value + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;

    async function run(): Promise<void> {
      const [health, readiness, version] = await Promise.all([
        fetchHealth(signal),
        fetchReadiness(signal),
        fetchVersion(signal),
      ]);

      if (signal.aborted) {
        return;
      }

      const backend: ConnectionState =
        health.ok && health.data.status === 'healthy' ? 'online' : 'offline';

      const database: ConnectionState =
        readiness.ok && readiness.data.status === 'healthy' ? 'online' : 'offline';

      setStatus({
        backend,
        database,
        version: version.ok ? version.data : null,
        lastCheckedAt: new Date(),
      });
    }

    void run();
    return () => controller.abort();
  }, [nonce]);

  return { status, refresh };
}
