# Dockerfile para TR&RS Management System
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Crear usuario no-root
RUN useradd -m -u 1000 trrs && chown -R trrs:trrs /app
USER trrs

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "trrs_project.wsgi:application"]
