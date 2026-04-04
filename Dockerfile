# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
# Must install ALL deps to run 'vite build', plus the linux binary fix
RUN npm install && npm install @rollup/rollup-linux-x64-musl
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.11-slim AS backend-runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# This ensures the backend can serve the frontend files if needed
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
