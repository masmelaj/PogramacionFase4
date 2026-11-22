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

# 7. INTERFAZ GRÁFICA TKINTER

class AplicacionSoftwareFJ:
    def __init__(self, root):
        self.root = root
        self.sistema = SistemaSoftwareFJ()
        self.root.title("PROGRAMA FJ")
        self.root.geometry("1120x720")
        self.root.minsize(980, 620)
        self.root.configure(bg="#eeeef7")

        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_contenido()
        self._actualizar_todo()

        log_sistema.info("Aplicación gráfica Software FJ iniciada.")

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TNotebook", background="#eef2f7", borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(18, 10),
                         font=("Segoe UI", 10, "bold"))
        estilo.configure("Treeview", rowheight=29, font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        estilo.configure("TLabel", background="#ffffff",
                         font=("Segoe UI", 10))
        estilo.configure("TButton", font=("Segoe UI", 9, "bold"),
                         padding=7)

    def _crear_encabezado(self):
        encabezado = tk.Frame(self.root, bg="#183153", height=88)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(encabezado, text="SOFTWARE FJ", bg="#183153",
                 fg="white", font=("Segoe UI", 22, "bold")).pack(
                     anchor="w", padx=25, pady=(13, 0))
        tk.Label(encabezado,
                 text="Sistema Integral de Gestión de Clientes, Servicios y Reservas",
                 bg="#183153", fg="#d7e4f2",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=27)

    def _crear_contenido(self):
        contenedor = tk.Frame(self.root, bg="#eef2f7")
        contenedor.pack(fill="both", expand=True, padx=18, pady=16)

        self.tarjetas = tk.Frame(contenedor, bg="#eef2f7")
        self.tarjetas.pack(fill="x", pady=(0, 13))

        self.lbl_clientes = self._crear_tarjeta(self.tarjetas, "CLIENTES", "0", "#2563eb")
        self.lbl_servicios = self._crear_tarjeta(self.tarjetas, "SERVICIOS", "0", "#059669")
        self.lbl_reservas = self._crear_tarjeta(self.tarjetas, "RESERVAS", "0", "#d97706")

        self.tabs = ttk.Notebook(contenedor)
        self.tabs.pack(fill="both", expand=True)

        self.tab_clientes = tk.Frame(self.tabs, bg="white", padx=16, pady=14)
        self.tab_servicios = tk.Frame(self.tabs, bg="white", padx=16, pady=14)
        self.tab_reservas = tk.Frame(self.tabs, bg="white", padx=16, pady=14)
        self.tab_logs = tk.Frame(self.tabs, bg="white", padx=16, pady=14)

        self.tabs.add(self.tab_clientes, text="Clientes")
        self.tabs.add(self.tab_servicios, text="Servicios")
        self.tabs.add(self.tab_reservas, text="Reservas")
        self.tabs.add(self.tab_logs, text="Registro de eventos")

        self._crear_tab_clientes()
        self._crear_tab_servicios()
        self._crear_tab_reservas()
        self._crear_tab_logs()

    def _crear_tarjeta(self, padre, titulo, valor, color):
        tarjeta = tk.Frame(padre, bg="white", highlightthickness=1,
                           highlightbackground="#dce3ec", padx=16, pady=9)
        tarjeta.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(tarjeta, text=titulo, bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        etiqueta = tk.Label(tarjeta, text=valor, bg="white", fg=color,
                            font=("Segoe UI", 22, "bold"))
        etiqueta.pack(anchor="w")
        return etiqueta

    def _campo(self, padre, etiqueta, fila, columna, ancho=25):
        tk.Label(padre, text=etiqueta, bg="white", fg="#334155",
                 font=("Segoe UI", 9, "bold")).grid(
                     row=fila, column=columna, sticky="w", padx=6, pady=(7, 2))
        entrada = ttk.Entry(padre, width=ancho)
        entrada.grid(row=fila + 1, column=columna, sticky="ew",
                     padx=6, pady=(0, 5))
        return entrada

    def _boton(self, padre, texto, comando, color="#2563eb"):
        return tk.Button(
            padre, text=texto, command=comando,
            bg=color, fg="white", activebackground=color,
            activeforeground="white", relief="flat",
            cursor="hand2", padx=12, pady=8,
            font=("Segoe UI", 9, "bold")
        )

    def _crear_tab_clientes(self):
        tk.Label(self.tab_clientes, text="Registro de clientes",
                 bg="white", fg="#183153",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))

        formulario = tk.Frame(self.tab_clientes, bg="white")
        formulario.pack(fill="x")
        self.cli_id = self._campo(formulario, "Identificación", 0, 0)
        self.cli_nombre = self._campo(formulario, "Nombre completo", 0, 1)
        self.cli_correo = self._campo(formulario, "Correo electrónico", 0, 2)
        self.cli_telefono = self._campo(formulario, "Teléfono", 0, 3)

        self._boton(self.tab_clientes, "Registrar cliente",
                    self.registrar_cliente).pack(anchor="e", pady=8)

        self.tree_clientes = self._crear_tabla(
            self.tab_clientes,
            ("id", "nombre", "correo", "telefono"),
            ("Identificación", "Nombre", "Correo", "Teléfono")
        )

    def _crear_tab_servicios(self):
        tk.Label(self.tab_servicios, text="Administración de servicios",
                 bg="white", fg="#183153",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))

        formulario = tk.Frame(self.tab_servicios, bg="white")
        formulario.pack(fill="x")

        self.srv_id = self._campo(formulario, "Código", 0, 0)
        self.srv_nombre = self._campo(formulario, "Nombre del servicio", 0, 1)
        self.srv_tarifa = self._campo(formulario, "Tarifa ($)", 0, 2)

        tk.Label(formulario, text="Tipo de servicio", bg="white",
                 fg="#334155", font=("Segoe UI", 9, "bold")).grid(
                     row=0, column=3, sticky="w", padx=6, pady=(7, 2))
        self.srv_tipo = ttk.Combobox(
            formulario, state="readonly",
            values=("Reserva de sala", "Alquiler de equipo", "Asesoría especializada"),
            width=23
        )
        self.srv_tipo.grid(row=1, column=3, sticky="ew", padx=6, pady=(0, 5))
        self.srv_tipo.current(0)

        self.srv_extra_label = tk.Label(
            formulario, text="Capacidad de sala", bg="white",
            fg="#334155", font=("Segoe UI", 9, "bold")
        )
        self.srv_extra_label.grid(row=2, column=0, sticky="w", padx=6, pady=(7, 2))
        self.srv_extra = ttk.Entry(formulario, width=25)
        self.srv_extra.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 5))
        self.srv_tipo.bind("<<ComboboxSelected>>", self._actualizar_etiqueta_extra)

        self._boton(self.tab_servicios, "Registrar servicio",
                    self.registrar_servicio).pack(anchor="e", pady=8)

        self.tree_servicios = self._crear_tabla(
            self.tab_servicios,
            ("id", "tipo", "nombre", "tarifa", "detalle"),
            ("Código", "Tipo", "Nombre", "Tarifa", "Capacidad / Stock / Consultor")
        )

    def _actualizar_etiqueta_extra(self, evento=None):
        tipo = self.srv_tipo.get()
        texto = {
            "Reserva de sala": "Capacidad de sala (personas)",
            "Alquiler de equipo": "Stock disponible (unidades)",
            "Asesoría especializada": "Nombre del consultor"
        }[tipo]
        self.srv_extra_label.config(text=texto)

    def _crear_tab_reservas(self):
        tk.Label(self.tab_reservas, text="Gestión de reservas",
                 bg="white", fg="#183153",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))

        formulario = tk.Frame(self.tab_reservas, bg="white")
        formulario.pack(fill="x")

        self.res_id = self._campo(formulario, "Código de reserva", 0, 0)
        tk.Label(formulario, text="Cliente", bg="white",
                 fg="#334155", font=("Segoe UI", 9, "bold")).grid(
                     row=0, column=1, sticky="w", padx=6, pady=(7, 2))
        self.res_cliente = ttk.Combobox(formulario, state="readonly", width=24)
        self.res_cliente.grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 5))

        tk.Label(formulario, text="Servicio", bg="white",
                 fg="#334155", font=("Segoe UI", 9, "bold")).grid(
                     row=0, column=2, sticky="w", padx=6, pady=(7, 2))
        self.res_servicio = ttk.Combobox(formulario, state="readonly", width=28)
        self.res_servicio.grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 5))

        self.res_unidades = self._campo(formulario, "Horas o días", 0, 3)
        self.res_requerimiento = self._campo(
            formulario, "Personas / equipos / horas", 2, 0
        )

        self._boton(self.tab_reservas, "Crear reserva",
                    self.crear_reserva).pack(anchor="e", pady=8)

        self.tree_reservas = self._crear_tabla(
            self.tab_reservas,
            ("id", "cliente", "servicio", "unidades", "estado", "total"),
            ("Código", "Cliente", "Servicio", "Horas/días", "Estado", "Total")
        )

        acciones = tk.Frame(self.tab_reservas, bg="white")
        acciones.pack(fill="x", pady=10)
        self._boton(acciones, "Confirmar seleccionada",
                    self.confirmar_reserva, "#059669").pack(side="left", padx=(0, 8))
        self._boton(acciones, "Calcular costo",
                    self.calcular_costo, "#eb2525").pack(side="left", padx=8)
        self._boton(acciones, "Cancelar seleccionada",
                    self.cancelar_reserva, "#2629dc").pack(side="left", padx=8)

        tk.Label(
            self.tab_reservas,
            text="Para salas: indique número de personas. Para equipos: unidades. "
                 "Para asesorías: horas solicitadas.",
            bg="white", fg="#64748b", font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 0))

    def _crear_tab_logs(self):
        tk.Label(self.tab_logs, text="Eventos y errores del sistema",
                 bg="white", fg="#183153",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(self.tab_logs,
                 text="El detalle completo se almacena en el archivo logs.txt.",
                 bg="white", fg="#64748b").pack(anchor="w")
        self.log_text = tk.Text(
            self.tab_logs, height=22, wrap="word",
            font=("Consolas", 9), bg="#f8fafc", fg="#334155"
        )
        self.log_text.pack(fill="both", expand=True, pady=10)
        self._boton(self.tab_logs, "Actualizar registros",
                    self.actualizar_logs).pack(anchor="e")

    def _crear_tabla(self, padre, columnas, encabezados):
        marco = tk.Frame(padre, bg="white")
        marco.pack(fill="both", expand=True, pady=(5, 0))
        tree = ttk.Treeview(marco, columns=columnas, show="headings")
        for columna, titulo in zip(columnas, encabezados):
            tree.heading(columna, text=titulo)
            tree.column(columna, width=145, anchor="w")
        scroll = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _ejecutar_seguro(self, funcion):
        try:
            funcion()
        except (SoftwareFJException, ValueError, TypeError) as error:
            log_sistema.exception("Operación rechazada: %s", error)
            messagebox.showerror("No fue posible completar la operación", str(error))
        except Exception as error:
            log_sistema.exception("Error inesperado en interfaz: %s", error)
            messagebox.showerror(
                "Error inesperado",
                "Se presentó un problema. La aplicación continuará activa.\n"
                f"Detalle: {error}"
            )
        else:
            self._actualizar_todo()
        finally:
            log_sistema.info("Finalizó una operación desde la interfaz.")

    def registrar_cliente(self):
        def accion():
            cliente = Cliente(
                self.cli_id.get(), self.cli_nombre.get(),
                self.cli_correo.get(), self.cli_telefono.get()
            )
            self.sistema.registrar_cliente(cliente)
            for campo in (self.cli_id, self.cli_nombre,
                          self.cli_correo, self.cli_telefono):
                campo.delete(0, tk.END)
            messagebox.showinfo("Registro exitoso", "El cliente fue registrado.")
        self._ejecutar_seguro(accion)

    def registrar_servicio(self):
        def accion():
            codigo = self.srv_id.get().strip()
            nombre = self.srv_nombre.get().strip()
            tarifa = float(self.srv_tarifa.get())
            extra = self.srv_extra.get().strip()
            tipo = self.srv_tipo.get()

            if tipo == "Reserva de sala":
                servicio = ReservaSala(codigo, nombre, tarifa, int(extra))
            elif tipo == "Alquiler de equipo":
                servicio = AlquilerEquipo(codigo, nombre, tarifa, int(extra))
            else:
                servicio = AsesoriaEspecializada(codigo, nombre, tarifa, extra)

            self.sistema.registrar_servicio(servicio)
            for campo in (self.srv_id, self.srv_nombre,
                          self.srv_tarifa, self.srv_extra):
                campo.delete(0, tk.END)
            messagebox.showinfo("Registro exitoso", "El servicio fue registrado.")
        self._ejecutar_seguro(accion)

    def crear_reserva(self):
        def accion():
            if not self.res_cliente.get() or not self.res_servicio.get():
                raise ReservaInvalidaException("Seleccione un cliente y un servicio.")

            id_cliente = self.res_cliente.get().split(" | ")[0]
            id_servicio = self.res_servicio.get().split(" | ")[0]
            cliente = self.sistema.buscar_cliente(id_cliente)
            servicio = self.sistema.buscar_servicio(id_servicio)

            reserva = self.sistema.crear_reserva(
                self.res_id.get().strip(), cliente, servicio,
                float(self.res_unidades.get()),
                int(self.res_requerimiento.get())
            )
            self.res_id.delete(0, tk.END)
            self.res_unidades.delete(0, tk.END)
            self.res_requerimiento.delete(0, tk.END)
            messagebox.showinfo(
                "Reserva creada",
                f"La reserva {reserva.id_reserva} quedó pendiente de confirmación."
            )
        self._ejecutar_seguro(accion)

    def _reserva_seleccionada(self):
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            raise ReservaInvalidaException("Seleccione una reserva de la tabla.")
        codigo = self.tree_reservas.item(seleccion[0], "values")[0]
        return self.sistema.buscar_reserva(codigo)

    def confirmar_reserva(self):
        def accion():
            reserva = self._reserva_seleccionada()
            reserva.confirmar()
            messagebox.showinfo("Reserva confirmada",
                                f"La reserva {reserva.id_reserva} fue confirmada.")
        self._ejecutar_seguro(accion)

    def calcular_costo(self):
        def accion():
            reserva = self._reserva_seleccionada()
            descuento = simpledialog_float(
                self.root, "Descuento", "Ingrese el descuento (%)", 0.0
            )
            corporativo = messagebox.askyesno(
                "Tipo de cliente", "¿Es una reserva corporativa? (aplica 5% adicional)"
            )
            total = reserva.calcular_costo_total(
                porcentaje_descuento=descuento,
                impuesto_iva=0.19,
                es_corporativo=corporativo
            )
            messagebox.showinfo(
                "Costo de la reserva",
                f"Subtotal calculado con descuentos e IVA del 19%:\n${total:,.2f}"
            )
        self._ejecutar_seguro(accion)

    def cancelar_reserva(self):
        def accion():
            reserva = self._reserva_seleccionada()
            if not messagebox.askyesno(
                "Confirmar cancelación",
                f"¿Desea cancelar la reserva {reserva.id_reserva}?"
            ):
                return
            reserva.cancelar()
            messagebox.showinfo("Reserva cancelada", "La reserva fue cancelada.")
        self._ejecutar_seguro(accion)

    def _actualizar_todo(self):
        self._actualizar_clientes()
        self._actualizar_servicios()
        self._actualizar_reservas()
        self._actualizar_combos()
        self.lbl_clientes.config(text=str(len(self.sistema.clientes)))
        self.lbl_servicios.config(text=str(len(self.sistema.servicios)))
        self.lbl_reservas.config(text=str(len(self.sistema.reservas)))
        self.actualizar_logs()

    def _limpiar_tabla(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _actualizar_clientes(self):
        self._limpiar_tabla(self.tree_clientes)
        for c in self.sistema.clientes:
            self.tree_clientes.insert(
                "", "end",
                values=(c.id_entidad, c.nombre, c.correo, c.telefono)
            )

    def _actualizar_servicios(self):
        self._limpiar_tabla(self.tree_servicios)
        for s in self.sistema.servicios:
            if isinstance(s, ReservaSala):
                tipo, detalle = "Sala", f"{s.capacidad_maxima} personas"
            elif isinstance(s, AlquilerEquipo):
                tipo, detalle = "Equipo", f"{s.stock_disponible} unidades"
            else:
                tipo, detalle = "Asesoría", s.consultor
            self.tree_servicios.insert(
                "", "end",
                values=(s.id_entidad, tipo, s.nombre,
                        f"${s.tarifa_base:,.2f}", detalle)
            )

    def _actualizar_reservas(self):
        self._limpiar_tabla(self.tree_reservas)
        for r in self.sistema.reservas:
            self.tree_reservas.insert(
                "", "end",
                values=(r.id_reserva, r.cliente.nombre, r.servicio.nombre,
                        r.unidades, r.estado,
                        f"${r.costo_total:,.2f}" if r.costo_total else "Pendiente")
            )

    def _actualizar_combos(self):
        self.res_cliente["values"] = [
            f"{c.id_entidad} | {c.nombre}" for c in self.sistema.clientes
        ]
        self.res_servicio["values"] = [
            f"{s.id_entidad} | {s.nombre}" for s in self.sistema.servicios
        ]

    def actualizar_logs(self):
        if not hasattr(self, "log_text"):
            return
        self.log_text.delete("1.0", tk.END)
        try:
            with open("logs.txt", "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            self.log_text.insert(tk.END, contenido[-16000:] or "Todavía no hay eventos.")
        except FileNotFoundError:
            self.log_text.insert(tk.END, "El archivo logs.txt se creará al registrar eventos.")


def simpledialog_float(parent, titulo, mensaje, inicial=0.0):
    from tkinter import simpledialog
    valor = simpledialog.askfloat(
        titulo, mensaje, parent=parent, initialvalue=inicial,
        minvalue=0.0, maxvalue=100.0
    )
    if valor is None:
        raise OperacionNoPermitidaException("Operación cancelada por el usuario.")
    return valor

# 8. INICIO DE LA APLICACIÓN

if __name__ == "__main__":
    try:
        ventana = tk.Tk()
        aplicacion = AplicacionSoftwareFJ(ventana)
        ventana.mainloop()
    except Exception as error:
        log_sistema.exception("No fue posible iniciar la aplicación: %s", error)
        raise
    finally:
        log_sistema.info("Aplicación Software FJ cerrada.")

