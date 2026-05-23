from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.base_datos import get_db
from app.modelos.modelos import Usuario, Espacio, Reserva, Vehiculo, Registro

router = APIRouter()


def verificar_personal(request: Request):
    return request.cookies.get("usuario_rol") == "personal"


# ====================== DASHBOARD PERSONAL ======================

@router.get("/dashboard")
async def personal_dashboard(request: Request, db: Session = Depends(get_db)):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    # Espacios
    espacios = db.query(Espacio).order_by(Espacio.piso, Espacio.numero_espacio).all()
    total = len(espacios)
    disponibles = sum(1 for e in espacios if e.estado == "disponible")
    ocupados = sum(1 for e in espacios if e.estado == "ocupado")
    reservados = sum(1 for e in espacios if e.estado == "reservado")
    mantenimiento = sum(1 for e in espacios if e.estado == "mantenimiento")

    pisos = {}
    for e in espacios:
        pisos.setdefault(e.piso, []).append(e)

    # Vehículos actualmente estacionados (registros sin salida)
    vehiculos_activos = db.query(Registro).filter(
        Registro.fecha_salida == None,
        Registro.estado == "activo"
    ).all()
    for r in vehiculos_activos:
        r.vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == r.id_vehiculo).first()
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()

    # Reservas próximas (activas)
    reservas_proximas = db.query(Reserva).filter(
        Reserva.estado == "activa"
    ).order_by(Reserva.fecha_inicio).limit(5).all()
    for r in reservas_proximas:
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()
        r.usuario = db.query(Usuario).filter(Usuario.id_usuario == r.id_usuario).first()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="personal_dashboard.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Personal"),
            "pisos": pisos,
            "total": total,
            "disponibles": disponibles,
            "ocupados": ocupados,
            "reservados": reservados,
            "mantenimiento": mantenimiento,
            "vehiculos_activos": vehiculos_activos,
            "reservas_proximas": reservas_proximas,
            "exito": request.query_params.get("exito"),
            "error": request.query_params.get("error"),
        }
    )


# ====================== REGISTRO DE INGRESO ======================

@router.get("/ingreso")
async def mostrar_ingreso(request: Request, db: Session = Depends(get_db)):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    espacios_disponibles = db.query(Espacio).filter(
        Espacio.estado == "disponible"
    ).order_by(Espacio.piso, Espacio.numero_espacio).all()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="personal_ingreso.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Personal"),
            "espacios_disponibles": espacios_disponibles,
            "exito": request.query_params.get("exito"),
            "error": request.query_params.get("error"),
        }
    )


@router.post("/ingreso/registrar")
async def registrar_ingreso(
    request: Request,
    placa: str = Form(...),
    id_espacio: int = Form(...),
    metodo_pago: str = Form("efectivo"),
    db: Session = Depends(get_db)
):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    usuario_id = int(request.cookies.get("usuario_id"))

    # Buscar o crear vehículo por placa
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa.upper()).first()
    if not vehiculo:
        return RedirectResponse(url="/personal/ingreso?error=Placa+no+encontrada+en+el+sistema", status_code=303)

    # Verificar espacio disponible
    espacio = db.query(Espacio).filter(Espacio.id_espacio == id_espacio).first()
    if not espacio or espacio.estado != "disponible":
        return RedirectResponse(url="/personal/ingreso?error=El+espacio+no+está+disponible", status_code=303)

    # Crear registro
    nuevo_registro = Registro(
        id_vehiculo=vehiculo.id_vehiculo,
        id_espacio=id_espacio,
        id_operador=usuario_id,
        fecha_ingreso=datetime.now(),
        metodo_pago=metodo_pago,
        estado="activo"
    )
    db.add(nuevo_registro)

    # Cambiar estado del espacio
    espacio.estado = "ocupado"
    db.commit()

    return RedirectResponse(url="/personal/dashboard?exito=Ingreso+registrado+correctamente", status_code=303)


# ====================== REGISTRO DE SALIDA ======================

