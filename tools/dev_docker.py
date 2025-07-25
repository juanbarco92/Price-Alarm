#!/usr/bin/env python3
"""
Script para desarrollo con Docker.

Este script:
1. Construye los contenedores Docker
2. Ejecuta tests de integración
3. Levanta el stack completo de desarrollo
4. Proporciona comandos útiles para desarrollo

Uso:
    python tools/dev_docker.py [comando]
    
Comandos:
    setup       - Setup inicial con Docker
    build       - Solo construir imágenes
    up          - Levantar servicios (web + db + redis)
    down        - Bajar servicios
    test        - Ejecutar tests en containers
    logs        - Ver logs de todos los servicios
    shell       - Acceder a shell del container web
    scraper     - Ejecutar scraper una vez
    reset       - Reset completo (borra volúmenes)
    status      - Ver estado de servicios
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import argparse

# --- Inicio de la corrección ---
# Asegurar que el directorio raíz del proyecto esté en el path de Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
# --- Fin de la corrección ---

# Cambiar al directorio raíz del proyecto
os.chdir(PROJECT_ROOT)

def print_header(title):
    """Imprime header formateado."""
    print(f"\n🐳 {title}")
    print("=" * (len(title) + 3))

def run_command(command, description, check=True, stream_output=False):
    """Ejecuta un comando, mostrando la salida en tiempo real si se solicita."""
    print(f"📋 {description}...")
    
    # Para la salida en tiempo real, no capturamos la salida.
    # El proceso hijo heredará los descriptores de archivo estándar.
    capture_output = not stream_output

    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            text=True, 
            capture_output=capture_output
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        if capture_output and e.stderr:
            print(f"Error details: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_docker():
    """Verifica que Docker esté disponible."""
    print("🔍 Verificando Docker...")
    
    try:
        result = subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker no encontrado")
        print("   Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    try:
        result = subprocess.run(["docker-compose", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ docker-compose no encontrado")
        sys.exit(1)

def create_env_file():
    """Crea archivo .env para Docker."""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando .env para Docker...")
        env_content = """# Price Alarm Configuration
TG_TOKEN=your_telegram_bot_token_here
TG_CHAT_ID=your_telegram_chat_id_here

# Database (PostgreSQL for Docker)
DATABASE_URL=postgresql://priceuser:pricepass@db:5432/pricealarm

# Redis
REDIS_URL=redis://redis:6379/0

# Flask settings
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Scraping settings
SCRAPE_DELAY=2
SCRAPE_RETRIES=3
"""
        env_file.write_text(env_content)
        print("✅ Archivo .env creado")
        print("⚠️  IMPORTANTE: Edita .env con tus tokens de Telegram")

def setup():
    """Setup inicial completo."""
    print_header("SETUP INICIAL CON DOCKER")
    
    check_docker()
    create_env_file()
    
    print("\n🏗️ Construyendo imágenes Docker...")
    # Mostramos la salida en tiempo real para el build
    run_command("docker-compose build", "Construyendo web y scraper", stream_output=True)
    
    print("\n🚀 Levantando servicios base...")
    run_command("docker-compose up -d db redis", "Iniciando PostgreSQL y Redis")
    
    print("\n⏳ Esperando que la base de datos esté lista...")
    time.sleep(10)
    
    print("\n🗃️ Inicializando base de datos...")
    run_command(
        "docker-compose run --rm web python -c \"from shared.utils.database import PriceDatabase; db = PriceDatabase(); print('Base de datos inicializada')\"",
        "Setup de base de datos"
    )
    
    print("\n✅ Setup completo!")
    print("📋 Próximos pasos:")
    print("   1. python tools/dev_docker.py up    # Levantar servicios")
    print("   2. Visitar http://localhost:5000")

def build():
    """Solo construir imágenes."""
    print_header("CONSTRUIR IMÁGENES")
    run_command("docker-compose build", "Construyendo imágenes")

def up():
    """Levantar servicios."""
    print_header("LEVANTAR SERVICIOS")
    run_command("docker-compose up -d", "Iniciando todos los servicios")
    
    print("\n⏳ Esperando que los servicios estén listos...")
    time.sleep(15)
    
    print("\n🌐 Servicios disponibles:")
    print("   📱 Dashboard: http://localhost:5000")
    print("   ⚙️  Admin: http://localhost:5000/admin")
    print("   🔌 Health: http://localhost:5000/health")
    print("   🗃️ PostgreSQL: localhost:5432")
    print("   📊 Redis: localhost:6379")
    
    print("\n📋 Comandos útiles:")
    print("   python tools/dev_docker.py logs     # Ver logs")
    print("   python tools/dev_docker.py shell    # Acceder a container")
    print("   python tools/dev_docker.py scraper  # Ejecutar scraper")

def down():
    """Bajar servicios."""
    print_header("BAJAR SERVICIOS")
    run_command("docker-compose down", "Deteniendo servicios")

def test():
    """Ejecutar tests en containers."""
    print_header("EJECUTAR TESTS")
    
    # Asegurar que los servicios estén corriendo
    run_command("docker-compose up -d db redis", "Iniciando servicios base")
    time.sleep(5)
    
    # Tests unitarios
    print("\n🧪 Tests unitarios...")
    run_command(
        "docker-compose run --rm web python -m pytest tests/unit/ -v",
        "Tests unitarios",
        check=False
    )
    
    # Tests de integración
    print("\n🔗 Tests de integración...")
    run_command(
        "docker-compose run --rm web python -m pytest tests/integration/ -v",
        "Tests de integración",
        check=False
    )
    
    # Test de salud de servicios
    print("\n💓 Health checks...")
    run_command(
        "docker-compose run --rm web curl -f http://web:5000/health",
        "Health check web app",
        check=False
    )

def logs():
    """Ver logs de servicios."""
    print_header("LOGS DE SERVICIOS")
    run_command("docker-compose logs -f", "Siguiendo logs", check=False)

def shell():
    """Acceder a shell del container web."""
    print_header("SHELL INTERACTIVO")
    print("🐚 Accediendo al container web...")
    os.system("docker-compose exec web /bin/bash")

def scraper():
    """Ejecutar scraper una vez."""
    print_header("EJECUTAR SCRAPER")
    run_command(
        "docker-compose run --rm scraper python scraper/track.py",
        "Ejecutando scraper"
    )

def reset():
    """Reset completo."""
    print_header("RESET COMPLETO")
    print("⚠️  Esto borrará todos los datos!")
    response = input("¿Continuar? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operación cancelada")
        return
    
    run_command("docker-compose down -v", "Bajando servicios y borrando volúmenes")
    run_command("docker system prune -f", "Limpiando sistema Docker")
    print("✅ Reset completo")

def status():
    """Ver estado de servicios."""
    print_header("ESTADO DE SERVICIOS")
    run_command("docker-compose ps", "Estado de containers")
    
    print("\n📊 Uso de recursos:")
    run_command("docker stats --no-stream", "Estadísticas de containers", check=False)

def main():
    parser = argparse.ArgumentParser(description="Price Alarm Docker Development")
    parser.add_argument("command", nargs="?", default="up", 
                       choices=["setup", "build", "up", "down", "test", "logs", "shell", "scraper", "reset", "status"],
                       help="Comando a ejecutar")
    
    args = parser.parse_args()
    
    # Mapeo de comandos a funciones
    commands = {
        "setup": setup,
        "build": build,
        "up": up,
        "down": down,
        "test": test,
        "logs": logs,
        "shell": shell,
        "scraper": scraper,
        "reset": reset,
        "status": status
    }
    
    try:
        commands[args.command]()
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
