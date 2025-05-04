# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY apps/backend/requirements.txt .
COPY apps/frontend /app/frontend

RUN pip install -r requirements.txt

COPY apps/backend .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]