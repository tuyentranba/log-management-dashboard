FROM node:20-alpine

WORKDIR /app

# Copy package files first for layer caching
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code (bind mount will override in dev)
COPY . .

# Expose Next.js dev port
EXPOSE 3000

# Command is overridden by docker-compose with npm run dev
CMD ["npm", "run", "dev"]
