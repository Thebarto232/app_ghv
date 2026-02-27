"""
Servidor de produccion para Gestión Humana - Colbeef
Usa Waitress (estable en Windows, reemplaza el servidor de desarrollo de Flask).

Uso:
    python run.py

La app estara disponible en:
    - Esta maquina:     http://localhost:5000
    - Red local (LAN):  http://<IP-DE-ESTA-MAQUINA>:5000

Para conocer la IP de esta maquina en red:
    ipconfig  (buscar "Direccion IPv4")
"""

import socket
from waitress import serve
from app import app

HOST = "0.0.0.0"   # Acepta conexiones desde cualquier maquina en la red
PORT = 5000

if __name__ == "__main__":
    # Obtener IP local para mostrarla en consola
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "desconocida"

    print("=" * 55)
    print("  GESTIÓN HUMANA - Colbeef  |  Servidor iniciado")
    print("=" * 55)
    print(f"  Local:      http://localhost:{PORT}")
    print(f"  Red LAN:    http://{local_ip}:{PORT}")
    print("  Para detener el servidor: Ctrl+C")
    print("=" * 55)

    serve(app, host=HOST, port=PORT, threads=8)
