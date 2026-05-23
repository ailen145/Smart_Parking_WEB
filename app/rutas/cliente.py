from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.base_datos import get_db
from app.modelos.modelos import Usuario, Espacio, Reserva, Vehiculo

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_cliente(request: Request):
    return request.cookies.get("usuario_id") is not None


# ====================== DASHBOARD CLIENTE ======================

@router.get("/dashboard")
async def cliente_dashboard(request: Request, db: Session = Depends(get_db)):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

    # Espacios disponibles
    espacios = db.query(Espacio).order_by(Espacio.piso, Espacio.numero_espacio).all()
    total = len(espacios)
    disponibles = sum(1 for e in espacios if e.estado == "disponible")
    ocupados = sum(1 for e in espacios if e.estado == "ocupado")
    reservados = sum(1 for e in espacios if e.estado == "reservado")
    mantenimiento = sum(1 for e in espacios if e.estado == "mantenimiento")

    pisos = {}
    for e in espacios:
        pisos.setdefault(e.piso, []).append(e)

    # Mis reservas activas
    mis_reservas = db.query(Reserva).filter(
        Reserva.id_usuario == usuario_id,
        Reserva.estado == "activa"
    ).order_by(Reserva.fecha_inicio).all()

    for r in mis_reservas:
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()

    # Mis vehículos
    mis_vehiculos = db.query(Vehiculo).filter(Vehiculo.id_usuario == usuario_id).all()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="cliente_dashboard.html",
        context={
            "usuario": usuario,
            "usuario_nombre": request.cookies.get("usuario_nombre", "Usuario"),
            "pisos": pisos,
            "total": total,
            "disponibles": disponibles,
            "ocupados": ocupados,
            "reservados": reservados,
            "mantenimiento": mantenimiento,
            "mis_reservas": mis_reservas,
            "mis_vehiculos": mis_vehiculos,
        }
    )


# ====================== PERFIL ======================

@router.get("/perfil")
async def ver_perfil(request: Request, db: Session = Depends(get_db)):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="cliente_perfil.html",
        context={
            "usuario": usuario,
            "usuario_nombre": request.cookies.get("usuario_nombre", "Usuario"),
            "exito": request.query_params.get("exito"),
            "error": request.query_params.get("error"),
        }
    )


@router.post("/perfil/editar")
async def editar_perfil(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(""),
    db: Session = Depends(get_db)
):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

    if not telefono.isdigit() or len(telefono) != 9:
        return RedirectResponse(url="/cliente/perfil?error=El+teléfono+debe+tener+9+dígitos", status_code=303)

    if usuario:
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.telefono = telefono
        usuario.direccion = direccion
        db.commit()

        # Actualizar cookie con nuevo nombre
        response = RedirectResponse(url="/cliente/perfil?exito=Perfil+actualizado+correctamente", status_code=303)
        response.set_cookie(key="usuario_nombre", value=f"{nombre} {apellido}", httponly=True, max_age=3600)
        return response

    return RedirectResponse(url="/cliente/perfil?error=Error+al+actualizar", status_code=303)


@router.post("/perfil/cambiar-password")
async def cambiar_password(
    request: Request,
    password_actual: str = Form(...),
    nueva_password: str = Form(...),
    confirmar_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

    if not pwd_context.verify(password_actual, usuario.contrasena):
        return RedirectResponse(url="/cliente/perfil?error=Contraseña+actual+incorrecta", status_code=303)

    if nueva_password != confirmar_password:
        return RedirectResponse(url="/cliente/perfil?error=Las+contraseñas+no+coinciden", status_code=303)

    if len(nueva_password) < 8:
        return RedirectResponse(url="/cliente/perfil?error=La+contraseña+debe+tener+mínimo+8+caracteres", status_code=303)

    usuario.contrasena = pwd_context.hash(nueva_password)
    db.commit()
    return RedirectResponse(url="/cliente/perfil?exito=Contraseña+cambiada+correctamente", status_code=303)


# ====================== VEHÍCULOS ======================

@router.get("/vehiculos")
async def ver_vehiculos(request: Request, db: Session = Depends(get_db)):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    vehiculos = db.query(Vehiculo).filter(Vehiculo.id_usuario == usuario_id).all()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="cliente_vehiculos.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Usuario"),
            "vehiculos": vehiculos,
            "exito": request.query_params.get("exito"),
            "error": request.query_params.get("error"),
        }
    )


@router.post("/vehiculos/agregar")
async def agregar_vehiculo(
    request: Request,
    placa: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    color: str = Form(...),
    tipo_vehiculo: str = Form(...),
    anio: int = Form(...),
    db: Session = Depends(get_db)
):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))

    existente = db.query(Vehiculo).filter(Vehiculo.placa == placa.upper()).first()
    if existente:
        return RedirectResponse(url="/cliente/vehiculos?error=Esta+placa+ya+está+registrada", status_code=303)

    nuevo = Vehiculo(
        id_usuario=usuario_id,
        placa=placa.upper(),
        marca=marca,
        modelo=modelo,
        color=color,
        tipo_vehiculo=tipo_vehiculo,
        anio=anio
    )
    db.add(nuevo)
    db.commit()
    return RedirectResponse(url="/cliente/vehiculos?exito=Vehículo+registrado+correctamente", status_code=303)


@router.post("/vehiculos/editar/{vehiculo_id}")
async def editar_vehiculo(
    request: Request,
    vehiculo_id: int,
    placa: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    color: str = Form(...),
    tipo_vehiculo: str = Form(...),
    anio: int = Form(...),
    db: Session = Depends(get_db)
):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id_vehiculo == vehiculo_id,
        Vehiculo.id_usuario == usuario_id
    ).first()

    if vehiculo:
        vehiculo.placa = placa.upper()
        vehiculo.marca = marca
        vehiculo.modelo = modelo
        vehiculo.color = color
        vehiculo.tipo_vehiculo = tipo_vehiculo
        vehiculo.anio = anio
        db.commit()

    return RedirectResponse(url="/cliente/vehiculos?exito=Vehículo+actualizado+correctamente", status_code=303)


@router.post("/vehiculos/eliminar/{vehiculo_id}")
async def eliminar_vehiculo(request: Request, vehiculo_id: int, db: Session = Depends(get_db)):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id_vehiculo == vehiculo_id,
        Vehiculo.id_usuario == usuario_id
    ).first()

    if vehiculo:
        db.delete(vehiculo)
        db.commit()

    return RedirectResponse(url="/cliente/vehiculos?exito=Vehículo+eliminado+correctamente", status_code=303)


# ====================== MIS RESERVAS ======================

@router.get("/reservas")
async def mis_reservas_cliente(request: Request, db: Session = Depends(get_db)):
    if not verificar_cliente(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))
    reservas = db.query(Reserva).filter(
        Reserva.id_usuario == usuario_id
    ).order_by(Reserva.fecha_reserva.desc()).all()

    for r in reservas:
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()

    activas = sum(1 for r in reservas if r.estado == "activa")
    canceladas = sum(1 for r in reservas if r.estado == "cancelada")
    total_gastado = sum(float(r.monto_pagado or 0) for r in reservas if r.estado == "activa")

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="mis_reservas.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Usuario"),
            "reservas": reservas,
            "activas": activas,
            "canceladas": canceladas,
            "total_gastado": total_gastado,
            "exito": request.query_params.get("exito"),
        }
    )