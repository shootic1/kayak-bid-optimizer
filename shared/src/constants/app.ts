/** Application-wide metadata. Single source of truth for the frontend. */

export const APP_NAME = 'KAYAK Bid Optimizer Pro' as const;
export const APP_VERSION = '1.0.0' as const;
export const SERVICE_NAME_BACKEND = 'backend' as const;

/** Deployment environments supported by the configuration strategy. */
export const ENVIRONMENTS = ['development', 'staging', 'production', 'test'] as const;
export type Environment = (typeof ENVIRONMENTS)[number];
