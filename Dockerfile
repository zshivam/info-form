# Backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt

# Frontend build
WORKDIR /app/frontend
COPY frontend/ /app/frontend
RUN npm install
RUN npm run build

# Serve frontend from backend
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
