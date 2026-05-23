from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.base_datos import get_db
from app.modelos.modelos import Espacio, Reserva

router = APIRouter()


@router.get("/nueva/{espacio_id}")
async def mostrar_reserva(request: Request, espacio_id: int, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    espacio = db.query(Espacio).filter(Espacio.id_espacio == espacio_id).first()
    if not espacio or espacio.estado != "disponible":
        return RedirectResponse(url="/dashboard", status_code=303)

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="reserva.html",
        context={"espacio": espacio}
    )


@router.post("/nueva/{espacio_id}")
async def crear_reserva(
    request: Request,
    espacio_id: int,
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    espacio = db.query(Espacio).filter(Espacio.id_espacio == espacio_id).first()
    if not espacio or espacio.estado != "disponible":
        return RedirectResponse(url="/dashboard", status_code=303)

    try:
        inicio = datetime.fromisoformat(fecha_inicio)
        fin = datetime.fromisoformat(fecha_fin)
    except ValueError:
        return RedirectResponse(url="/dashboard", status_code=303)

    if fin <= inicio:
        return request.app.state.plantillas.TemplateResponse(
            request=request,
            name="reserva.html",
            context={"espacio": espacio, "error": "La fecha de fin debe ser mayor a la de inicio"}
        )

    horas = (fin - inicio).total_seconds() / 3600
    monto = round(float(espacio.tarifa_por_hora or 3.0) * horas, 2)

    nueva_reserva = Reserva(
        id_usuario=int(usuario_id),
        id_espacio=espacio_id,
        fecha_reserva=datetime.now(),
        fecha_inicio=inicio,
        fecha_fin=fin,
        estado="activa",
        monto_pagado=monto
    )
    db.add(nueva_reserva)
    espacio.estado = "reservado"
    db.commit()

    return RedirectResponse(url="/reservas/mis-reservas?exito=1", status_code=303)


@router.get("/mis-reservas")
async def mis_reservas(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    reservas = db.query(Reserva).filter(
        Reserva.id_usuario == int(usuario_id)
    ).order_by(Reserva.fecha_reserva.desc()).all()

    for r in reservas:
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()

    exito = request.query_params.get("exito")
    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="mis_reservas.html",
        context={
            "reservas": reservas,
            "usuario_nombre": request.cookies.get("usuario_nombre", "Usuario"),
            "exito": exito
        }
    )


@router.post("/cancelar/{reserva_id}")
async def cancelar_reserva(request: Request, reserva_id: int, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    reserva = db.query(Reserva).filter(
        Reserva.id_reserva == reserva_id,
        Reserva.id_usuario == int(usuario_id)
    ).first()

    if reserva and reserva.estado == "activa":
        reserva.estado = "cancelada"
        espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio).first()
        if espacio:
            espacio.estado = "disponible"
        db.commit()

    return RedirectResponse(url="/reservas/mis-reservas", status_code=303)