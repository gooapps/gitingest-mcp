# 🎯 Ejemplo de Uso - Configuración Estilo Atlassian

Basado en tu ejemplo del MCP de Atlassian, aquí tienes la configuración exacta para usar el servidor MCP de GitIngest:

## 📋 Configuración JSON

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

## 🚀 Pasos para Implementar

### 1. Construir y Publicar la Imagen Docker

```bash
# En el directorio del proyecto
cd "Gitingest MCP"

# Construir y publicar la imagen
./build_and_publish.sh

# O manualmente
docker build -t ghcr.io/gooapps/gitingest-mcp:latest .
docker push ghcr.io/gooapps/gitingest-mcp:latest
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

### 3. Usar en tu Herramienta MCP

Agrega la configuración JSON a tu herramienta. Por ejemplo, para Claude Desktop:

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
        "-e", "LOG_LEVEL",
        "-e", "GITINGEST_MAX_FILE_SIZE",
        "-e", "GITINGEST_TIMEOUT",
        "ghcr.io/gooapps/gitingest-mcp:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here",
        "LOG_LEVEL": "INFO",
        "GITINGEST_MAX_FILE_SIZE": "1048576",
        "GITINGEST_TIMEOUT": "300"
      }
    }
  }
}
```

## 🔧 Herramientas Disponibles

Una vez configurado, tendrás acceso a estas herramientas MCP:

### 1. `ingest_repository`
Genera un digest de texto de un repositorio de GitHub.

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

## 🧪 Pruebas

### Probar la Imagen

```bash
# Probar que la imagen funciona
docker run --rm -e GITHUB_TOKEN=your_token ghcr.io/gooapps/gitingest-mcp:latest python -c "import mcp; print('MCP server is working')"
```

### Probar con un Repositorio

```bash
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

## 🔑 Configuración del Token de GitHub

1. Ve a [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Genera un nuevo token con los siguientes scopes:
   - `repo` (para repositorios privados)
   - `public_repo` (para repositorios públicos)
3. Copia el token y configúralo en la variable `GITHUB_TOKEN`

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

## 📝 Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `GITHUB_TOKEN` | Token de acceso personal de GitHub (requerido para repositorios privados) | - |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | INFO |
| `GITINGEST_MAX_FILE_SIZE` | Tamaño máximo de archivo en bytes | 1048576 (1MB) |
| `GITINGEST_TIMEOUT` | Timeout en segundos | 300 (5 minutos) |

## 🎉 ¡Listo!

Con esta configuración, tu servidor MCP de GitIngest estará disponible para:

1. **Generar archivos de contexto** de repositorios GitHub privados
2. **Integrarse con nodos LLM** para resolución de tareas
3. **Proporcionar texto estructurado** optimizado para consumo de LLM
4. **Manejar repositorios privados** con autenticación GitHub

¡Tu servidor MCP está listo para usar desde cualquier herramienta compatible! 🚀
