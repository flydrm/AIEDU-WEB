FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .
COPY app /app/app
COPY content /app/content
EXPOSE 8080
CMD ["uvicorn", "app.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
