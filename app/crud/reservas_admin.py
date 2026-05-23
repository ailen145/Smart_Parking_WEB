from sqlalchemy.orm import Session
from sqlalchemy import cast, Date
from datetime import datetime
from typing import Optional

from app.modelos.modelos import Reserva, Espacio, Vehiculo, Usuario


def _enriquecer(db: Session, reservas):
    for r in reservas:
        if not hasattr(r, 'usuario') or r.usuario is None:
            r.usuario = db.query(Usuario).filter(Usuario.id_usuario == r.id_usuario).first()
        if not hasattr(r, 'espacio') or r.espacio is None:
            r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()
        if r.id_vehiculo and (not hasattr(r, 'vehiculo') or r.vehiculo is None):
            r.vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == r.id_vehiculo).first()
        else:
            if not hasattr(r, 'vehiculo'):
                r.vehiculo = None


def obtener_todas(
    db: Session,
    estado: Optional[str] = None,
    fecha: Optional[str] = None,
    buscar: Optional[str] = None,
) -> list:
    q = db.query(Reserva)

    if estado and estado != "todos":
        q = q.filter(Reserva.estado == estado)

    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            q = q.filter(Reserva.fecha_reserva >= fecha_dt)
        except ValueError:
            pass

    if buscar:
        usuarios = db.query(Usuario).filter(
            (Usuario.nombre.ilike(f"%{buscar}%")) |
            (Usuario.apellido.ilike(f"%{buscar}%")) |
            (Usuario.email.ilike(f"%{buscar}%"))
        ).all()
        ids = [u.id_usuario for u in usuarios]
        if ids:
            q = q.filter(Reserva.id_usuario.in_(ids))
        else:
            return []

    reservas = q.order_by(Reserva.fecha_reserva.desc()).all()
    _enriquecer(db, reservas)
    return reservas


def obtener_por_id(db: Session, id_reserva: int) -> Optional[Reserva]:
    reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
    if reserva:
        _enriquecer(db, [reserva])
    return reserva


def otras_reservas_usuario(db: Session, id_usuario: int, excluir_id: int) -> list:
    reservas = db.query(Reserva).filter(
        Reserva.id_usuario == id_usuario,
        Reserva.id_reserva != excluir_id
    ).order_by(Reserva.fecha_reserva.desc()).limit(5).all()
    _enriquecer(db, reservas)
    return reservas


def cambiar_estado(db: Session, id_reserva: int, nuevo_estado: str) -> bool:
    reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
    if not reserva:
        return False
    reserva.estado = nuevo_estado
    if nuevo_estado in ["cancelada", "completada"]:
        espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio).first()
        if espacio:
            espacio.estado = "disponible"
    db.commit()
    return True


def cancelar(db: Session, id_reserva: int) -> bool:
    return cambiar_estado(db, id_reserva, "cancelada")


def cancelar_reserva(db: Session, id_reserva: int, id_usuario: int, es_admin=False) -> bool:
    q = db.query(Reserva).filter(Reserva.id_reserva == id_reserva)
    if not es_admin:
        q = q.filter(Reserva.id_usuario == id_usuario)
    reserva = q.first()
    if not reserva:
        return False
    reserva.estado = "cancelada"
    espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio).first()
    if espacio:
        espacio.estado = "disponible"
    db.commit()
    return True


def stats(db: Session) -> dict:
    todas = db.query(Reserva).all()
    hoy = datetime.now().date()
    reservas_hoy = [
        r for r in todas
        if r.fecha_reserva and r.fecha_reserva.date() == hoy
    ]
    return {
        "total":        len(todas),
        "activas":      sum(1 for r in todas if r.estado == "activa"),
        "canceladas":   sum(1 for r in todas if r.estado == "cancelada"),
        "pendientes":   sum(1 for r in todas if r.estado == "pendiente"),
        "hoy":          len(reservas_hoy),
        "ingresos":     sum(           # ← clave corregida (era "ingresos_totales")
            float(r.monto_pagado or 0)
            for r in todas
            if r.estado in ("activa", "completada")
        ),
        "ingresos_hoy": sum(
            float(r.monto_pagado or 0)
            for r in reservas_hoy
            if r.estado in ("activa", "completada")
        ),
    }


def crear_reserva(
    db: Session,
    id_usuario: int,
    id_espacio: int,
    id_vehiculo: Optional[int],
    fecha_inicio: datetime,
    fecha_fin: datetime,
) -> Reserva:
    espacio = db.query(Espacio).filter(Espacio.id_espacio == id_espacio).first()
    if not espacio:
        raise ValueError("El espacio no existe.")

    horas = max(1, (fecha_fin - fecha_inicio).total_seconds() / 3600)
    monto = round(float(espacio.tarifa_por_hora or 0) * horas, 2)

    reserva = Reserva(
        id_usuario=id_usuario,
        id_espacio=id_espacio,
        id_vehiculo=id_vehiculo,
        fecha_reserva=datetime.now(),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="activa",
        monto_pagado=monto,
    )
    db.add(reserva)
    espacio.estado = "reservado"
    db.commit()
    db.refresh(reserva)
    return reserva