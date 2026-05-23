from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.base_datos import get_db
from app.modelos.modelos import Usuario

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/login")
async def mostrar_login(request: Request):
    return request.app.state.plantillas.TemplateResponse(
        request=request, name="login.html"
    )

@router.get("/registro")
async def mostrar_registro(request: Request):
    return request.app.state.plantillas.TemplateResponse(
        request=request, name="registro.html"
    )

@router.post("/registro")
async def registrar_usuario(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    direccion: str = Form(...),
    password: str = Form(...),
    confirmar_password: str = Form(...),
    rol: str = Form("usuario"),
    db: Session = Depends(get_db)
):
    # Validar DNI
    if not dni.isdigit() or len(dni) != 8:
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "El DNI debe tener exactamente 8 dígitos"}
        )

    # Validar teléfono
    if not telefono.isdigit() or len(telefono) != 9:
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "El teléfono debe tener exactamente 9 dígitos"}
        )

    # Validar contraseñas
    if password != confirmar_password:
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "Las contraseñas no coinciden"}
        )

    if len(password) < 8:
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "La contraseña debe tener mínimo 8 caracteres"}
        )

    # Verificar email duplicado
    if db.query(Usuario).filter(Usuario.email == email).first():
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "Este correo ya está registrado"}
        )

    # Verificar DNI duplicado
    if db.query(Usuario).filter(Usuario.dni == dni).first():
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "Este DNI ya está registrado"}
        )

    hashed_password = pwd_context.hash(password)
    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        telefono=telefono,
        email=email,
        direccion=direccion,
        contrasena=hashed_password,
        tipo_usuario=rol,
        estado="activo"
    )
    db.add(nuevo_usuario)
    db.commit()

    return RedirectResponse(url="/auth/login?registro=ok", status_code=303)


@router.post("/login")
async def login_usuario(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not pwd_context.verify(password, usuario.contrasena):
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Correo o contraseña incorrectos"}
        )

    if usuario.estado != "activo":
        return request.app.state.plantillas.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Tu cuenta está desactivada. Contacta al administrador."}
        )

    # Redirigir según rol
    if usuario.tipo_usuario == "admin":
        redirect_url = "/admin/dashboard"
    elif usuario.tipo_usuario == "personal":
        redirect_url = "/personal/dashboard"
    else:
        redirect_url = "/dashboard"

    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(key="usuario_id", value=str(usuario.id_usuario), httponly=True, max_age=3600)
    response.set_cookie(key="usuario_nombre", value=f"{usuario.nombre} {usuario.apellido}", httponly=True, max_age=3600)
    response.set_cookie(key="usuario_rol", value=usuario.tipo_usuario or "usuario", httponly=True, max_age=3600)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("usuario_id")
    response.delete_cookie("usuario_nombre")
    response.delete_cookie("usuario_rol")
    return response