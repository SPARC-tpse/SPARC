# Replace Alpine
# FROM node:22-alpine
# With full Debian-based image:
FROM node:22-bullseye

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all source files
COPY . .

# Expose Nuxt dev port
EXPOSE 3000

# Start Nuxt dev server
CMD ["npm", "run", "dev", "--", "-o"]
