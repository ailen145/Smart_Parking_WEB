from sqlalchemy.orm import Session
from typing import Optional
from app.modelos.modelos import Espacio


def obtener_todos(db: Session) -> list:
    return db.query(Espacio).order_by(Espacio.piso, Espacio.numero_espacio).all()


def obtener_por_id(db: Session, id_espacio: int) -> Optional[Espacio]:
    return db.query(Espacio).filter(Espacio.id_espacio == id_espacio).first()


def obtener_por_piso(db: Session, piso: int) -> list:
    return (
        db.query(Espacio)
        .filter(Espacio.piso == piso)
        .order_by(Espacio.numero_espacio)
        .all()
    )


def crear(db: Session, datos: dict) -> Espacio:
    espacio = Espacio(
        numero_espacio  = datos["numero_espacio"].upper().strip(),
        piso            = datos["piso"],
        tipo_espacio    = datos["tipo_espacio"],
        estado          = datos.get("estado", "disponible"),
        tarifa_por_hora = datos.get("tarifa_por_hora") or None,
        tarifa_por_dia  = datos.get("tarifa_por_dia")  or None,
        tarifa_mensual  = datos.get("tarifa_mensual")  or None,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def actualizar(db: Session, id_espacio: int, datos: dict) -> Optional[Espacio]:
    espacio = obtener_por_id(db, id_espacio)
    if not espacio:
        return None
    espacio.numero_espacio  = datos["numero_espacio"].upper().strip()
    espacio.piso            = datos["piso"]
    espacio.tipo_espacio    = datos["tipo_espacio"]
    espacio.estado          = datos["estado"]
    espacio.tarifa_por_hora = datos.get("tarifa_por_hora") or None
    espacio.tarifa_por_dia  = datos.get("tarifa_por_dia")  or None
    espacio.tarifa_mensual  = datos.get("tarifa_mensual")  or None
    db.commit()
    db.refresh(espacio)
    return espacio


def cambiar_estado(db: Session, id_espacio: int, nuevo_estado: str) -> bool:
    espacio = obtener_por_id(db, id_espacio)
    if not espacio:
        return False
    espacio.estado = nuevo_estado
    db.commit()
    return True


def eliminar(db: Session, id_espacio: int) -> bool:
    espacio = obtener_por_id(db, id_espacio)
    if not espacio:
        return False
    db.delete(espacio)
    db.commit()
    return True


def stats(db: Session) -> dict:
    espacios = db.query(Espacio).all()
    total = len(espacios)
    return {
        "total":          total,
        "disponibles":    sum(1 for e in espacios if e.estado == "disponible"),
        "ocupados":       sum(1 for e in espacios if e.estado == "ocupado"),
        "reservados":     sum(1 for e in espacios if e.estado == "reservado"),
        "mantenimiento":  sum(1 for e in espacios if e.estado == "mantenimiento"),
        "pisos":          sorted(set(e.piso for e in espacios)),
        "tipos":          sorted(set(e.tipo_espacio for e in espacios if e.tipo_espacio)),
    }