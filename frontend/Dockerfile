# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# KAYAK Bid Optimizer Pro — Frontend image (Next.js 16 standalone)
# Build context is the MONOREPO ROOT so the @kayak/shared workspace package is
# available. Produces a minimal standalone server run by a non-root user.
# ---------------------------------------------------------------------------

FROM node:26-alpine AS base
RUN npm install -g pnpm@11.17.0
ENV NEXT_TELEMETRY_DISABLED=1

# ---- Dependencies (cached on lockfile + manifests) ------------------------
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY shared/package.json ./shared/
COPY frontend/package.json ./frontend/
RUN pnpm install --frozen-lockfile

# ---- Builder: compile the standalone production bundle --------------------
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/shared/node_modules ./shared/node_modules
COPY --from=deps /app/frontend/node_modules ./frontend/node_modules
COPY . .
# Trace files from the monorepo root so standalone output is self-contained.
ENV NEXT_OUTPUT_FILE_TRACING_ROOT=/app
RUN pnpm --filter @kayak/frontend build

# ---- Runner: standalone Next.js server as non-root ------------------------
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs
COPY --from=builder /app/frontend/public ./frontend/public
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/static ./frontend/.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "frontend/server.js"]
