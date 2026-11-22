# UNAD - Fase 4: Prácticas Simuladas
# Software FJ: Sistema Integral de Gestión de Clientes, Servicios y Reservas
# Versión con interfaz gráfica Tkinter.
# No utiliza bases de datos: los datos se mantienen en listas mientras
# la aplicación está abierta. Los eventos y errores se registran en logs.txt.


import logging
import re
import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime

# 1. CONFIGURACIÓN DE LOGS

def configurar_logger():
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        archivo = logging.FileHandler("logs.txt", encoding="utf-8")
        archivo.setFormatter(formato)
        logger.addHandler(archivo)

    return logger


log_sistema = configurar_logger()

# 2. EXCEPCIONES PERSONALIZADAS

class SoftwareFJException(Exception):
    def __init__(self, mensaje, codigo_error="ERR_GEN"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self):
        return f"[{self.codigo_error}] {self.mensaje}"


class ErrorValidacionCliente(SoftwareFJException):
    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_CLI_01")


class ServicioNoDisponibleException(SoftwareFJException):
    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_SRV_02")


class ReservaInvalidaException(SoftwareFJException):
    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_RSV_03")


class OperacionNoPermitidaException(SoftwareFJException):
    def __init__(self, mensaje):
        super().__init__(mensaje, "ERR_OP_04")

# 3. ENTIDAD ABSTRACTA Y CLIENTE

class EntidadSistema(ABC):
    def __init__(self, id_entidad):
        if not str(id_entidad).strip():
            raise ValueError("El identificador es obligatorio.")
        self._id_entidad = str(id_entidad).strip()

    @property
    def id_entidad(self):
        return self._id_entidad

    @abstractmethod
    def mostrar_detalle(self):
        pass

class Cliente(EntidadSistema):
    def __init__(self, id_cliente, nombre, correo, telefono):
        super().__init__(id_cliente)
        self._nombre = None
        self._correo = None
        self._telefono = None
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        log_sistema.info("Cliente registrado: ID=%s, Nombre=%s",
                         self._id_entidad, self._nombre)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ErrorValidacionCliente(
                "El nombre debe tener mínimo 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        patron = r"^[\w.+-]+@[\w.-]+\.\w+$"
        if not valor or not re.match(patron, valor.strip()):
            raise ErrorValidacionCliente(
                f"Formato de correo inválido: '{valor}'."
            )
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if (not valor or not valor.strip().isdigit()
                or not 7 <= len(valor.strip()) <= 15):
            raise ErrorValidacionCliente(
                "El teléfono debe contener entre 7 y 15 dígitos."
            )
        self._telefono = valor.strip()

    def mostrar_detalle(self):
        return (f"[Cliente] ID: {self.id_entidad} | "
                f"Nombre: {self.nombre} | Correo: {self.correo} | "
                f"Tel: {self.telefono}")

# 4. SERVICIOS ABSTRACTOS Y ESPECIALIZADOS

class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre, tarifa_base):
        super().__init__(id_servicio)
        try:
            tarifa_base = float(tarifa_base)
        except (TypeError, ValueError) as error:
            raise ValueError("La tarifa debe ser numérica.") from error
        if tarifa_base <= 0:
            raise ValueError("La tarifa base debe ser mayor a cero.")
        if not nombre.strip():
            raise ValueError("El nombre del servicio es obligatorio.")
        self._nombre = nombre.strip()
        self._tarifa_base = tarifa_base

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @abstractmethod
    def calcular_costo(self, unidades):
        pass

    @abstractmethod
    def validar_disponibilidad(self, requerimiento):
        pass

class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_por_hora, capacidad_maxima):
        super().__init__(id_servicio, nombre, tarifa_por_hora)
        self.capacidad_maxima = int(capacidad_maxima)
        if self.capacidad_maxima <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")

    def validar_disponibilidad(self, personas):
        if int(personas) <= 0:
            raise ReservaInvalidaException("La cantidad de personas debe ser positiva.")
        if int(personas) > self.capacidad_maxima:
            raise ServicioNoDisponibleException(
                f"Capacidad superada. Máximo: {self.capacidad_maxima}; "
                f"solicitadas: {personas}."
            )
        return True

    def calcular_costo(self, horas):
        horas = float(horas)
        if horas <= 0:
            raise ValueError("Las horas deben ser mayores a cero.")
        return self.tarifa_base * horas

    def mostrar_detalle(self):
        return (f"[Sala] {self.nombre} | Tarifa/h: ${self.tarifa_base:,.2f} | "
                f"Capacidad: {self.capacidad_maxima} personas")

