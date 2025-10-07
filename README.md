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

### `ingest_git`

**Descripción:** Clona y analiza el repositorio indicado, generando resumen, estructura y contenido. Evita la duplicación de cabeceras Authorization en entornos Docker persistentes.

**Parámetros:**
- `source` (requerido): URL del repositorio Git o ruta local a analizar
- `token` (requerido): Access token de GitHub para autenticación
- `max_file_size` (opcional): Tamaño máximo de archivo permitido para ingestión (por defecto 10 MB)
- `include_patterns` (opcional): Patrones de archivos a incluir, ej. '*.py, src/'
- `exclude_patterns` (opcional): Patrones de archivos a excluir, ej. 'node_modules/, *.md'
- `branch` (opcional): Branch del repositorio a clonar (por defecto 'main')

**Ejemplo de uso desde un cliente MCP:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/usuario/repositorio-privado",
    "token": "ghp_tu_token_aqui",
    "include_patterns": "*.py, *.js, *.md",
    "exclude_patterns": "node_modules/, __pycache__/, *.log",
    "max_file_size": 1048576,
    "branch": "main"
  }
}
```

**Casos de uso comunes:**

1. **Analizar repositorio completo:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto",
    "token": "ghp_tu_token_aqui"
  }
}
```

2. **Solo archivos de código fuente:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto",
    "token": "ghp_tu_token_aqui",
    "include_patterns": "*.py, *.js, *.ts, *.java, *.cpp, *.h",
    "exclude_patterns": "test/, tests/, __pycache__/, node_modules/"
  }
}
```

3. **Documentación específica:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto",
    "token": "ghp_tu_token_aqui",
    "include_patterns": "*.md, *.rst, docs/, README*",
    "max_file_size": 524288
  }
}
```

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

### Configuración para GitHub Copilot (IntelliJ/VSCode)

Para integrar con GitHub Copilot, crea o actualiza el archivo de configuración MCP:

**Archivo:** `~/.config/github-copilot/intellij/mcp.json` (IntelliJ) o `~/.config/github-copilot/vscode/mcp.json` (VSCode)

```json
{
  "servers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "docker.io/develgooapps/gitingest-mcp:main-26b875d"
      ]
    }
  }
}
```

### Configuración usando Imagen Docker Local

Si prefieres construir la imagen localmente:

```json
{
  "servers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "gitingest-mcp:latest"
      ]
    }
  }
}
```

### Configuración para Claude Desktop

Para usar con Claude Desktop, agrega al archivo de configuración:

**Archivo:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "docker.io/develgooapps/gitingest-mcp:main-26b875d"
      ]
    }
  }
}
```

### Configuración para Cline (VSCode Extension)

Para usar con la extensión Cline en VSCode:

```json
{
  "mcpServers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "docker.io/develgooapps/gitingest-mcp:main-26b875d"
      ]
    }
  }
}
```

## 🎯 Guía de Uso Práctica

### Configuración Inicial Rápida

1. **Obtener un Token de GitHub:**
   ```bash
   # Ve a: https://github.com/settings/tokens
   # Genera un nuevo token con permisos:
   # - repo (para repositorios privados)
   # - public_repo (para repositorios públicos)
   # Nota: Este token se usará directamente en las llamadas al MCP
   ```

2. **Configurar en GitHub Copilot (IntelliJ/VSCode):**
   ```bash
   # Crear directorio de configuración si no existe
   mkdir -p ~/.config/github-copilot/intellij
   
   # Crear archivo mcp.json
   cat > ~/.config/github-copilot/intellij/mcp.json << 'EOF'
   {
     "servers": {
       "gitingest": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "docker.io/develgooapps/gitingest-mcp:main-26b875d"
         ]
       }
     }
   }
   EOF
   ```

3. **Reiniciar GitHub Copilot** para que cargue la nueva configuración.

### Casos de Uso Comunes

#### 1. Análisis Completo de Repositorio
**Escenario:** Necesitas entender un repositorio completo para hacer contribuciones o debugging.

**Comando en el chat de Copilot:**
```
@gitingest analiza el repositorio https://github.com/empresa/proyecto-backend
Token: ghp_tu_token_aqui
```

**Llamada MCP interna:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto-backend",
    "token": "ghp_tu_token_aqui"
  }
}
```

#### 2. Análisis de Solo Código Fuente
**Escenario:** Solo quieres ver el código, sin documentación ni archivos de configuración.

