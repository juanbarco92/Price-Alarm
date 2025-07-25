#!/usr/bin/env python3
"""
Script para ejecutar Price Alarm localmente en desarrollo.

Este script:
1. Configura el entorno local
2. Ejecuta la aplicación web en modo desarrollo
3. Permite testing sin deployment

Uso:
    python dev_server.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica que Poetry esté instalado."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Poetry no encontrado. Instálalo con: pip install poetry")
        sys.exit(1)

def install_dependencies():
    """Instala dependencias con Poetry."""
    print("📦 Instalando dependencias...")
    subprocess.run(["poetry", "install"], check=True)
    print("✅ Dependencias instaladas")

def setup_env():
    """Configura variables de entorno para desarrollo."""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando archivo .env desde .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            content = example_file.read_text()
            # Configuración por defecto para desarrollo
            content = content.replace(
                "DATABASE_URL=postgresql://user:password@localhost:5432/pricealarm",
                "DATABASE_URL=sqlite:///db/prices.db"
            )
            content = content.replace(
                "FLASK_ENV=development",
                "FLASK_ENV=development"
            )
            env_file.write_text(content)
            print("✅ Archivo .env creado")
            print("⚠️  IMPORTANTE: Edita .env con tus tokens de Telegram")
        else:
            print("❌ No se encontró .env.example")

def create_directories():
    """Crea directorios necesarios."""
    directories = ["db", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directorios creados")

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
    env["PYTHONPATH"] = str(Path.cwd())
    
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
    
    # Verificaciones
    check_dependencies()
    
    # Setup
    install_dependencies()
    setup_env()
    create_directories()
    
    # Ejecutar
    run_web_app()

if __name__ == "__main__":
    main()
