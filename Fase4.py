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

# 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
class SoftwareFJException(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_GEN"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self):
        return f"[{self.codigo_error}] {self.mensaje}"


class ErrorValidacionCliente(SoftwareFJException):
    """Lanzada cuando los datos del cliente no superan las validaciones."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLI_01")


class ServicioNoDisponibleException(SoftwareFJException):
    """Lanzada cuando un servicio supera capacidad o agota stock."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SRV_02")


class ReservaInvalidaException(SoftwareFJException):
    """Lanzada cuando una reserva no cumple las reglas de negocio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_RSV_03")


class OperacionNoPermitidaException(SoftwareFJException):
    """Lanzada ante transiciones de estado no permitidas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_OP_04")

# 3. ENTIDADES BASE Y CLIENTE (Encapsulamiento y Validaciones)
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

# 4. SERVICIOS ESPECIALIZADOS (Abstracción, Herencia y Polimorfismo)

class Servicio(EntidadSistema):
    """Clase abstracta base para servicios de Software FJ."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float):
        super().__init__(id_servicio)
        if tarifa_base <= 0:
            raise ValueError("La tarifa base debe ser mayor a 0.")
        self._nombre = nombre
        self._tarifa_base = tarifa_base

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def calcular_costo(self, unidades: int) -> float:
        pass

    @abstractmethod
    def validar_disponibilidad(self, requerimiento: int) -> bool:
        pass

class ReservaSala(Servicio):
    """Servicio: Reserva de salas de conferencias o juntas."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_por_hora: float, capacidad_maxima: int):
        super().__init__(id_servicio, nombre, tarifa_por_hora)
        self.capacidad_maxima = capacidad_maxima

    def validar_disponibilidad(self, personas: int) -> bool:
        if personas > self.capacidad_maxima:
            raise ServicioNoDisponibleException(
                f"Capacidad superada en {self.nombre}. Máximo {self.capacidad_maxima} personas, solicitadas: {personas}."
            )
        return True

    def calcular_costo(self, horas: int) -> float:
        if horas <= 0:
            raise ValueError("El número de horas debe ser mayor a 0.")
        return self._tarifa_base * horas

    def mostrar_detalle(self) -> str:
        return f"[Sala] {self._nombre} | Tarifa/h: ${self._tarifa_base:,.2f} | Capacidad: {self.capacidad_maxima} pers."


class AlquilerEquipo(Servicio):
    """Servicio: Alquiler de equipos tecnológicos."""
    def __init__(self, id_servicio: str, nombre: str, costo_por_dia: float, stock_disponible: int):
        super().__init__(id_servicio, nombre, costo_por_dia)
        self.stock_disponible = stock_disponible

    def validar_disponibilidad(self, cantidad: int) -> bool:
        if cantidad > self.stock_disponible:
            raise ServicioNoDisponibleException(
                f"Stock insuficiente en {self.nombre}. Disponibles: {self.stock_disponible}, solicitados: {cantidad}."
            )
        return True

    def calcular_costo(self, dias: int) -> float:
        if dias <= 0:
            raise ValueError("El número de días debe ser mayor a 0.")
        costo = self._tarifa_base * dias
        if dias >= 5:
            costo *= 0.90  # 10% de descuento automático a partir de 5 días
        return costo

    def mostrar_detalle(self) -> str:
        return f"[Equipo] {self._nombre} | Tarifa/día: ${self._tarifa_base:,.2f} | Stock: {self.stock_disponible} unid."


class AsesoriaEspecializada(Servicio):
    """Servicio: Asesorías y consultorías técnicas."""
    def __init__(self, id_servicio: str, nombre: str, tarifa_por_hora: float, consultor: str):
        super().__init__(id_servicio, nombre, tarifa_por_hora)
        self.consultor = consultor

    def validar_disponibilidad(self, horas: int) -> bool:
        if horas > 8:
            raise ServicioNoDisponibleException(
                f"El consultor {self.consultor} no puede atender más de 8 horas continuas."
            )
        return True

    def calcular_costo(self, horas: int) -> float:
        if horas <= 0:
            raise ValueError("Las horas de asesoría deben ser mayores a 0.")
        return self._tarifa_base * horas

    def mostrar_detalle(self) -> str:
        return f"[Asesoría] {self._nombre} | Consultor: {self.consultor} | Tarifa/h: ${self._tarifa_base:,.2f}"

