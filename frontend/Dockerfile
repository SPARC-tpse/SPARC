# === build ===
FROM node:22-alpine AS builder

WORKDIR /app

# Copy lockfile first for better layer caching
COPY package*.json ./

# ci instead of install: respects package-lock.json exactly, faster in CI/CD
RUN npm ci

COPY . .

# Build Nuxt — output goes to .output/
RUN npm run build


# === production runtime ===
FROM node:22-alpine AS production

LABEL org.opencontainers.image.title="SPARC Frontend" \
      org.opencontainers.image.description="Production Nuxt service"

WORKDIR /app

# Non-root user
RUN addgroup --system nuxt && adduser --system --ingroup nuxt nuxt

# Only copy the built output — no source, no node_modules, no devDependencies
COPY --from=builder --chown=nuxt:nuxt /app/.output /app/.output

USER nuxt

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

# Nuxt's standalone server — no node_modules required at runtime
CMD ["node", ".output/server/index.mjs"]


# === development ===
FROM node:22-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
