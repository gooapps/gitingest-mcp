# 🌐 Uso Externo del GitIngest MCP Server

Esta guía explica cómo usar el servidor MCP de GitIngest desde otras herramientas, similar al ejemplo del MCP de Atlassian que proporcionaste.

## 🐳 Configuración Docker para Uso Externo

### Configuración Básica (Estilo Atlassian)

```json
{
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e", "GITHUB_TOKEN",
    "-e", "LOG_LEVEL",
    "-e", "GITINGEST_MAX_FILE_SIZE",
    "-e", "GITINGEST_TIMEOUT",
    "ghcr.io/gooapps/gitingest-mcp:latest"
  ],
  "env": {
    "GITHUB_TOKEN": "",
    "LOG_LEVEL": "INFO",
    "GITINGEST_MAX_FILE_SIZE": "1048576",
    "GITINGEST_TIMEOUT": "300"
  }
}
```

### Configuración Simplificada

```json
{
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
```

## 🚀 Pasos para Implementar

### 1. Construir y Publicar la Imagen

```bash
# Clonar el repositorio
git clone https://github.com/gooapps/gitingest-mcp.git
cd gitingest-mcp

# Construir y publicar la imagen
./build_and_publish.sh
```

### 2. Configurar Variables de Entorno

```bash
# Configurar tu token de GitHub
export GITHUB_TOKEN="ghp_your_token_here"

# Opcional: Configurar otros parámetros
export LOG_LEVEL="INFO"
export GITINGEST_MAX_FILE_SIZE="1048576"
export GITINGEST_TIMEOUT="300"
```

### 3. Usar en tu Herramienta

Agrega la configuración JSON a tu herramienta MCP. Por ejemplo, para Claude Desktop:

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

## 🔧 Herramientas MCP Disponibles

Una vez configurado, tendrás acceso a estas herramientas:

### 1. `ingest_repository`
Genera un digest de texto de un repositorio de GitHub.

**Parámetros:**
- `repository_url` (requerido): URL del repositorio
- `github_token` (opcional): Token de GitHub
- `branch` (opcional): Rama específica
- `include_patterns` (opcional): Patrones de archivos a incluir
- `exclude_patterns` (opcional): Patrones de archivos a excluir
- `max_file_size` (opcional): Tamaño máximo de archivo

**Ejemplo de uso:**
```json
{
  "name": "ingest_repository",
  "arguments": {
    "repository_url": "https://github.com/user/private-repo",
    "include_patterns": ["*.py", "*.js", "*.md"],
    "exclude_patterns": ["node_modules/*", "*.log"],
    "max_file_size": 51200
  }
}
```

### 2. `ingest_repository_async`
Versión asíncrona para procesamiento por lotes.

### 3. `validate_repository_url`
Valida si una URL es un repositorio de GitHub válido.

## 📊 Formato de Salida

El servidor devuelve texto estructurado optimizado para LLM:

```
Repository: owner/repo-name
Files analyzed: 42
Estimated tokens: 15.2k

Directory structure:
└── project-name/
    ├── src/
    │   ├── main.py
    │   └── utils.py
    └── README.md

================================================
FILE: src/main.py
================================================
def hello_world():
    print("Hello, World!")
```

## 🔑 Configuración del Token de GitHub

1. Ve a [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Genera un nuevo token con los siguientes scopes:
   - `repo` (para repositorios privados)
   - `public_repo` (para repositorios públicos)
3. Copia el token y configúralo en la variable `GITHUB_TOKEN`

## 🧪 Pruebas

### Probar la Imagen Localmente

```bash
# Probar que la imagen funciona
docker run --rm -e GITHUB_TOKEN=your_token ghcr.io/gooapps/gitingest-mcp:latest python -c "import mcp; print('MCP server is working')"

# Probar con un repositorio público
docker run --rm -e GITHUB_TOKEN=your_token ghcr.io/gooapps/gitingest-mcp:latest python -c "
from mcp_server import GitIngestMCPServer
import asyncio
async def test():
    server = GitIngestMCPServer()
    result = await server._ingest_repository({'repository_url': 'https://github.com/octocat/Hello-World'})
    print('Test successful:', len(result[0].text) > 0)
asyncio.run(test())
"
```

### Probar con Claude Desktop

1. Configura el archivo `claude_desktop_config.json`
2. Reinicia Claude Desktop
3. Verifica que el servidor MCP aparezca en la lista de servidores conectados
4. Prueba con: "Ingiere el repositorio https://github.com/octocat/Hello-World"

## 🐛 Solución de Problemas

### Error: "Image not found"
```bash
# Verificar que la imagen existe
docker images | grep gitingest-mcp

# Si no existe, construirla
docker build -t ghcr.io/gooapps/gitingest-mcp:latest .
```

### Error: "GitHub token required"
```bash
# Verificar que el token esté configurado
echo $GITHUB_TOKEN

# Configurar el token
export GITHUB_TOKEN="ghp_your_token_here"
```

### Error: "Permission denied"
```bash
# Verificar permisos del token
# El token debe tener scopes: repo, public_repo
```

### Error: "Repository not found"
- Verifica que la URL del repositorio sea correcta
- Asegúrate de que el token tenga permisos para el repositorio
- Para repositorios privados, el token debe tener scope `repo`

## 📝 Logs y Debugging

### Habilitar Logs Detallados

```json
{
  "env": {
    "GITHUB_TOKEN": "your_token_here",
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Ver Logs del Contenedor

```bash
# Ejecutar con logs visibles
docker run --rm -e GITHUB_TOKEN=your_token -e LOG_LEVEL=DEBUG ghcr.io/gooapps/gitingest-mcp:latest
```

## 🔄 Actualizaciones

Para actualizar a la última versión:

```bash
# Obtener la última imagen
docker pull ghcr.io/gooapps/gitingest-mcp:latest

# O reconstruir localmente
./build_and_publish.sh
```

## 🤝 Contribución

Si encuentras problemas o quieres mejorar la integración:

1. Abre un issue en el repositorio
2. Proporciona detalles sobre tu configuración
3. Incluye logs de error si los hay
4. Sugiere mejoras si tienes ideas

¡Tu servidor MCP de GitIngest está listo para usar desde cualquier herramienta compatible! 🚀
