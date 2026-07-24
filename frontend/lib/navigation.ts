/** Sidebar navigation configuration. */

import {
  ArrowUpFromLine,
  LayoutDashboard,
  type LucideIcon,
  MapPin,
  Plane,
  Settings,
  SlidersHorizontal,
  Table2,
} from 'lucide-react';

import { APP_ROUTES } from '@kayak/shared';

export interface NavItem {
  readonly label: string;
  readonly href: string;
  readonly icon: LucideIcon;
  /** When true, the route has real Phase 1 content; otherwise it is a placeholder. */
  readonly implemented: boolean;
}

export const PRIMARY_NAV: readonly NavItem[] = [
  { label: 'Dashboard', href: APP_ROUTES.dashboard, icon: LayoutDashboard, implemented: true },
  { label: 'Reports', href: APP_ROUTES.reports, icon: Table2, implemented: false },
  {
    label: 'Optimization',
    href: APP_ROUTES.optimization,
    icon: SlidersHorizontal,
    implemented: false,
  },
  { label: 'Routes', href: APP_ROUTES.routes, icon: MapPin, implemented: false },
  { label: 'Airports', href: APP_ROUTES.airports, icon: Plane, implemented: false },
  { label: 'Exports', href: APP_ROUTES.exports, icon: ArrowUpFromLine, implemented: false },
] as const;

export const SECONDARY_NAV: readonly NavItem[] = [
  { label: 'Settings', href: APP_ROUTES.settings, icon: Settings, implemented: true },
] as const;