class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre, costo_por_dia, stock_disponible):
        super().__init__(id_servicio, nombre, costo_por_dia)
        self.stock_disponible = int(stock_disponible)
        if self.stock_disponible <= 0:
            raise ValueError("El stock debe ser mayor que cero.")

    def validar_disponibilidad(self, cantidad):
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ReservaInvalidaException("La cantidad solicitada debe ser positiva.")
        if cantidad > self.stock_disponible:
            raise ServicioNoDisponibleException(
                f"Stock insuficiente. Disponibles: {self.stock_disponible}; "
                f"solicitados: {cantidad}."
            )
        return True

    def calcular_costo(self, dias):
        dias = float(dias)
        if dias <= 0:
            raise ValueError("Los días deben ser mayores a cero.")
        costo = self.tarifa_base * dias
        if dias >= 5:
            costo *= 0.90
        return costo

    def mostrar_detalle(self):
        return (f"[Equipo] {self.nombre} | Tarifa/día: "
                f"${self.tarifa_base:,.2f} | Stock: {self.stock_disponible}")

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_por_hora, consultor):
        super().__init__(id_servicio, nombre, tarifa_por_hora)
        if not consultor.strip():
            raise ValueError("Debe indicar el nombre del consultor.")
        self.consultor = consultor.strip()

    def validar_disponibilidad(self, horas):
        horas = int(horas)
        if horas <= 0:
            raise ReservaInvalidaException("Las horas deben ser mayores a cero.")
        if horas > 8:
            raise ServicioNoDisponibleException(
                f"El consultor {self.consultor} no puede atender más de 8 horas."
            )
        return True

    def calcular_costo(self, horas):
        horas = float(horas)
        if horas <= 0:
            raise ValueError("Las horas deben ser mayores a cero.")
        return self.tarifa_base * horas

    def mostrar_detalle(self):
        return (f"[Asesoría] {self.nombre} | Consultor: {self.consultor} | "
                f"Tarifa/h: ${self.tarifa_base:,.2f}")

# 5. RESERVA Y CÁLCULO DE COSTOS CON PARÁMETROS OPCIONALES

class Reserva:
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_CANCELADA = "CANCELADA"

    def __init__(self, id_reserva, cliente, servicio, unidades, parametro_disp):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalidaException("Cliente o servicio no válido.")
        if float(unidades) <= 0 or int(parametro_disp) <= 0:
            raise ReservaInvalidaException("Las unidades y el requerimiento deben ser positivos.")

        self.id_reserva = str(id_reserva).strip()
        self.cliente = cliente
        self.servicio = servicio
        self.unidades = float(unidades)
        self.parametro_disp = int(parametro_disp)
        self.estado = self.ESTADO_PENDIENTE
        self.costo_total = 0.0
        log_sistema.info("Reserva creada: %s para %s",
                         self.id_reserva, self.cliente.nombre)

    def confirmar(self):
        if self.estado != self.ESTADO_PENDIENTE:
            raise OperacionNoPermitidaException(
                f"No se puede confirmar una reserva en estado {self.estado}."
            )
        self.servicio.validar_disponibilidad(self.parametro_disp)
        self.estado = self.ESTADO_CONFIRMADA
        log_sistema.info("Reserva %s confirmada.", self.id_reserva)

    def cancelar(self):
        if self.estado == self.ESTADO_CANCELADA:
            raise OperacionNoPermitidaException("La reserva ya está cancelada.")
        self.estado = self.ESTADO_CANCELADA
        log_sistema.warning("Reserva %s cancelada.", self.id_reserva)

    def calcular_costo_total(self, porcentaje_descuento=0.0,
                             impuesto_iva=0.19, es_corporativo=False):
        if self.estado != self.ESTADO_CONFIRMADA:
            raise OperacionNoPermitidaException(
                "La reserva debe estar confirmada para calcular el costo."
            )
        if not 0 <= float(porcentaje_descuento) <= 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")
        if not 0 <= float(impuesto_iva) <= 1:
            raise ValueError("El IVA debe expresarse entre 0 y 1 (ejemplo: 0.19).")

        costo_base = self.servicio.calcular_costo(self.unidades)
        descuento = float(porcentaje_descuento) + (5.0 if es_corporativo else 0.0)
        if descuento > 100:
            raise ValueError("El descuento total no puede superar el 100%.")
        subtotal = costo_base * (1 - descuento / 100)
        self.costo_total = round(subtotal * (1 + float(impuesto_iva)), 2)
        log_sistema.info("Costo calculado para reserva %s: %.2f",
                         self.id_reserva, self.costo_total)
        return self.costo_total

    def mostrar_resumen(self):
        return (f"Reserva [{self.id_reserva}] | {self.estado} | "
                f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre}")

# 6. SISTEMA DE GESTIÓN EN MEMORIA

class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
            raise ErrorValidacionCliente("Ya existe un cliente con esa identificación.")
        if any(c.correo.lower() == cliente.correo.lower() for c in self.clientes):
            raise ErrorValidacionCliente("Ya existe un cliente con ese correo.")
        self.clientes.append(cliente)

    def registrar_servicio(self, servicio):
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise ValueError("Ya existe un servicio con ese código.")
        self.servicios.append(servicio)

    def buscar_cliente(self, identificacion):
        for cliente in self.clientes:
            if cliente.id_entidad == identificacion:
                return cliente
        raise ErrorValidacionCliente("No se encontró el cliente seleccionado.")

    def buscar_servicio(self, codigo):
        for servicio in self.servicios:
            if servicio.id_entidad == codigo:
                return servicio
        raise ValueError("No se encontró el servicio seleccionado.")

    def crear_reserva(self, codigo, cliente, servicio, unidades, requerimiento):
        if any(r.id_reserva == codigo for r in self.reservas):
            raise ReservaInvalidaException("Ya existe una reserva con ese código.")
        reserva = Reserva(codigo, cliente, servicio, unidades, requerimiento)
        self.reservas.append(reserva)
        return reserva

    def buscar_reserva(self, codigo):
        for reserva in self.reservas:
            if reserva.id_reserva == codigo:
                return reserva
        raise ReservaInvalidaException("No se encontró la reserva seleccionada.")
