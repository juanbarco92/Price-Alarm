#!/usr/bin/env python3
"""
Script de setup completo para Price Alarm.

Este script configura todo el entorno de desarrollo:
- Verifica dependencias del sistema
- Instala Poetry si es necesario  
- Configura el entorno virtual
- Crea archivos de configuración
- Inicializa la base de datos
- Ejecuta tests básicos

Uso:
    python tools/setup_env.py [opciones]
    
Opciones:
    --skip-tests    No ejecutar tests de verificación
    --force         Forzar reinstalación de dependencias
    --production    Setup para producción (PostgreSQL)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

# Cambiar al directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def print_header():
    """Imprime header del script."""
    print("🎯" + "="*50)
    print("   PRICE ALARM - SETUP ENVIRONMENT")
    print("="*52)
    print()

def check_system_dependencies():
    """Verifica dependencias del sistema."""
    print("🔍 Verificando dependencias del sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ requerido")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Verificar Git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✅ Git disponible")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git no encontrado")
        sys.exit(1)

def install_poetry():
    """Instala Poetry si no está disponible."""
    print("📦 Verificando Poetry...")
    
    try:
        result = subprocess.run(["poetry", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("🔧 Instalando Poetry...")
    try:
        # Instalar usando el método oficial de Poetry para Windows
        if os.name == 'nt':  # Windows
            print("📥 Descargando instalador de Poetry...")
            import urllib.request
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.py', delete=False) as f:
                urllib.request.urlretrieve('https://install.python-poetry.org', f.name)
                subprocess.run([sys.executable, f.name], check=True)
                os.unlink(f.name)
        else:
            # Para Unix/Linux/macOS
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", "poetry"
            ], check=True)
        
        print("✅ Poetry instalado")
        print("⚠️  Puede que necesites reiniciar tu terminal")
        
        # Verificar que Poetry esté disponible
        try:
            subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Poetry instalado pero no está en PATH")
            print("   Agrega %APPDATA%\\Python\\Scripts a tu PATH en Windows")
            
    except Exception as e:
        print(f"❌ Error instalando Poetry: {e}")
        print("🔧 Instalación manual:")
        print("   Windows: https://python-poetry.org/docs/#installing-with-the-official-installer")
        sys.exit(1)

def setup_project_dependencies(force=False):
    """Instala dependencias del proyecto."""
    print("📚 Configurando dependencias del proyecto...")
    
    if force and Path(".venv").exists():
        print("🗑️ Removiendo entorno virtual existente...")
        shutil.rmtree(".venv")
    
    try:
        # Instalar dependencias
        subprocess.run(["poetry", "install"], check=True)
        print("✅ Dependencias Python instaladas")
        
        # Instalar navegadores de Playwright
        subprocess.run(["poetry", "run", "playwright", "install", "chromium"], check=True)
        print("✅ Navegadores Playwright instalados")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def create_env_file():
    """Crea archivo .env desde .env.example."""
    print("⚙️ Configurando variables de entorno...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("⚠️ .env.example no encontrado, creando uno básico...")
        env_example.write_text("""# Price Alarm Configuration
TG_TOKEN=your_telegram_bot_token_here
TG_CHAT_ID=your_telegram_chat_id_here

# Database (SQLite for development)
DATABASE_URL=sqlite:///./db/prices.db

# Flask settings
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Scraping settings
SCRAPE_DELAY=2
SCRAPE_RETRIES=3
""")
    
    if not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde .env.example")
    else:
        print("ℹ️ Archivo .env ya existe")

def setup_directories():
    """Crea directorios necesarios."""
    print("📁 Configurando directorios...")
    
    directories = ["db", "logs", "backups"]
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directorio {dir_name}/ creado")

def initialize_database():
    """Inicializa la base de datos."""
    print("🗃️ Inicializando base de datos...")
    
    try:
        # Importar y configurar la base de datos
        subprocess.run([
            "poetry", "run", "python", "-c",
            "from shared.utils.database import PriceDatabase; PriceDatabase().setup_database()"
        ], check=True, capture_output=True)
        print("✅ Base de datos inicializada")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error inicializando BD: {e}")
        sys.exit(1)

def run_basic_tests(skip=False):
    """Ejecuta tests básicos de verificación."""
    if skip:
        print("⏭️ Saltando tests de verificación")
        return
    
    print("🧪 Ejecutando tests de verificación...")
    
    tests = [
        ("Importación de módulos", "from shared.utils.database import PriceDatabase; print('✅ DB OK')"),
        ("Adaptadores", "from shared.adapters.alkosto import AlkostoAdapter; print('✅ Adapters OK')"),
        ("Flask app", "from app.main import create_app; app = create_app(); print('✅ Flask OK')")
    ]
    
    for test_name, test_code in tests:
        try:
            subprocess.run([
                "poetry", "run", "python", "-c", test_code
            ], check=True, capture_output=True)
            print(f"✅ {test_name}")
        except subprocess.CalledProcessError:
            print(f"❌ {test_name}")

def print_next_steps():
    """Imprime pasos siguientes."""
    print("\n🎉 ¡Setup completo!")
    print("\n📋 Próximos pasos:")
    print("   1. Configura tus tokens de Telegram en .env")
    print("   2. Agrega productos en shared/config/products.yml")
    print("   3. Ejecuta: python tools/dev_server.py")
    print("   4. Visita: http://localhost:5000")
    print("\n📖 Documentación completa en docs/DESARROLLO_LOCAL.md")

def main():
    parser = argparse.ArgumentParser(description="Setup Price Alarm development environment")
    parser.add_argument("--skip-tests", action="store_true", help="Skip verification tests")
    parser.add_argument("--force", action="store_true", help="Force reinstall dependencies")
    parser.add_argument("--production", action="store_true", help="Setup for production")
    
    args = parser.parse_args()
    
    print_header()
    
    try:
        check_system_dependencies()
        install_poetry()
        setup_project_dependencies(force=args.force)
        create_env_file()
        setup_directories()
        initialize_database()
        run_basic_tests(skip=args.skip_tests)
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
