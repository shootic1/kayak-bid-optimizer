import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Produce a self-contained server bundle for small, fast Docker images.
  output: 'standalone',
  // Compile the in-repo workspace package from source (no prebuilt dist needed).
  transpilePackages: ['@kayak/shared'],
  reactStrictMode: true,
  poweredByHeader: false,
  // In the Docker monorepo build the workspace root is one level up.
  outputFileTracingRoot: process.env.NEXT_OUTPUT_FILE_TRACING_ROOT ?? undefined,
};

export default nextConfig;
