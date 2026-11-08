"""
Módulo de Excepciones Personalizadas para Software FJ.
Define la jerarquía de errores para control del sistema.
"""

class SoftwareFJException(Exception):
    """Excepción base para todos los errores de la aplicación."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_GEN"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self):
        return f"[{self.codigo_error}] {self.mensaje}"


class ErrorValidacionCliente(SoftwareFJException):
    """Lanzada cuando los datos de un cliente no cumplen las restricciones."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLI_01")


class ServicioNoDisponibleException(SoftwareFJException):
    """Lanzada cuando un servicio excede capacidad o no tiene stock."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SRV_02")


class ReservaInvalidaException(SoftwareFJException):
    """Lanzada al intentar procesar o cancelar una reserva en estado incompatible."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_RSV_03")


class OperacionNoPermitidaException(SoftwareFJException):
    """Lanzada para operaciones que violan reglas del negocio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_OP_04")
