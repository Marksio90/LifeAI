# Development Dockerfile for Frontend
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose port
EXPOSE 3000

# Default command (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]
