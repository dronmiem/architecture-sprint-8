# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build --verbose

# Production stage
FROM node:16-alpine
WORKDIR /app
RUN npm install -g serve

# Copy built assets from build stage
COPY --from=build /app/build /app/build

# Expose port
EXPOSE 3000

# Start nginx
CMD ["serve", "-s", "build", "-l", "3000"]