FROM python:3.11-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia todos los archivos del proyecto
COPY . /app

# Instala las dependencias del MCP
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir mcp gitingest

# Cambia al directorio donde está el servidor MCP
WORKDIR /app/src/gitingest_mcp

# Ejecuta el servidor MCP (por STDIO)
ENTRYPOINT ["python", "mcp_server.py"]
