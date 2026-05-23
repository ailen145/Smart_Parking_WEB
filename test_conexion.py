import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# ================== CONFIGURACIÓN ==================
SERVER = r".\SQLEXPRESS"          # Opción 1 (recomendada)
# SERVER = "localhost\\SQLEXPRESS"   # Opción 2
# SERVER = "(local)\\SQLEXPRESS"     # Opción 3

DATABASE = "SmartParking"
USERNAME = "sa"
PASSWORD = "jhomy1403"        # ← CAMBIA ESTO por la contraseña que le pusiste al usuario 'sa'

print("🔄 Probando conexión a SQL Server SQLEXPRESS...")
print(f"Usando servidor: {SERVER}")
print(f"Base de datos: {DATABASE}\n")

try:
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    
    conn = pyodbc.connect(conn_str, timeout=15)
    print("✅ ¡Conexión exitosa con pyodbc usando usuario 'sa'!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"📌 Versión SQL Server: {version[:100]}...\n")
    
    cursor.execute("SELECT DB_NAME()")
    print(f"📌 Conectado correctamente a la base de datos: {cursor.fetchone()[0]}")
    
    conn.close()

except pyodbc.Error as e:
    print("❌ Error de pyodbc:")
    print(e)
except Exception as e:
    print("❌ Error inesperado:", e)