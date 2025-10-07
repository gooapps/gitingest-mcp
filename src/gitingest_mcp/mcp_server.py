#!/usr/bin/env python3
"""
GitIngest MCP Server - Compatible con entornos locales y remotos

Versión adaptada para evitar errores de doble autenticación (Duplicate header: Authorization)
al ejecutar en Flowise o contenedores Docker con GITHUB_TOKEN.
"""

from typing import Annotated
from gitingest import ingest_async
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import subprocess

# Inicializa el servidor MCP
mcp = FastMCP("Gitingest MCP Server", log_level="ERROR")


@mcp.tool()
async def ingest_git(
    source: Annotated[
        str,
        Field(description="URL del repositorio Git o ruta local a analizar."),
    ],
    max_file_size: Annotated[
        int,
        Field(description="Tamaño máximo de archivo permitido para ingestión (por defecto 10 MB)."),
    ] = 10 * 1024 * 1024,
    include_patterns: Annotated[
        str,
        Field(description="Patrones de archivos a incluir, e.g. '*.py, src/'."),
    ] = "",
    exclude_patterns: Annotated[
        str,
        Field(description="Patrones de archivos a excluir, e.g. 'node_modules/, *.md'."),
    ] = "",
    branch: Annotated[
        str,
        Field(description="Branch del repositorio a clonar (por defecto 'main')."),
    ] = "main",
) -> str:
    """
    Clona y analiza el repositorio indicado, generando resumen, estructura y contenido.
    Compatible con repositorios privados de GitHub mediante GITHUB_TOKEN.
    """

    token = os.getenv("GITHUB_TOKEN")

    if token:
        # 🚫 Evitamos que gitingest duplique cabeceras Authorization
        os.environ.pop("GITHUB_TOKEN", None)

        # 🧠 Configuramos git globalmente con el token para repos privados
        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "url.https://x-access-token:"
                + token
                + "@github.com/.insteadOf",
                "https://github.com/",
            ],
            check=False,
        )

    # Ejecutar la ingestión real
    summary, tree, content = await ingest_async(
        source,
        max_file_size=max_file_size,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        branch=branch,
    )

    return "\n\n".join([summary, tree, content])


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
