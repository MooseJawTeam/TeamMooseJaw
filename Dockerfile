FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "moosejawums.wsgi:application", "--bind", "0.0.0.0:8000"]
