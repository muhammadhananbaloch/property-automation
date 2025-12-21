# frontend/Dockerfile
FROM node:24-alpine

# Set working directory
WORKDIR /app

# Copy package files first (so we don't reinstall dependencies on every change)
COPY package.json package-lock.json* ./

# Install the dependencies (this creates the node_modules folder inside the container)
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port Vite runs on
EXPOSE 5173

# Start the development server
# --host is REQUIRED for Docker to share the site with Windows
CMD ["npm", "run", "dev", "--", "--host"]
