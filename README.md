# GitIngest MCP Server

Un servidor MCP (Model Context Protocol) que integra GitIngest para generar archivos de contexto de repositorios de GitHub privados, diseñado para nodos de resolución de tareas LLM.

## 🚀 Características

- **Integración completa con GitIngest**: Soporte para repositorios públicos y privados de GitHub
- **Protocolo MCP**: Compatible con el estándar MCP para integración con agentes de IA
- **Dockerizado**: Fácil despliegue y ejecución en contenedores
- **Configuración flexible**: Patrones de inclusión/exclusión personalizables
- **Manejo robusto de errores**: Fallback automático a CLI si el paquete Python no está disponible
- **Seguridad**: Ejecución como usuario no-root en contenedores

## 📋 Requisitos

- Python 3.11+
- Docker (opcional, para ejecución en contenedor)
- Token de acceso personal de GitHub (para repositorios privados)

## 🛠️ Instalación

### Opción 1: Ejecución Directa

```bash
# Clonar o descargar el proyecto
cd "Gitingest MCP"

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env y agregar tu GITHUB_TOKEN
```

### Opción 2: Docker

```bash
# Construir la imagen localmente
docker build -t gitingest-mcp .

# O usar docker-compose
docker-compose up --build

# O usar el script automatizado
./build_and_publish.sh
```

### 3. Publicación de Imagen Docker

Para publicar la imagen en GitHub Container Registry:

```bash
# Usar el script automatizado (recomendado)
./build_and_publish.sh

# O manualmente
docker build -t ghcr.io/gooapps/gitingest-mcp:latest .
docker push ghcr.io/gooapps/gitingest-mcp:latest
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `env.example`:

```bash
# Token de GitHub (requerido para repositorios privados)
GITHUB_TOKEN=ghp_your_token_here

# Configuración opcional
LOG_LEVEL=INFO
GITINGEST_MAX_FILE_SIZE=1048576  # 1MB
GITINGEST_TIMEOUT=300  # 5 minutos
```

### Token de GitHub

Para acceder a repositorios privados, necesitas un token de acceso personal de GitHub:

1. Ve a [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Genera un nuevo token con los siguientes scopes:
   - `repo` (para repositorios privados)
   - `public_repo` (para repositorios públicos)
3. Copia el token y configúralo en la variable `GITHUB_TOKEN`

## 🚀 Uso

### Ejecución Directa

```bash
# Usar el script de inicio (recomendado)
./start.sh

# O ejecutar directamente
python -m gitingest_mcp.mcp_server
```

### Docker

```bash
# Ejecutar con docker-compose
docker-compose up

# O ejecutar directamente
docker run -e GITHUB_TOKEN=your_token_here gitingest-mcp
```

## 🔧 Herramientas MCP Disponibles

### 1. `ingest_repository`

Genera un digest de texto de un repositorio de GitHub.

**Parámetros:**
- `repository_url` (requerido): URL del repositorio de GitHub
- `github_token` (opcional): Token de GitHub (si no está en variables de entorno)
- `branch` (opcional): Rama específica a analizar
- `include_patterns` (opcional): Patrones de archivos a incluir
- `exclude_patterns` (opcional): Patrones de archivos a excluir
- `max_file_size` (opcional): Tamaño máximo de archivo en bytes

**Ejemplo:**
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

El servidor devuelve texto estructurado optimizado para consumo de LLM:

```
Repository: owner/repo-name
Files analyzed: 42
Estimated tokens: 15.2k

Directory structure:
└── project-name/
    ├── src/
    │   ├── main.py
    │   └── utils.py
    ├── tests/
    │   └── test_main.py
    └── README.md

================================================
FILE: src/main.py
================================================
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

## 🔗 Integración con Nodos LLM

### Uso con Imagen Docker Publicada (Recomendado)

Para usar la imagen Docker publicada en GitHub Container Registry:

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

### Uso con Imagen Docker Local

Si prefieres construir la imagen localmente:

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

### Configuración Estilo Atlassian

Para usar con herramientas que requieren configuración similar al MCP de Atlassian:

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

### Ejemplo de Uso con Otros Clientes MCP

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializar
            await session.initialize()
            
            # Listar herramientas
            tools = await session.list_tools()
            print("Herramientas disponibles:", tools)
            
            # Usar herramienta
            result = await session.call_tool(
                "ingest_repository",
                {
                    "repository_url": "https://github.com/user/repo",
                    "include_patterns": ["*.py", "*.md"]
                }
            )
            print("Resultado:", result)

asyncio.run(main())
```

## 🐳 Docker Compose

El archivo `docker-compose.yml` incluye:

- Configuración de salud del contenedor
- Límites de recursos
- Política de reinicio
- Configuración de seguridad
- Sistema de archivos de solo lectura

## 🔒 Seguridad

- Ejecución como usuario no-root en contenedores
- Sistema de archivos de solo lectura
- Límites de recursos configurados
- Validación de URLs de GitHub
- Manejo seguro de tokens

## 🐛 Solución de Problemas

### Error: "GitIngest package not found"

```bash
# Instalar GitIngest
pip install gitingest

# O verificar que el CLI esté disponible
gitingest --help
```

### Error: "GitHub token required"

```bash
# Configurar token de GitHub
export GITHUB_TOKEN=your_token_here

# O crear archivo .env
echo "GITHUB_TOKEN=your_token_here" > .env
```

### Error: "Repository not found"

- Verifica que la URL del repositorio sea correcta
- Asegúrate de que el token tenga permisos para el repositorio
- Para repositorios privados, el token debe tener scope `repo`

## 📝 Logs

Los logs se pueden configurar con la variable `LOG_LEVEL`:

- `DEBUG`: Información detallada
- `INFO`: Información general (por defecto)
- `WARNING`: Solo advertencias y errores
- `ERROR`: Solo errores

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/your-repo/gitingest-mcp/issues)
- **Documentación**: [GitIngest Docs](https://github.com/coderamp-labs/gitingest)
- **Comunidad**: [Discord](https://discord.gg/zerRaGK9EC)
