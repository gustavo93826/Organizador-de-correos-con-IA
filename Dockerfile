FROM python:3.12-slim

# Instala uv (el mismo gestor de paquetes que se usa en todo el proyecto)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copia solo los archivos de dependencias primero: así Docker cachea
# esta capa y no reinstala todo cada vez que solo cambia el código de la app.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copiamos el código de la aplicación
COPY app ./app

# Carpetas para los volúmenes de datos y logs (se montan desde docker-compose)
RUN mkdir -p data logs

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]