# 5. RESERVA Y SOBRECARGA DE MÉTODOS
class Reserva:
    """Clase Reserva con control de estados y sobrecarga de costos."""
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_CANCELADA = "CANCELADA"

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, unidades: int, parametro_disp: int):
        if unidades <= 0:
            raise ReservaInvalidaException("Las unidades de reserva deben ser mayores a cero.")

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.unidades = unidades
        self.parametro_disp = parametro_disp
        self.estado = self.ESTADO_PENDIENTE
        log_sistema.info(f"Reserva creada [{self.id_reserva}] para {self.cliente.nombre}.")

    def confirmar(self):
        if self.estado == self.ESTADO_CONFIRMADA:
            raise OperacionNoPermitidaException(f"La reserva {self.id_reserva} ya está confirmada.")
        if self.estado == self.ESTADO_CANCELADA:
            raise OperacionNoPermitidaException(f"No se puede confirmar la reserva {self.id_reserva} porque está cancelada.")

        # Validación polimórfica según el tipo de servicio
        self.servicio.validar_disponibilidad(self.parametro_disp)
        self.estado = self.ESTADO_CONFIRMADA
        log_sistema.info(f"Reserva {self.id_reserva} confirmada con éxito.")

    def cancelar(self):
        if self.estado == self.ESTADO_CANCELADA:
            raise OperacionNoPermitidaException(f"La reserva {self.id_reserva} ya se encuentra cancelada.")
        self.estado = self.ESTADO_CANCELADA
        log_sistema.warning(f"Reserva {self.id_reserva} cancelada.")

    def calcular_costo_total(self, porcentaje_descuento: float = 0.0, impuesto_iva: float = 0.19, es_corporativo: bool = False) -> float:
        """Sobrecarga simulada mediante parámetros opcionales."""
        costo_base = self.servicio.calcular_costo(self.unidades)
        descuento = porcentaje_descuento + (5.0 if es_corporativo else 0.0)
        subtotal = costo_base * (1.0 - (descuento / 100.0))
        return round(subtotal * (1.0 + impuesto_iva), 2)

    def mostrar_resumen(self) -> str:
        return f"Reserva [{self.id_reserva}] | Estado: {self.estado} | Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre}"

# 6. SIMULACIÓN DE AL MENOS 10 OPERACIONES (Manejo Robusto de Excepciones)

