from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from app.modelos.modelos import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def obtener_todos(db: Session) -> list:
    return db.query(Usuario).order_by(Usuario.fecha_registro.desc()).all()


def obtener_por_id(db: Session, id_usuario: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()


def obtener_por_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email).first()


def crear(db: Session, datos: dict) -> Usuario:
    usuario = Usuario(
        nombre       = datos["nombre"].strip(),
        apellido     = datos["apellido"].strip(),
        dni          = datos.get("dni", "").strip() or None,
        telefono     = datos.get("telefono", "").strip() or None,
        email        = datos["email"].strip().lower(),
        direccion    = datos.get("direccion", "").strip() or None,
        tipo_usuario = datos.get("tipo_usuario", "Cliente"),
        estado       = datos.get("estado", "activo"),
        contrasena   = pwd_context.hash(datos["contrasena"]),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar(db: Session, id_usuario: int, datos: dict) -> Optional[Usuario]:
    usuario = obtener_por_id(db, id_usuario)
    if not usuario:
        return None
    usuario.nombre       = datos["nombre"].strip()
    usuario.apellido     = datos["apellido"].strip()
    usuario.dni          = datos.get("dni", "").strip() or None
    usuario.telefono     = datos.get("telefono", "").strip() or None
    usuario.email        = datos["email"].strip().lower()
    usuario.direccion    = datos.get("direccion", "").strip() or None
    usuario.tipo_usuario = datos["tipo_usuario"]
    usuario.estado       = datos["estado"]
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_contrasena(db: Session, id_usuario: int, nueva: str) -> bool:
    usuario = obtener_por_id(db, id_usuario)
    if not usuario:
        return False
    usuario.contrasena = pwd_context.hash(nueva)
    db.commit()
    return True


def cambiar_estado(db: Session, id_usuario: int, nuevo_estado: str) -> bool:
    usuario = obtener_por_id(db, id_usuario)
    if not usuario:
        return False
    usuario.estado = nuevo_estado
    db.commit()
    return True


def eliminar(db: Session, id_usuario: int) -> bool:
    usuario = obtener_por_id(db, id_usuario)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True


def stats(db: Session) -> dict:
    usuarios = db.query(Usuario).all()
    return {
        "total":     len(usuarios),
        "activos":   sum(1 for u in usuarios if u.estado == "activo"),
        "inactivos": sum(1 for u in usuarios if u.estado == "inactivo"),
        "clientes":  sum(1 for u in usuarios if u.tipo_usuario == "Cliente"),
        "personal":  sum(1 for u in usuarios if u.tipo_usuario == "Personal"),
        "admins":    sum(1 for u in usuarios if u.tipo_usuario == "Admin"),
    }