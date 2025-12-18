# 1. Usar imagen base de Python 3.12 (coincide con tu pyproject.toml)
FROM python:3.12-slim

# 2. Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo en el contenedor
WORKDIR /app

# 4. Instalar dependencias del sistema necesarias para compilar psycopg (Postgres)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar Poetry
RUN pip install poetry

# 6. Copiar archivos de configuración de dependencias
COPY pyproject.toml poetry.lock /app/

# 7. Configurar Poetry para no crear entorno virtual e instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 8. Copiar el resto del código del proyecto
COPY . /app/

# 9. Exponer el puerto
EXPOSE 8000

# 10. Comando para iniciar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]