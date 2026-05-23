# 🚗 SmartParking Web — Sistema de Gestión de Estacionamiento Vehicular (SIGEV)

> **Proyecto académico** desarrollado para el curso de Modelamiento de Base de Datos  
> Escuela Superior La Pontificia — Ingeniería de Sistemas de Información  
> Autor: Condori Cotaquispe, Suly Jhomy | Docente: Ing. Palomino Alanya, Erick | Ayacucho, 2026

---

## 📋 Descripción General

**SmartParking** es una aplicación web completa desarrollada con Python y FastAPI que automatiza y digitaliza todos los procesos operativos del estacionamiento **"Parking Central Ayacucho"**. El sistema reemplaza los registros manuales en papel por una plataforma moderna con tres paneles de control diferenciados según el rol del usuario: administrador, personal operativo y cliente.

El proyecto integra el modelamiento de una base de datos relacional normalizada hasta **Tercera Forma Normal (3FN)** en **Microsoft SQL Server**, con una interfaz web responsiva construida con **Tailwind CSS** y un backend de alto rendimiento con **FastAPI**.

---

## 🎯 Problema que Resuelve

| Situación Antes (Manual) | Situación Después (SIGEV) |
|--------------------------|---------------------------|
| Ingreso: 4.2 min/vehículo | Ingreso: 1.1 min/vehículo (**↓73.8%**) |
| Salida/cobro: 5.8 min/vehículo | Salida/cobro: 0.9 min/vehículo (**↓84.5%**) |
| Error en tarifas: 12% de transacciones | Error en tarifas: **0%** |
| Rendición de cuentas: 47 min/turno | Rendición de cuentas: <2 min/turno (**↓95.7%**) |

---

## 🏗️ Arquitectura del Sistema

