'use client';

import type * as React from 'react';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

import type { NavItem } from '@/lib/navigation';
import { cn } from '@/lib/utils';

interface SidebarNavProps {
  readonly items: readonly NavItem[];
  readonly onNavigate?: () => void;
}

/** Renders a group of sidebar navigation links with active-route highlighting. */
export function SidebarNav({ items, onNavigate }: SidebarNavProps): React.JSX.Element {
  const pathname = usePathname();

  return (
    <nav className="grid gap-1">
      {items.map((item) => {
        const isActive = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href);
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            aria-current={isActive ? 'page' : undefined}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
              isActive && 'bg-sidebar-accent text-sidebar-accent-foreground',
            )}
          >
            <Icon className="size-4 shrink-0" aria-hidden />
            <span className="truncate">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
