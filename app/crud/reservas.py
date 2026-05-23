from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Date
from datetime import datetime
from typing import Optional

from app.modelos.modelos import Reserva, Espacio, Vehiculo, Usuario


def obtener_espacios_disponibles(db: Session, fecha_inicio: datetime, fecha_fin: datetime) -> list:
    reservados_ids = (
        db.query(Reserva.id_espacio)
        .filter(
            Reserva.estado.notin_(["Cancelada", "Finalizada"]),
            Reserva.fecha_inicio < fecha_fin,
            Reserva.fecha_fin > fecha_inicio,
        )
        .subquery()
    )
    return (
        db.query(Espacio)
        .filter(
            Espacio.estado == "disponible",
            Espacio.id_espacio.notin_(reservados_ids),
        )
        .order_by(Espacio.piso, Espacio.numero_espacio)
        .all()
    )


def obtener_espacio_por_id(db: Session, id_espacio: int) -> Optional[Espacio]:
    return db.query(Espacio).filter(Espacio.id_espacio == id_espacio).first()


def obtener_vehiculos_usuario(db: Session, id_usuario: int) -> list:
    return (
        db.query(Vehiculo)
        .filter(Vehiculo.id_usuario == id_usuario)
        .all()
    )


def _calcular_monto(tarifa_hora: float, inicio: datetime, fin: datetime) -> float:
    horas = max(1, (fin - inicio).total_seconds() / 3600)
    return round(tarifa_hora * horas, 2)


def crear_reserva(
    db: Session,
    id_usuario: int,
    id_espacio: int,
    id_vehiculo: int,
    fecha_inicio: datetime,
    fecha_fin: datetime,
) -> Reserva:
    espacio = obtener_espacio_por_id(db, id_espacio)
    if not espacio:
        raise ValueError("El espacio no existe.")

    monto = _calcular_monto(float(espacio.tarifa_por_hora or 0), fecha_inicio, fecha_fin)

    reserva = Reserva(
        id_usuario=id_usuario,
        id_espacio=id_espacio,
        id_vehiculo=id_vehiculo,
        fecha_reserva=datetime.now(),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="Pendiente",
        monto_pagado=monto,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def obtener_reservas_usuario(db: Session, id_usuario: int) -> list:
    return (
        db.query(Reserva)
        .options(
            joinedload(Reserva.espacio),
            joinedload(Reserva.vehiculo),
        )
        .filter(Reserva.id_usuario == id_usuario)
        .order_by(Reserva.fecha_inicio.desc())
        .all()
    )


def obtener_todas_reservas(
    db: Session,
    estado: Optional[str] = None,
    fecha: Optional[str] = None,
) -> list:
    q = (
        db.query(Reserva)
        .options(
            joinedload(Reserva.espacio),
            joinedload(Reserva.vehiculo),
            joinedload(Reserva.usuario),
        )
    )
    if estado:
        q = q.filter(Reserva.estado == estado)
    if fecha:
        q = q.filter(cast(Reserva.fecha_inicio, Date) == fecha)
    return q.order_by(Reserva.fecha_inicio.desc()).all()


def obtener_reserva_por_id(db: Session, id_reserva: int) -> Optional[Reserva]:
    return (
        db.query(Reserva)
        .options(
            joinedload(Reserva.espacio),
            joinedload(Reserva.vehiculo),
            joinedload(Reserva.usuario),
        )
        .filter(Reserva.id_reserva == id_reserva)
        .first()
    )


def cancelar_reserva(db: Session, id_reserva: int, id_usuario: int, es_admin=False) -> bool:
    q = db.query(Reserva).filter(Reserva.id_reserva == id_reserva)
    if es_admin:
        q = q.filter(Reserva.estado.notin_(["Finalizada", "Cancelada"]))
    else:
        q = q.filter(Reserva.id_usuario == id_usuario, Reserva.estado == "Pendiente")
    reserva = q.first()
    if not reserva:
        return False
    reserva.estado = "Cancelada"
    db.commit()
    return True


def confirmar_reserva(db: Session, id_reserva: int) -> bool:
    reserva = db.query(Reserva).filter(
        Reserva.id_reserva == id_reserva,
        Reserva.estado == "Pendiente"
    ).first()
    if not reserva:
        return False
    reserva.estado = "Confirmada"
    db.commit()
    return True


def finalizar_reserva(db: Session, id_reserva: int) -> bool:
    reserva = db.query(Reserva).filter(
        Reserva.id_reserva == id_reserva,
        Reserva.estado == "Confirmada"
    ).first()
    if not reserva:
        return False
    reserva.estado = "Finalizada"
    db.commit()
    return True


def stats_reservas_hoy(db: Session) -> dict:
    hoy = datetime.now().date()
    reservas = db.query(Reserva).filter(
        cast(Reserva.fecha_reserva, Date) == hoy
    ).all()
    return {
        "total":       len(reservas),
        "confirmadas": sum(1 for r in reservas if r.estado == "Confirmada"),
        "pendientes":  sum(1 for r in reservas if r.estado == "Pendiente"),
        "canceladas":  sum(1 for r in reservas if r.estado == "Cancelada"),
        "ingresos":    sum(float(r.monto_pagado or 0) for r in reservas if r.estado != "Cancelada"),
    }