**Comando en el chat:**
```
@gitingest analiza solo el código fuente de https://github.com/empresa/api-service
Incluye: *.py, *.js, *.ts, *.java
Excluye: tests/, docs/, *.md, node_modules/
Token: ghp_tu_token_aqui
```

**Llamada MCP interna:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/api-service",
    "token": "ghp_tu_token_aqui",
    "include_patterns": "*.py, *.js, *.ts, *.java",
    "exclude_patterns": "tests/, docs/, *.md, node_modules/"
  }
}
```

#### 3. Análisis de Documentación
**Escenario:** Solo necesitas la documentación del proyecto.

**Comando en el chat:**
```
@gitingest extrae solo la documentación de https://github.com/empresa/frontend-app
Incluye: *.md, *.rst, docs/, README*, CHANGELOG*
Token: ghp_tu_token_aqui
```

**Llamada MCP interna:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/frontend-app",
    "token": "ghp_tu_token_aqui",
    "include_patterns": "*.md, *.rst, docs/, README*, CHANGELOG*"
  }
}
```

#### 4. Análisis de Branch Específico
**Escenario:** Quieres analizar una feature branch específica.

**Comando en el chat:**
```
@gitingest analiza la rama feature/nueva-funcionalidad del repo https://github.com/empresa/proyecto
Token: ghp_tu_token_aqui
```

**Llamada MCP interna:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto",
    "token": "ghp_tu_token_aqui",
    "branch": "feature/nueva-funcionalidad"
  }
}
```

#### 5. Análisis con Límite de Tamaño
**Escenario:** El repo es muy grande y solo quieres archivos pequeños.

**Comando en el chat:**
```
@gitingest analiza https://github.com/empresa/proyecto-grande pero solo archivos menores a 500KB
Token: ghp_tu_token_aqui
```

**Llamada MCP interna:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/empresa/proyecto-grande",
    "token": "ghp_tu_token_aqui",
    "max_file_size": 512000
  }
}
```

### Flujo de Trabajo Típico

1. **Identificar Repositorio:** Obtén la URL del repositorio que necesitas analizar
2. **Determinar Scope:** Decide qué archivos necesitas (código, docs, config, etc.)
3. **Usar Filtros:** Aplica patrones de inclusión/exclusión según tu necesidad
4. **Ejecutar Análisis:** Usa el comando con @gitingest en tu cliente MCP
5. **Revisar Resultados:** El MCP retornará el contenido estructurado del repositorio

### Consejos de Uso

- **Repositorios Grandes:** Usa `exclude_patterns` para evitar `node_modules/`, `__pycache__/`, `.git/`
- **Análisis Específico:** Usa `include_patterns` para enfocarte en tipos de archivo específicos
- **Branches:** Especifica el branch si no quieres analizar `main`/`master`
- **Tamaño de Archivos:** Limita `max_file_size` para evitar archivos binarios grandes
- **Tokens:** Usa tokens con permisos mínimos necesarios para el repositorio

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

### Problemas Comunes y Soluciones

#### 1. Error: "Authentication failed" o "Repository not found"

**Síntomas:**
```
Error: Repository not found or access denied
HTTP 404: Not Found
```

**Soluciones:**
- Verifica que la URL del repositorio sea correcta
- Asegúrate de que el token de GitHub tenga los permisos necesarios:
  - `repo` para repositorios privados
  - `public_repo` para repositorios públicos
- Para repositorios de organizaciones, el token debe tener acceso a la organización

```bash
# Verificar permisos del token
curl -H "Authorization: token TU_TOKEN" https://api.github.com/user
```

#### 2. Error: "Docker image not found"

**Síntomas:**
```
Unable to find image 'docker.io/develgooapps/gitingest-mcp:main-26b875d'
```

**Soluciones:**
```bash
# Descargar la imagen manualmente
docker pull docker.io/develgooapps/gitingest-mcp:main-26b875d

# O construir localmente
cd "Gitingest MCP"
docker build -t gitingest-mcp:latest .

# Actualizar mcp.json para usar imagen local
# Cambiar "docker.io/develgooapps/gitingest-mcp:main-26b875d" por "gitingest-mcp:latest"
```

#### 3. Error: "GITHUB_TOKEN not set"

**Síntomas:**
```
Error: GitHub token is required but not provided
```

