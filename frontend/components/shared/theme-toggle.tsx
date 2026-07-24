'use client';

import type * as React from 'react';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';

import { Button } from '@/components/ui/button';

/**
 * Toggle between light and dark themes.
 *
 * Both icons are always rendered and their visibility is driven by the `.dark`
 * class via CSS. This avoids a hydration mismatch without a mounted-state guard
 * (and the cascading-render it would cause).
 */
export function ThemeToggle(): React.JSX.Element {
  const { resolvedTheme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Toggle color theme"
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
    >
      <Sun className="dark:hidden" aria-hidden />
      <Moon className="hidden dark:block" aria-hidden />
      <span className="sr-only">Toggle color theme</span>
    </Button>
  );
}