@router.get("/salida")
async def mostrar_salida(request: Request, db: Session = Depends(get_db)):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    # Vehículos estacionados actualmente
    registros_activos = db.query(Registro).filter(
        Registro.fecha_salida == None,
        Registro.estado == "activo"
    ).order_by(Registro.fecha_ingreso.desc()).all()

    for r in registros_activos:
        r.vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == r.id_vehiculo).first()
        r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()
        if r.vehiculo:
            r.usuario = db.query(Usuario).filter(
                Usuario.id_usuario == r.vehiculo.id_usuario
            ).first()
        # Calcular tiempo estacionado
        if r.fecha_ingreso:
            diff = datetime.now() - r.fecha_ingreso
            horas = diff.total_seconds() / 3600
            r.horas_estacionado = round(horas, 1)
            if r.espacio:
                r.monto_calcualado = round(float(r.espacio.tarifa_por_hora or 3.0) * horas, 2)
            else:
                r.monto_calcualado = 0
        else:
            r.horas_estacionado = 0
            r.monto_calcualado = 0

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="personal_salida.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Personal"),
            "registros_activos": registros_activos,
            "exito": request.query_params.get("exito"),
            "error": request.query_params.get("error"),
        }
    )


@router.post("/salida/registrar/{registro_id}")
async def registrar_salida(
    request: Request,
    registro_id: int,
    db: Session = Depends(get_db)
):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    registro = db.query(Registro).filter(Registro.id_registro == registro_id).first()
    if not registro:
        return RedirectResponse(url="/personal/salida?error=Registro+no+encontrado", status_code=303)

    fecha_salida = datetime.now()
    registro.fecha_salida = fecha_salida
    registro.estado = "completado"

    # Liberar espacio
    espacio = db.query(Espacio).filter(Espacio.id_espacio == registro.id_espacio).first()
    if espacio:
        espacio.estado = "disponible"

    db.commit()
    return RedirectResponse(url="/personal/salida?exito=Salida+registrada+correctamente", status_code=303)


# ====================== BÚSQUEDA POR PLACA ======================

@router.get("/buscar-placa")
async def buscar_placa(request: Request, db: Session = Depends(get_db)):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    placa = request.query_params.get("placa", "").upper()
    vehiculo = None
    historial = []
    registro_activo = None

    if placa:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
        if vehiculo:
            historial = db.query(Registro).filter(
                Registro.id_vehiculo == vehiculo.id_vehiculo
            ).order_by(Registro.fecha_ingreso.desc()).limit(10).all()

            for r in historial:
                r.espacio = db.query(Espacio).filter(Espacio.id_espacio == r.id_espacio).first()
                if r.fecha_ingreso and r.fecha_salida:
                    diff = r.fecha_salida - r.fecha_ingreso
                    r.horas = round(diff.total_seconds() / 3600, 1)
                else:
                    r.horas = None

            registro_activo = next((r for r in historial if r.estado == "activo"), None)
            if vehiculo:
                vehiculo.usuario = db.query(Usuario).filter(
                    Usuario.id_usuario == vehiculo.id_usuario
                ).first()

    return request.app.state.plantillas.TemplateResponse(
        request=request,
        name="personal_buscar.html",
        context={
            "usuario_nombre": request.cookies.get("usuario_nombre", "Personal"),
            "placa": placa,
            "vehiculo": vehiculo,
            "historial": historial,
            "registro_activo": registro_activo,
        }
    )


# ====================== GESTIÓN DE PLAZAS ======================

@router.post("/espacios/estado/{espacio_id}")
async def cambiar_estado_espacio(
    request: Request,
    espacio_id: int,
    estado: str = Form(...),
    db: Session = Depends(get_db)
):
    if not verificar_personal(request):
        return RedirectResponse(url="/auth/login", status_code=303)

    espacio = db.query(Espacio).filter(Espacio.id_espacio == espacio_id).first()
    if espacio:
        espacio.estado = estado
        db.commit()
    return RedirectResponse(url="/personal/dashboard?exito=Estado+actualizado", status_code=303)