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

class Cliente(EntidadSistema):
    """Clase Cliente con atributos encapsulados y validación estricta."""
    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self._nombre = None
        self._correo = None
        self._telefono = None

        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        log_sistema.info(f"Cliente registrado: ID={self._id_entidad}, Nombre={self._nombre}")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise ErrorValidacionCliente("El nombre del cliente debe tener mínimo 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not valor or not re.match(patron, valor.strip()):
            raise ErrorValidacionCliente(f"Formato de correo inválido: '{valor}'.")
        self._correo = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.strip().isdigit() or len(valor.strip()) < 7:
            raise ErrorValidacionCliente(f"Teléfono inválido: '{valor}'. Debe contener solo dígitos (mínimo 7).")
        self._telefono = valor.strip()

    def mostrar_detalle(self) -> str:
        return f"[Cliente] ID: {self._id_entidad} | Nombre: {self._nombre} | Correo: {self._correo} | Tel: {self._telefono}"

