'use client';

import type * as React from 'react';

import { ThemeProvider as NextThemesProvider } from 'next-themes';

type ThemeProviderProps = React.ComponentProps<typeof NextThemesProvider>;

/** App-wide theme provider (light/dark) backed by next-themes. */
export function ThemeProvider({ children, ...props }: ThemeProviderProps): React.JSX.Element {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