```
Navegador Web (Cliente)
        │  HTTP
        ▼
┌─────────────────────────────────┐
│  FastAPI + Uvicorn (ASGI)       │  ← Backend (Python 3.11)
│  Jinja2 Templates               │  ← Motor de plantillas HTML
│  SQLAlchemy ORM                 │  ← Capa de acceso a datos
└────────────────┬────────────────┘
                 │ pyodbc
                 ▼
┌─────────────────────────────────┐
│  Microsoft SQL Server Express   │  ← Base de datos relacional
│  Base de datos: SmartParking    │
└─────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológico

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11 | Lenguaje principal |
| FastAPI | Latest | Framework web y rutas |
| SQLAlchemy | Latest | ORM para acceso a BD |
| Uvicorn | Latest | Servidor ASGI |
| Jinja2 | Latest | Motor de plantillas |
| passlib[bcrypt] | Latest | Cifrado de contraseñas |
| openpyxl | Latest | Exportación a Excel |
| pyodbc | Latest | Driver SQL Server |
| python-dotenv | Latest | Variables de entorno |

### Frontend
| Tecnología | Uso |
|------------|-----|
| HTML5 | Estructura semántica de páginas |
| Tailwind CSS (CDN) | Diseño visual responsivo |
| DaisyUI | Componentes UI adicionales |
| JavaScript ES6+ | Interactividad del cliente |
| Google Fonts: Syne + DM Sans | Tipografía |

### Base de Datos
| Componente | Detalle |
|------------|---------|
| SQL Server Express | Motor de base de datos |
| ODBC Driver 17 | Conector Windows |
| Normalización | Hasta 3FN (Tercera Forma Normal) |
| Tablas principales | 12 tablas relacionales |

---

## 📁 Estructura del Proyecto

```
Smart_Parking_WEB/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI, registro de routers
│   ├── base_datos.py              # Configuración de conexión SQLAlchemy + pyodbc
│   ├── configuracion.py           # Settings con pydantic-settings (.env)
│   │
│   ├── modelos/
│   │   ├── __init__.py
│   │   └── modelos.py             # Clases ORM: Usuario, Vehiculo, Espacio,
│   │                              #   Reserva, Registro, Pago, Personal,
│   │                              #   Puesto, Mantenimiento, TarjetaAcceso,
│   │                              #   TipoReporte, Reporte
│   │
│   ├── esquemas/
│   │   ├── __init__.py
│   │   └── reservas.py            # Esquemas Pydantic: ReservaCreate, ReservaOut
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── espacios.py            # CRUD: obtener_todos, crear, actualizar,
│   │   │                          #   cambiar_estado, eliminar, stats
│   │   ├── reservas.py            # CRUD cliente: crear_reserva, obtener_reservas_usuario,
│   │   │                          #   cancelar_reserva, confirmar_reserva, finalizar_reserva
│   │   ├── reservas_admin.py      # CRUD admin: obtener_todas, filtros, stats,
│   │   │                          #   cambiar_estado, cancelar
│   │   └── usuarios.py            # CRUD: crear, actualizar, cambiar_contrasena,
│   │                              #   cambiar_estado, eliminar, stats
│   │
│   ├── rutas/
│   │   ├── __init__.py
│   │   ├── autenticacion.py       # GET/POST /auth/login, /auth/registro, /auth/logout
│   │   ├── admin.py               # Todas las rutas /admin/* (dashboard, espacios,
│   │   │                          #   usuarios, reservas, personal, pagos,
│   │   │                          #   mantenimiento, reportes, exportar Excel)
│   │   ├── cliente.py             # Rutas /cliente/* (dashboard, perfil, vehículos,
│   │   │                          #   reservas, cambio de contraseña)
│   │   ├── personal.py            # Rutas /personal/* (dashboard, ingreso, salida,
│   │   │                          #   buscar por placa)
│   │   └── reservas.py            # Rutas /reservas/* (nueva reserva, mis-reservas,
│   │                              #   cancelar)
│   │
│   ├── plantillas/                # Templates HTML con Jinja2 + Tailwind CSS
│   │   ├── base.html              # Layout base con estilos globales
│   │   │
│   │   ├── login.html             # Pantalla de inicio de sesión
│   │   ├── registro.html          # Formulario de registro con validaciones
│   │   │
│   │   ├── admin_dashboard.html   # Panel admin: stats, mapa tiempo real, últimas reservas
│   │   ├── admin_espacios.html    # Gestión de espacios: tabla, modales crear/editar
│   │   ├── admin_usuarios.html    # Gestión de usuarios: editar, activar/desactivar
│   │   ├── admin_reservas.html    # Lista con filtros por estado/fecha/búsqueda
│   │   ├── admin_reserva_detalle.html  # Detalle completo de una reserva
│   │   ├── admin_personal.html    # Gestión de personal y puestos
│   │   ├── admin_pagos.html       # Historial y registro manual de pagos
│   │   ├── admin_mantenimiento.html    # Control de mantenimiento de espacios
│   │   ├── admin_reportes.html    # Estadísticas y botones de exportación
│   │   │
│   │   ├── cliente_dashboard.html # Panel cliente: mapa interactivo, mis reservas activas
│   │   ├── cliente_perfil.html    # Edición de perfil y cambio de contraseña
│   │   ├── cliente_vehiculos.html # CRUD de vehículos registrados
│   │   │
│   │   ├── personal_dashboard.html     # Panel operario: mapa, vehículos estacionados
│   │   ├── personal_ingreso.html       # Formulario registro de ingreso por placa
│   │   ├── personal_salida.html        # Lista de vehículos con botón registrar salida
│   │   ├── personal_buscar.html        # Búsqueda de historial por placa
│   │   │
│   │   ├── reserva.html           # Formulario de nueva reserva con cálculo dinámico
│   │   ├── mis_reservas.html      # Historial de reservas del cliente/usuario
│   │   ├── dashboard.html         # Dashboard genérico (redirección por rol)
│   │   └── ...
│   │
│   └── static/                    # Archivos estáticos (CSS, JS, imágenes)
│
├── .env                           # Variables de entorno (no commitear)
├── requirements.txt               # Dependencias Python
└── test_conexion.py               # Script de prueba de conexión SQL Server
```

---

## 🗄️ Modelo de Base de Datos

### Tablas Principales

```
usuarios          → Todos los usuarios del sistema (admin, personal, cliente)
    │
    ├──< vehiculos          → Vehículos registrados por cada usuario
    │       │
    │       └──< registros  → Entradas/salidas físicas de vehículos
    │               └──< pagos → Pagos de los registros
    │
    ├──< reservas           → Reservas anticipadas de espacios
    │
    └──< personal           → Datos laborales del personal operativo
            └──< mantenimiento → Trabajos de mantenimiento asignados

