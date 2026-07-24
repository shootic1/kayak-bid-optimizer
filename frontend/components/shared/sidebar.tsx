'use client';

import type * as React from 'react';

import Link from 'next/link';
import { Plane } from 'lucide-react';

import { APP_NAME, APP_ROUTES, APP_VERSION } from '@kayak/shared';

import { SidebarNav } from '@/components/shared/sidebar-nav';
import { Separator } from '@/components/ui/separator';
import { PRIMARY_NAV, SECONDARY_NAV } from '@/lib/navigation';

interface SidebarProps {
  readonly onNavigate?: () => void;
}

/** Sidebar contents: brand, primary nav, secondary nav. Reused by desktop rail and mobile drawer. */
export function Sidebar({ onNavigate }: SidebarProps): React.JSX.Element {
  return (
    <div className="bg-sidebar flex h-full flex-col gap-4 p-4">
      <Link
        href={APP_ROUTES.dashboard}
        onClick={onNavigate}
        className="flex items-center gap-2 px-2 py-1"
      >
        <span className="bg-sidebar-primary text-sidebar-primary-foreground flex size-8 items-center justify-center rounded-md">
          <Plane className="size-4" aria-hidden />
        </span>
        <span className="flex flex-col leading-tight">
          <span className="text-sidebar-foreground text-sm font-semibold">{APP_NAME}</span>
          <span className="text-sidebar-foreground/60 text-xs">v{APP_VERSION}</span>
        </span>
      </Link>

      <Separator className="bg-sidebar-border" />

      <div className="flex-1 overflow-y-auto">
        <SidebarNav items={PRIMARY_NAV} onNavigate={onNavigate} />
      </div>

      <Separator className="bg-sidebar-border" />
      <SidebarNav items={SECONDARY_NAV} onNavigate={onNavigate} />
    </div>
  );
}
