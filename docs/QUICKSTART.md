# 🚀 GitIngest MCP Server - Quick Start Guide

## Instalación Rápida

### 1. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env y agregar tu token de GitHub
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
```

### 2. Instalar Dependencias

```bash
# Opción A: Instalación directa
pip install -r requirements.txt

# Opción B: Usar Makefile
make install
```

### 3. Ejecutar el Servidor

```bash
# Opción A: Script de inicio
./start.sh

# Opción B: Directamente
python -m gitingest_mcp.mcp_server

# Opción C: Con Docker
docker-compose up --build
```

## Uso Básico

### Probar el Servidor

```bash
# Ejecutar tests
python test_mcp.py

# O usar Makefile
make test
```

### Ejemplo de Uso

```python
# example_client.py muestra cómo usar el servidor
python example_client.py
```

## Integración con Claude Desktop

### Opción 1: Imagen Docker Publicada (Recomendado)

```json
{
  "mcpServers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "GITHUB_TOKEN",
        "ghcr.io/gooapps/gitingest-mcp:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### Opción 2: Imagen Docker Local

```json
{
  "mcpServers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "GITHUB_TOKEN",
        "gitingest-mcp:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### Opción 3: Configuración Estilo Atlassian

```json
{
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e", "GITHUB_TOKEN",
    "-e", "LOG_LEVEL",
    "ghcr.io/gooapps/gitingest-mcp:latest"
  ],
  "env": {
    "GITHUB_TOKEN": "",
    "LOG_LEVEL": "INFO"
  }
}
```

## Comandos Útiles

```bash
# Ver ayuda
make help

# Limpiar archivos temporales
make clean

# Verificar token de GitHub
make check-token

# Test con repositorio público
make test-public
```

## Solución de Problemas

### Error: "GitIngest not found"
```bash
pip install gitingest
```

### Error: "GitHub token required"
```bash
export GITHUB_TOKEN=your_token_here
```

### Error: "Permission denied"
```bash
chmod +x start.sh
chmod +x test_mcp.py
chmod +x example_client.py
```

¡Listo! Tu servidor MCP está funcionando. 🎉
