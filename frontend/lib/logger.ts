/**
 * Thin console wrapper — the single seam for client-side logging.
 *
 * Centralizing this (rather than calling `console.*` directly, which lint
 * disallows) lets us later forward errors to an aggregator and quiet noise in
 * production without touching call sites.
 */

type LogArgs = readonly unknown[];

const isProduction = process.env.NODE_ENV === 'production';

export const logger = {
  debug(...args: LogArgs): void {
    if (!isProduction) {
      // eslint-disable-next-line no-console
      console.debug('[kayak]', ...args);
    }
  },
  info(...args: LogArgs): void {
    if (!isProduction) {
      // eslint-disable-next-line no-console
      console.info('[kayak]', ...args);
    }
  },
  warn(...args: LogArgs): void {
    console.warn('[kayak]', ...args);
  },
  error(...args: LogArgs): void {
    console.error('[kayak]', ...args);
  },
} as const;
