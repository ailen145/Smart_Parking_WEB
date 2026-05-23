from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.base_datos import get_db
from app.modelos.modelos import Reserva, Espacio, Usuario
from app.crud import reservas_admin as crud_reservas

router = APIRouter()


def verificar_admin(request: Request):
    return request.cookies.get("usuario_rol") == "admin"


@router.get("")
async def listar_reservas(
    request: Request,
    estado: str = None,
    fecha: str = None,
    buscar: str = None,
    db: Session = Depends(get_db)
):
    if not verificar_admin(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    reservas = crud_reservas.obtener_todas(db, estado, fecha, buscar)

    total = len(reservas)
    activas = sum(1 for r in reservas if r.estado == "activa")
    canceladas = sum(1 for r in reservas if r.estado == "cancelada")
    ingresos = sum(float(r.monto_pagado or 0) for r in reservas if r.estado == "activa")

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="admin_reservas.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Admin"),
            "reservas": reservas,
            "total": total,
            "activas": activas,
            "canceladas": canceladas,
            "ingresos": ingresos,
            "estado_filtro": estado or "todos",
            "fecha_filtro": fecha or "",
            "buscar_filtro": buscar or "",
            "exito": request.query_params.get("exito"),
        }
    )


@router.post("/cancelar/{reserva_id}")
async def cancelar_reserva(request: Request, reserva_id: int, db: Session = Depends(get_db)):
    if not verificar_admin(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    reserva = db.query(Reserva).filter(Reserva.id_reserva == reserva_id).first()
    if reserva and reserva.estado == "activa":
        reserva.estado = "cancelada"
        espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio).first()
        if espacio:
            espacio.estado = "disponible"
        db.commit()

    return RedirectResponse(url="/admin/reservas?exito=Reserva+cancelada+correctamente", status_code=303)