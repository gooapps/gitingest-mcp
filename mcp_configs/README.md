# Configuraciones MCP para GitIngest

Este directorio contiene diferentes configuraciones para usar el servidor MCP de GitIngest con varios clientes.

## 📁 Archivos de Configuración

### `claude_desktop_config.json`
Configuración para usar la imagen Docker publicada en GitHub Container Registry.

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
        "ghcr.io/robertoperez/gitingest-mcp:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### `claude_desktop_config_local.json`
Configuración para usar una imagen Docker construida localmente.

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

### `claude_desktop_config_direct.json`
Configuración para ejecutar directamente el servidor Python (sin Docker).

```json
{
  "mcpServers": {
    "gitingest": {
      "command": "python",
      "args": [
        "/path/to/your/gitingest-mcp/mcp_server.py"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

## 🔧 Variables de Entorno Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `GITHUB_TOKEN` | Token de acceso personal de GitHub (requerido para repositorios privados) | - |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | INFO |
| `GITINGEST_MAX_FILE_SIZE` | Tamaño máximo de archivo en bytes | 1048576 (1MB) |
| `GITINGEST_TIMEOUT` | Timeout en segundos | 300 (5 minutos) |

## 🚀 Instrucciones de Uso

### 1. Con Imagen Docker Publicada (Recomendado)

```bash
# 1. Copiar la configuración
cp mcp_configs/claude_desktop_config.json ~/.config/claude-desktop/claude_desktop_config.json

# 2. Editar y agregar tu token de GitHub
# Reemplazar "your_github_token_here" con tu token real

# 3. Reiniciar Claude Desktop
```

### 2. Con Imagen Docker Local

```bash
# 1. Construir la imagen localmente
docker build -t gitingest-mcp:latest .

# 2. Copiar la configuración local
cp mcp_configs/claude_desktop_config_local.json ~/.config/claude-desktop/claude_desktop_config.json

# 3. Editar y agregar tu token de GitHub
# 4. Reiniciar Claude Desktop
```

### 3. Ejecución Directa (Sin Docker)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Copiar la configuración directa
cp mcp_configs/claude_desktop_config_direct.json ~/.config/claude-desktop/claude_desktop_config.json

# 3. Editar la ruta del servidor y agregar tu token
# 4. Reiniciar Claude Desktop
```

## 🔑 Configuración del Token de GitHub

1. Ve a [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Genera un nuevo token con los siguientes scopes:
   - `repo` (para repositorios privados)
   - `public_repo` (para repositorios públicos)
3. Copia el token y reemplázalo en la configuración

## 🧪 Verificación

Para verificar que la configuración funciona:

1. Abre Claude Desktop
2. Verifica que el servidor MCP aparezca en la lista de servidores conectados
3. Prueba con un comando como: "Ingiere el repositorio https://github.com/octocat/Hello-World"

## 🐛 Solución de Problemas

### Error: "Docker not found"
- Instala Docker Desktop
- Asegúrate de que Docker esté ejecutándose

### Error: "Image not found"
- Para imagen publicada: Verifica que la imagen existe en el registry
- Para imagen local: Ejecuta `docker build -t gitingest-mcp:latest .`

### Error: "GitHub token required"
- Verifica que el token esté configurado correctamente
- Asegúrate de que el token tenga los scopes necesarios

### Error: "Permission denied"
- Verifica los permisos del archivo de configuración
- Asegúrate de que Claude Desktop tenga acceso al archivo
