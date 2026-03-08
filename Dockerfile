# Multi-stage build for optimized production image
FROM node:20-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++ cairo-dev jpeg-dev pango-dev giflib-dev

# Copy all workspace package.json files so npm ci resolves workspace links
COPY package*.json ./
COPY packages/contracts/package.json packages/contracts/
COPY packages/github-pages-index-core/package.json packages/github-pages-index-core/
COPY web-react/package.json web-react/
COPY apps/mobile/package.json apps/mobile/
COPY apps/desktop/package.json apps/desktop/

# Install dependencies (includes devDependencies like TypeScript)
RUN npm ci && \
    npm cache clean --force

# Copy source code (web-react/apps excluded via .dockerignore for image size)
COPY src/ src/
COPY packages/ packages/
COPY tsconfig.json ./

# Build contracts first (workspace dependency), then main project
RUN npm run -w packages/contracts build && \
    npm run build

# Trim to production-only dependencies for runtime image
RUN npm prune --omit=dev

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    dumb-init \
    curl \
    ca-certificates && \
    addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built application from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app/packages ./packages

# Create required directories (including /data for Fly.io volume mount)
RUN mkdir -p db atomized/embeddings /data .batch-checkpoints logs && \
    chown -R nodejs:nodejs db atomized /data .batch-checkpoints logs /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Use non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Default command - start web server
CMD ["node", "dist/web-server.js"]