**Soluciones:**
- Verificar que estés pasando el token correctamente en la llamada al MCP
- Asegurar que el token no tenga espacios ni caracteres especiales
- El token debe incluirse en cada llamada individual al MCP, no en la configuración

**Ejemplo correcto de uso:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/usuario/repo",
    "token": "ghp_tu_token_sin_espacios"
  }
}
```

#### 4. Error: "Rate limit exceeded"

**Síntomas:**
```
API rate limit exceeded for user
```

**Soluciones:**
- Esperar una hora antes de hacer más requests
- Usar un token de GitHub autenticado (aumenta el límite de 60 a 5000 requests/hora)
- Para uso intensivo, considera usar GitHub Apps

#### 5. Error: "File too large" o "Repository too large"

**Síntomas:**
```
Error: File exceeds maximum size limit
Warning: Repository is very large
```

**Soluciones:**
```json
{
  "name": "ingest_git",
  "arguments": {
    "source": "https://github.com/user/large-repo",
    "token": "ghp_tu_token",
    "max_file_size": 1048576,
    "exclude_patterns": "*.zip, *.tar.gz, *.pdf, *.png, *.jpg, node_modules/, .git/"
  }
}
```

#### 6. Error: "MCP server not responding"

**Síntomas:**
- El chat no reconoce @gitingest
- No aparecen las herramientas del MCP

**Soluciones:**
1. Verificar que Docker esté ejecutándose:
```bash
docker ps
```

2. Probar la imagen manualmente:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
docker run -i --rm \
docker.io/develgooapps/gitingest-mcp:main-26b875d
```

3. Reiniciar GitHub Copilot/IDE después de cambios en mcp.json

4. Verificar logs de Docker:
```bash
docker logs $(docker ps -q --filter ancestor=docker.io/develgooapps/gitingest-mcp:main-26b875d)
```

### Mejores Prácticas

#### Gestión de Tokens
- **Rotación:** Rota los tokens de GitHub regularmente
- **Scope Mínimo:** Usa tokens con el mínimo scope necesario
- **Seguridad:** Nunca compartas tokens en código o logs
- **Uso Dinámico:** El token se pasa directamente en cada llamada al MCP, no se almacena en configuración

#### Optimización de Rendimiento
- **Filtros Inteligentes:** Usa patrones de exclusión para evitar archivos innecesarios
```json
{
  "exclude_patterns": "node_modules/, __pycache__/, .git/, *.log, *.tmp, dist/, build/"
}
```

- **Límites de Tamaño:** Establece límites apropiados para tu caso de uso
```json
{
  "max_file_size": 524288  // 512KB para análisis de código
}
```

#### Uso Eficiente
- **Branches Específicos:** Analiza branches específicos en lugar de todo el repositorio
- **Análisis Incremental:** Para repos grandes, analiza directorios específicos
- **Cache Local:** Docker cachea las imágenes, aprovecha esto para múltiples usos

### Verificación de Configuración

Usa este script para verificar que todo esté configurado correctamente:

```bash
#!/bin/bash
echo "🔍 Verificando configuración GitIngest MCP..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi
echo "✅ Docker está disponible"

# Verificar imagen
if docker image inspect docker.io/develgooapps/gitingest-mcp:main-26b875d &> /dev/null; then
    echo "✅ Imagen Docker encontrada"
else
    echo "⚠️  Descargando imagen Docker..."
    docker pull docker.io/develgooapps/gitingest-mcp:main-26b875d
fi

# Verificar archivo de configuración
MCP_CONFIG="$HOME/.config/github-copilot/intellij/mcp.json"
if [ -f "$MCP_CONFIG" ]; then
    echo "✅ Archivo mcp.json encontrado"
    if grep -q "gitingest" "$MCP_CONFIG"; then
        echo "✅ Configuración gitingest encontrada"
    else
        echo "❌ Configuración gitingest no encontrada en mcp.json"
    fi
else
    echo "❌ Archivo mcp.json no encontrado en $MCP_CONFIG"
fi

# Verificar que el MCP responda
echo "🧪 Probando conexión con el MCP..."
if echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
   docker run -i --rm docker.io/develgooapps/gitingest-mcp:main-26b875d > /dev/null 2>&1; then
    echo "✅ MCP responde correctamente"
else
    echo "❌ MCP no responde - verificar imagen Docker"
fi

echo "🎉 Verificación completada"
echo "💡 Recuerda: El token de GitHub se pasa dinámicamente en cada llamada al MCP"
```

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