def main():
    print("=" * 70)
    print("      SOFTWARE FJ - SISTEMA DE CLIENTES, SERVICIOS Y RESERVAS")
    print("               SIMULACIÓN DE 10 OPERACIONES (FASE 4)")
    print("=" * 70)

    clientes = []
    servicios = []
    reservas = []

    # Op 1: Cliente Válido
    print("\n[Operación 1] Registro de cliente válido...")
    try:
        c1 = Cliente("CLI-001", "Jonathan Másmela", "jonathan@unad.edu.co", "3154889900")
        clientes.append(c1)
    except ErrorValidacionCliente as e:
        log_sistema.error(f"Fallo Op 1: {e}")
    else:
        print(f" -> ÉXITO: {c1.mostrar_detalle()}")
    finally:
        print(" -> [Op 1 Finalizada]")

    # Op 2: Cliente con correo inválido
    print("\n[Operación 2] Registro de cliente con correo inválido...")
    try:
        c_err1 = Cliente("CLI-002", "Pedro Gómez", "correo_sin_arroba", "3112223344")
        clientes.append(c_err1)
    except ErrorValidacionCliente as e:
        log_sistema.warning(f"Captura controlada Op 2: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 2 Finalizada sin interrupción]")

    # Op 3: Cliente con teléfono inválido
    print("\n[Operación 3] Registro de cliente con letras en el teléfono...")
    try:
        c_err2 = Cliente("CLI-003", "Maria Ruiz", "maria@mail.com", "TELEFONO123")
        clientes.append(c_err2)
    except ErrorValidacionCliente as e:
        log_sistema.warning(f"Captura controlada Op 3: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 3 Finalizada]")

    # Op 4: Creación de catálogo polimórfico de Servicios
    print("\n[Operación 4] Creación polimórfica de Servicios...")
    try:
        s_sala = ReservaSala("SRV-01", "Sala de Juntas Principal", tarifa_por_hora=50000.0, capacidad_maxima=12)
        s_equipo = AlquilerEquipo("SRV-02", "Kit Proyector + Portátil", costo_por_dia=40000.0, stock_disponible=4)
        s_asesoria = AsesoriaEspecializada("SRV-03", "Consultoría Cloud", tarifa_por_hora=95000.0, consultor="Ing. Juan Arango")
        servicios.extend([s_sala, s_equipo, s_asesoria])
    except Exception as e:
        log_sistema.error(f"Fallo Op 4: {e}")
    else:
        for s in servicios:
            print(f" -> {s.mostrar_detalle()}")
    finally:
        print(" -> [Op 4 Finalizada]")

    # Op 5: Reserva válida confirmada y liquidada
    print("\n[Operación 5] Reserva y liquidación exitosa...")
    try:
        r1 = Reserva("RES-001", c1, s_sala, unidades=3, parametro_disp=8)
        r1.confirmar()
        reservas.append(r1)
        total = r1.calcular_costo_total(porcentaje_descuento=10.0, es_corporativo=True)
    except SoftwareFJException as e:
        log_sistema.error(f"Fallo Op 5: {e}")
    else:
        print(f" -> ÉXITO: {r1.mostrar_resumen()}")
        print(f" -> Costo Total Liquidado: ${total:,.2f}")
    finally:
        print(" -> [Op 5 Finalizada]")

    # Op 6: Reserva rechazada por capacidad excedida
    print("\n[Operación 6] Reserva de sala superando la capacidad máxima...")
    try:
        r2 = Reserva("RES-002", c1, s_sala, unidades=2, parametro_disp=20)
        r2.confirmar()
    except ServicioNoDisponibleException as e:
        log_sistema.warning(f"Captura controlada Op 6: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 6 Finalizada]")

    # Op 7: Reserva rechazada por falta de stock
    print("\n[Operación 7] Alquiler solicitando más equipos de los disponibles...")
    try:
        r3 = Reserva("RES-003", c1, s_equipo, unidades=2, parametro_disp=10)
        r3.confirmar()
    except ServicioNoDisponibleException as e:
        log_sistema.warning(f"Captura controlada Op 7: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 7 Finalizada]")

    # Op 8: Reserva rechazada por exceder horas de consultor
    print("\n[Operación 8] Asesoría superando el límite de 8 horas...")
    try:
        r4 = Reserva("RES-004", c1, s_asesoria, unidades=10, parametro_disp=10)
        r4.confirmar()
    except ServicioNoDisponibleException as e:
        log_sistema.warning(f"Captura controlada Op 8: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 8 Finalizada]")

    # Op 9: Doble confirmación no permitida
    print("\n[Operación 9] Intento de volver a confirmar una reserva ya confirmada...")
    try:
        r1.confirmar()
    except OperacionNoPermitidaException as e:
        log_sistema.warning(f"Captura controlada Op 9: {e}")
        print(f" -> ERROR CONTROLADO: {e}")
    finally:
        print(" -> [Op 9 Finalizada]")

    # Op 10: Cancelación y validación de estado
    print("\n[Operación 10] Cancelar reserva y reintentar confirmación...")
    try:
        r1.cancelar()
        print(f" -> Reserva en estado: {r1.estado}")
        r1.confirmar()
    except OperacionNoPermitidaException as e:
        log_sistema.warning(f"Captura controlada Op 10: {e}")
        print(f" -> ERROR CONTROLADO: Operación rechazada correctamente tras cancelación.")
    finally:
        print(" -> [Op 10 Finalizada]")

    print("\n" + "=" * 70)
    print("SIMULACIÓN 10/10 FINALIZADA - SISTEMA ESTABLE Y LOGS REGISTRADOS")
    print("=" * 70)

if __name__ == "__main__":
    main()
