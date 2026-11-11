"""
UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
Curso: Programación (Código: 213023)
Fase 4: Prácticas Simuladas
Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas (Software FJ)
"""

import os
import re
import logging
from abc import ABC, abstractmethod


# 1. SISTEMA DE LOGS (Sin bases de datos, trazabilidad en archivo)

def configurar_logger():
    nombre_archivo = "logs.txt"
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Handler para archivo de texto
        archivo_handler = logging.FileHandler(nombre_archivo, encoding="utf-8")
        formato = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        archivo_handler.setFormatter(formato)
        logger.addHandler(archivo_handler)

        # Handler para consola
        consola_handler = logging.StreamHandler()
        consola_handler.setFormatter(formato)
        logger.addHandler(consola_handler)

    return logger

log_sistema = configurar_logger()


# =============================================================================
# ENTIDADES BASE Y CLIENTE (Encapsulamiento y Validaciones)
# =============================================================================
class EntidadSistema(ABC):
    """Clase abstracta base para entidades del sistema."""
    def __init__(self, id_entidad: str):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abstractmethod
    def mostrar_detalle(self) -> str:
        pass

