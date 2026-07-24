/** Frontend application route paths (route ids). */

export const APP_ROUTES = {
  dashboard: '/',
  reports: '/reports',
  optimization: '/optimization',
  routes: '/routes',
  airports: '/airports',
  exports: '/exports',
  settings: '/settings',
} as const;

export type AppRouteKey = keyof typeof APP_ROUTES;
export type AppRoutePath = (typeof APP_ROUTES)[AppRouteKey];
