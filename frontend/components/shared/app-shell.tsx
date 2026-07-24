'use client';

import * as React from 'react';

import { Footer } from '@/components/shared/footer';
import { Header } from '@/components/shared/header';
import { Sidebar } from '@/components/shared/sidebar';
import { cn } from '@/lib/utils';

/**
 * Responsive application shell: a persistent desktop sidebar rail, a slide-in
 * mobile drawer, the top header, the scrollable content area, and the footer.
 */
export function AppShell({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const closeMobile = React.useCallback(() => setMobileOpen(false), []);

  return (
    <div className="flex min-h-svh">
      {/* Desktop sidebar rail */}
      <aside className="hidden w-64 shrink-0 border-r lg:block">
        <div className="sticky top-0 h-svh">
          <Sidebar />
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            aria-label="Close navigation menu"
            className="absolute inset-0 bg-black/50"
            onClick={closeMobile}
          />
          <div
            className={cn(
              'absolute inset-y-0 left-0 w-64 border-r shadow-lg',
              'animate-in slide-in-from-left duration-200',
            )}
          >
            <Sidebar onNavigate={closeMobile} />
          </div>
        </div>
      ) : null}

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onOpenSidebar={() => setMobileOpen(true)} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
        <Footer />
      </div>
    </div>
  );
}
