import type * as React from 'react';

import { APP_NAME, APP_VERSION } from '@kayak/shared';

import { env } from '@/lib/env';

/** Application footer: name, version, environment. */
export function Footer(): React.JSX.Element {
  return (
    <footer className="text-muted-foreground border-t px-6 py-4 text-xs">
      <div className="flex flex-col items-center justify-between gap-1 sm:flex-row">
        <span>
          {APP_NAME} · v{APP_VERSION}
        </span>
        <span className="capitalize">Environment: {env.nodeEnv}</span>
      </div>
    </footer>
  );
}
