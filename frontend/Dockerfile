# =============================================================================
# FGN Savings Bond Frontend - Multi-Stage Dockerfile
# =============================================================================
# Stages:
#   - deps:       Install dependencies (shared)
#   - test:       Run tests, linting (has Node.js)
#   - build:      Build production assets
#   - production: Serve with nginx (no Node.js)
#
# Usage:
#   Production:  docker build -t frontend .
#   Test:        docker build --target test -t frontend-test .
# =============================================================================

# -----------------------------------------------------------------------------
# Dependencies stage (shared base for test and build)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# -----------------------------------------------------------------------------
# Test stage (has Node.js - can run tests, lint, type-check)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS test

WORKDIR /app

# Copy only package.json (not lock file) to ensure correct platform binaries
# This is necessary due to npm bug with optional deps: https://github.com/npm/cli/issues/4828
# The lock file may not include linux-arm64-musl variants if generated on macOS
COPY package.json ./
RUN npm install

# Copy source code
COPY . .

# Default command runs tests
CMD ["npm", "run", "test:run"]

# -----------------------------------------------------------------------------
# Build stage (compile TypeScript, bundle assets)
# -----------------------------------------------------------------------------
FROM deps AS build

WORKDIR /app

# Copy source code
COPY . .

# Build the application
RUN npm run build

# -----------------------------------------------------------------------------
# Production stage (nginx only - minimal image size)
# -----------------------------------------------------------------------------
FROM nginx:alpine AS production

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
