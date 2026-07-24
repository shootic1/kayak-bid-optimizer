'use client';

import type * as React from 'react';

import { Menu } from 'lucide-react';

import { ThemeToggle } from '@/components/shared/theme-toggle';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  readonly onOpenSidebar: () => void;
}

/** Top application header: mobile menu trigger + theme toggle. */
export function Header({ onOpenSidebar }: HeaderProps): React.JSX.Element {
  return (
    <header className="bg-background/95 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-30 flex h-14 items-center gap-2 border-b px-4 backdrop-blur">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        aria-label="Open navigation menu"
        onClick={onOpenSidebar}
      >
        <Menu />
      </Button>

      <div className="flex-1" />

      <ThemeToggle />
    </header>
  );
}
