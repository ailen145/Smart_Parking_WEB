from sqlalchemy import Column, Integer, String, DateTime, Date, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base_datos import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True)
    telefono = Column(String(15))
    email = Column(String(100), unique=True)
    direccion = Column(String(200))
    fecha_registro = Column(DateTime, server_default=func.now())
    tipo_usuario = Column(String(20))
    contrasena = Column(String(255))
    estado = Column(String(20))


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    placa = Column(String(20), unique=True, nullable=False)
    marca = Column(String(50))
    modelo = Column(String(50))
    color = Column(String(30))
    tipo_vehiculo = Column(String(20))
    anio = Column(Integer)


class Espacio(Base):
    __tablename__ = "espacios"
    id_espacio = Column(Integer, primary_key=True, index=True)
    numero_espacio = Column(String(10), unique=True, nullable=False)
    piso = Column(Integer, nullable=False)
    tipo_espacio = Column(String(20))
    estado = Column(String(20))
    tarifa_por_hora = Column(DECIMAL(10, 2))
    tarifa_por_dia = Column(DECIMAL(10, 2))
    tarifa_mensual = Column(DECIMAL(10, 2))


class TarjetaAcceso(Base):
    __tablename__ = "tarjetas_acceso"
    id_tarjeta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    numero_tarjeta = Column(String(20), unique=True, nullable=False)
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    estado = Column(String(20))
    saldo = Column(DECIMAL(10, 2))


class Registro(Base):
    __tablename__ = "registros"
    id_registro = Column(Integer, primary_key=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"))
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"))
    id_tarjeta = Column(Integer, ForeignKey("tarjetas_acceso.id_tarjeta"), nullable=True)
    id_operador = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha_ingreso = Column(DateTime)
    fecha_salida = Column(DateTime)
    metodo_pago = Column(String(30))
    estado = Column(String(20))


class Pago(Base):
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True)
    id_registro = Column(Integer, ForeignKey("registros.id_registro"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    monto = Column(DECIMAL(10, 2))
    fecha_pago = Column(DateTime, server_default=func.now())
    metodo_pago = Column(String(30))
    comprobante = Column(String(100))
    estado = Column(String(20))


class Puesto(Base):
    __tablename__ = "puestos"
    id_puesto = Column(Integer, primary_key=True, index=True)
    nombre_puesto = Column(String(20))
    salario_base = Column(DECIMAL(10, 2))


class Personal(Base):
    __tablename__ = "personal"
    id_personal = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True)
    id_puesto = Column(Integer, ForeignKey("puestos.id_puesto"))
    turno = Column(String(20))
    fecha_contratacion = Column(Date)


class Mantenimiento(Base):
    __tablename__ = "mantenimiento"
    id_mantenimiento = Column(Integer, primary_key=True, index=True)
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"))
    id_personal = Column(Integer, ForeignKey("personal.id_personal"))
    tipo_mantenimiento = Column(String(20))
    descripcion = Column(Text)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    estado = Column(String(20))
    costo = Column(DECIMAL(10, 2))


class Reserva(Base):
    __tablename__ = "reservas"
    id_reserva = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"))
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"), nullable=True)
    fecha_reserva = Column(DateTime)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    estado = Column(String(20))
    monto_pagado = Column(DECIMAL(10, 2))

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    espacio = relationship("Espacio", foreign_keys=[id_espacio])
    vehiculo = relationship("Vehiculo", foreign_keys=[id_vehiculo])


class TipoReporte(Base):
    __tablename__ = "tipos_reporte"
    id_tipo_reporte = Column(Integer, primary_key=True, index=True)
    nombre_tipo = Column(String(20))
    descripcion = Column(String(100))


class Reporte(Base):
    __tablename__ = "reportes"
    id_reporte = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"))
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"))
    id_tipo_reporte = Column(Integer, ForeignKey("tipos_reporte.id_tipo_reporte"))
    descripcion = Column(Text)
    fecha_reporte = Column(DateTime, server_default=func.now())
    estado = Column(String(30))
    evidencia = Column(String(255))