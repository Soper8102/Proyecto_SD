
FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requerimientos.txt .
RUN pip install --no-cache-dir -r requerimientos.txt


COPY . .

EXPOSE 8001


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]