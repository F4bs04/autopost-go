"""Configuração padrão de logging para o projeto."""

from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retorna um logger com configuração padrão.

    Args:
        name: Nome do logger. Usa o nome do módulo chamador por padrão.

    Returns:
        Instância de ``logging.Logger`` configurada.
    """

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    return logging.getLogger(name or __name__)

