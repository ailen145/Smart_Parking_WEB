from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class ReservaCreate(BaseModel):
    id_espacio:  int
    id_vehiculo: int
    fecha_inicio: datetime
    fecha_fin:    datetime

    @field_validator("fecha_fin")
    @classmethod
    def validar_fechas(cls, v, info):
        if "fecha_inicio" in info.data and v <= info.data["fecha_inicio"]:
            raise ValueError("La fecha de fin debe ser posterior a la de inicio.")
        return v


class ReservaOut(BaseModel):
    id_reserva:      int
    id_usuario:      int
    id_espacio:      int
    id_vehiculo:     int
    fecha_reserva:   datetime
    fecha_inicio:    datetime
    fecha_fin:       datetime
    estado:          str
    monto_pagado:    float
    nombre_usuario:  Optional[str] = None
    apellido_usuario:Optional[str] = None
    placa_vehiculo:  Optional[str] = None
    numero_espacio:  Optional[str] = None
    piso:            Optional[int] = None
    tipo_espacio:    Optional[str] = None

    class Config:
        from_attributes = True