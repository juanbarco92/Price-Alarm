#!/usr/bin/env python3
"""
Script para ejecutar Price Alarm localmente en desarrollo.

Este script:
1. Configura el entorno local
2. Ejecuta la aplicación web en modo desarrollo
3. Permite testing sin deployment

Uso:
    python tools/dev_server.py (desde la raíz del proyecto)
"""

import os
import sys
import subprocess
from pathlib import Path

# Cambiar al directorio raíz del proyecto (parent de tools/)
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def check_dependencies():
    """Verifica que Poetry esté instalado."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Poetry no encontrado. Instálalo con: pip install poetry")
def install_dependencies():
    """Instala dependencias con Poetry usando setup_env.py."""
    print("📦 Configurando entorno completo...")
    
    # Ejecutar setup completo
    subprocess.run([
        "python", "tools/setup_env.py", "--skip-tests"
    ], check=True)
    print("✅ Entorno configurado")

def run_web_app():
    """Ejecuta la aplicación web en modo desarrollo."""
    print("🚀 Iniciando aplicación web...")
    print("📱 Dashboard: http://localhost:5000")
    print("⚙️  Admin Panel: http://localhost:5000/admin")
    print("🔌 API Health: http://localhost:5000/health")
    print("\n💡 Presiona Ctrl+C para detener\n")
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    try:
        subprocess.run(
            ["poetry", "run", "python", "app/main.py"],
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida")

def main():
    """Función principal."""
    print("🎯 Price Alarm - Servidor de Desarrollo")
    print("=" * 40)
    
    # Verificaciones básicas
    check_dependencies()
    
    # Setup completo (incluyendo dependencias)
    install_dependencies()
    
    # Ejecutar aplicación web
    run_web_app()

if __name__ == "__main__":
    main()