espacios          → Espacios del estacionamiento con tarifas y estado
    └──< reservas, registros, mantenimiento

puestos           → Catálogo de puestos laborales con salario base
tarjetas_acceso   → Tarjetas RFID/acceso de usuarios
tipos_reporte     → Catálogo de tipos de reporte
reportes          → Reportes de incidencias del sistema
```

### Estados de los Espacios
| Estado | Color en UI | Descripción |
|--------|-------------|-------------|
| `disponible` | 🟢 Verde | Libre para reservar o estacionar |
| `ocupado` | 🔴 Rojo | Vehículo físicamente estacionado |
| `reservado` | 🟡 Amarillo | Con reserva activa confirmada |
| `mantenimiento` | ⚫ Gris | No disponible temporalmente |

### Estados de las Reservas
| Estado | Descripción |
|--------|-------------|
| `Pendiente` | Creada, pendiente de confirmación |
| `Confirmada` | Confirmada por el sistema o administrador |
| `Cancelada` | Cancelada por el cliente o admin |
| `Finalizada` | Completada exitosamente |

---

## 👥 Roles y Funcionalidades

### 🔴 Administrador (`/admin/`)
- **Dashboard** con estadísticas en tiempo real: ocupación, ingresos, reservas del día, mapa visual de plazas por piso
- **Gestión de Espacios**: crear, editar, cambiar estado, eliminar. Estadísticas por tipo y estado
- **Gestión de Usuarios**: ver todos, editar datos, activar/desactivar cuentas, resetear contraseña
- **Gestión de Reservas**: listado con filtros múltiples (estado, fecha, búsqueda por nombre/placa), detalle completo, cambiar estado, cancelar
- **Gestión de Personal**: registrar personal, asignar puestos y turnos, crear nuevos puestos con salario base
- **Gestión de Pagos**: historial completo, registrar pagos manuales, actualizar estado de pago
- **Mantenimiento**: registrar trabajos, asignar responsable, completar y liberar espacio automáticamente
- **Reportes**: estadísticas globales, espacios más reservados, exportar a **Excel (.xlsx)** con 4 hojas (Reservas, Espacios, Usuarios, Pagos)

### 🟡 Personal Operativo (`/personal/`)
- **Dashboard** con mapa de ocupación en tiempo real, vehículos actualmente estacionados y reservas próximas
- **Registrar Ingreso**: búsqueda de vehículo por placa, selección de espacio disponible, método de pago, hora en tiempo real
- **Registrar Salida**: lista de vehículos estacionados con cálculo automático de horas y monto, confirmación con un clic
- **Buscar por Placa**: historial completo de cualquier vehículo, datos del propietario, estado actual

### 🔵 Cliente (`/cliente/`)
- **Dashboard** con mapa interactivo de espacios por piso (clic en verde para reservar), estadísticas y mis reservas activas
- **Mis Vehículos**: registrar, editar y eliminar vehículos propios (placa, marca, modelo, color, año, tipo)
- **Reservar Espacio**: selección de fechas de inicio/fin con cálculo automático del monto estimado
- **Mis Reservas**: historial completo con opción de cancelar reservas pendientes
- **Mi Perfil**: editar nombre, teléfono, dirección; cambiar contraseña con validación de contraseña actual

---

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.11+
- Microsoft SQL Server Express
- ODBC Driver 17 for SQL Server
- Node.js (opcional, para herramientas de desarrollo)

### 1. Clonar el repositorio
```bash
git clone https://github.com/usuario/SmartParking.git
cd SmartParking
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### 3. Configurar la base de datos en SQL Server
```sql
CREATE DATABASE SmartParking;
```
Ejecutar los scripts SQL de creación de tablas (ver Capítulo 4 del informe).

