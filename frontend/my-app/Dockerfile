# FRONTEND build
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/ /app/frontend
RUN npm install
RUN npm run build

# BACKEND build
FROM python:3.11-slim AS backend
WORKDIR /app/backend
COPY backend/ /app/backend
COPY --from=frontend /app/frontend/dist /app/backend/static
RUN pip install -r requirements.txt

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
