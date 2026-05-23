from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse

from app.base_datos import engine, Base, get_db
from app.rutas.autenticacion  import router as auth_router
from app.rutas.admin          import router as admin_router
from app.rutas.reservas       import router as reservas_router
from app.rutas.reservas_admin import router as reservas_admin_router
from app.rutas.cliente        import router as cliente_router
from app.rutas.personal       import router as personal_router

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Parking")

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
plantillas = Jinja2Templates(directory="app/plantillas")
app.state.plantillas = plantillas

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,           prefix="/auth",           tags=["autenticacion"])
app.include_router(admin_router,          prefix="/admin",          tags=["admin"])
app.include_router(reservas_admin_router, prefix="/admin/reservas", tags=["reservas-admin"])
app.include_router(reservas_router,       prefix="/reservas",       tags=["reservas"])
app.include_router(cliente_router,        prefix="/cliente",        tags=["cliente"])
app.include_router(personal_router,       prefix="/personal",       tags=["personal"])


@app.get("/")
async def home(request: Request):
    return plantillas.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard")
async def dashboard(request: Request):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/auth/login", status_code=303)

    rol = request.cookies.get("usuario_rol", "usuario")

    if rol == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    elif rol == "personal":
        return RedirectResponse(url="/personal/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/cliente/dashboard", status_code=303)


print("🚀 Smart Parking iniciado correctamente")
print("🌐 Abre: http://127.0.0.1:8000")