### 4. Configurar variables de entorno
Crear el archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=mssql+pyodbc://sa:TU_PASSWORD@.\SQLEXPRESS/SmartParking?driver=ODBC+Driver+17+for+SQL+Server
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
```

### 5. Verificar la conexión
```bash
python test_conexion.py
```

### 6. Iniciar el servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Abrir en el navegador
```
http://localhost:8000
```

---

## 🔐 Seguridad

| Mecanismo | Implementación |
|-----------|----------------|
| Cifrado de contraseñas | `bcrypt` vía `passlib` |
| Gestión de sesiones | Cookies HTTP `httponly` con expiración de 1 hora |
| Control de acceso por rol | Verificación de cookie `usuario_rol` en cada ruta protegida |
| Protección SQL Injection | Consultas parametrizadas automáticas via SQLAlchemy ORM |
| Protección XSS | Escape automático de variables en plantillas Jinja2 |
| Middleware de seguridad | `TrustedHostMiddleware` y `CORSMiddleware` de FastAPI |

---

## 📊 Funcionalidades Destacadas

### Cálculo Automático de Tarifas
```python
# En crud/reservas.py
def _calcular_monto(tarifa_hora: float, inicio: datetime, fin: datetime) -> float:
    horas = max(1, (fin - inicio).total_seconds() / 3600)
    return round(tarifa_hora * horas, 2)
```

### Exportación a Excel con openpyxl
El reporte Excel generado incluye:
- **Hoja 1 — Reservas**: ID, usuario, email, espacio, piso, fechas, monto, estado
- **Hoja 2 — Espacios**: número, piso, tipo, estado, tarifas (hora/día)
- **Hoja 3 — Usuarios**: nombre, apellido, email, DNI, teléfono, rol, estado, fecha de registro
- **Hoja 4 — Pagos**: usuario, monto, método de pago, comprobante, fecha, estado

### Mapa Visual de Ocupación en Tiempo Real
Cada espacio se renderiza como un bloque de color en el dashboard, con tooltip de información. Los espacios disponibles son **clicables** y redirigen directamente al formulario de reserva.

---

## 📦 Dependencias (requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
pyodbc
python-dotenv
pydantic-settings
passlib[bcrypt]
jinja2
python-multipart
openpyxl
```

---

## 🗺️ Rutas Principales de la API

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET/POST | `/auth/login` | Todos | Inicio de sesión |
| GET/POST | `/auth/registro` | Público | Registro de nuevo usuario |
| GET | `/auth/logout` | Todos | Cierre de sesión |
| GET | `/admin/dashboard` | Admin | Panel principal |
| GET/POST | `/admin/espacios` | Admin | Listar y gestionar espacios |
| GET/POST | `/admin/usuarios` | Admin | Listar y gestionar usuarios |
| GET | `/admin/reservas` | Admin | Listar reservas con filtros |
| GET | `/admin/reportes` | Admin | Estadísticas generales |
| GET | `/admin/reportes/exportar/excel` | Admin | Descarga Excel con 4 hojas |
| GET | `/cliente/dashboard` | Cliente | Panel con mapa interactivo |
| GET/POST | `/cliente/vehiculos` | Cliente | Gestión de vehículos propios |
| GET/POST | `/cliente/reservas` | Cliente | Ver mis reservas |
| GET | `/personal/dashboard` | Personal | Panel operativo |
| GET/POST | `/personal/ingreso/registrar` | Personal | Registrar entrada de vehículo |
| POST | `/personal/salida/registrar/{id}` | Personal | Registrar salida con cobro |
| GET/POST | `/reservas/nueva/{id_espacio}` | Cliente | Crear nueva reserva |

---

## 📈 Resultados Obtenidos

La implementación del SIGEV en el estacionamiento "Parking Central Ayacucho" demostró los siguientes resultados cuantitativos tras 30 días de operación:

- **73.8%** de reducción en tiempo promedio de atención en ingreso
- **84.5%** de reducción en tiempo promedio de atención en salida
- **100%** de eliminación de errores en cálculo de tarifas (de 12% a 0%)
- **95.7%** de reducción en tiempo de rendición de cuentas por turno
- Personal operativo autónomo en el uso del sistema tras **2 horas** de capacitación

---

## 👨‍💻 Autor

**Condori Cotaquispe, Suly Jhomy**  
Escuela Superior La Pontificia — Ingeniería de Sistemas de Información  
Curso: Modelamiento de Base de Datos — Sección 7"A"  
Docente: Ing. Palomino Alanya, Erick  
Ayacucho, 2026

---

## 📄 Licencia

Proyecto académico desarrollado con fines educativos para la Escuela Superior La Pontificia, Ayacucho, Perú.

---

*"SmartParking — Transformando la gestión de estacionamientos en Ayacucho mediante tecnología moderna y bases de datos relacionales."*
