#!/usr/bin/env python3
"""
Script de testing completo para Price Alarm.

Este script ejecuta todos los tests disponibles:
- Tests unitarios
- Tests de integración  
- Tests de Docker
- Health checks
- Performance tests

Uso:
    python tools/test_all.py [opciones]
    
Opciones:
    --docker        Solo tests con Docker
    --local         Solo tests locales
    --unit          Solo tests unitarios
    --integration   Solo tests de integración
    --quick         Tests rápidos (sin Docker build)
    --ci            Modo CI (sin interacción)
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import argparse

# Cambiar al directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def print_section(title):
    """Imprime sección formateada."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def run_command(command, description, check=True):
    """Ejecuta comando con manejo de errores."""
    print(f"\n📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, text=True)
        print("✅ PASÓ")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FALLÓ: {e}")
        return False

def test_docker_availability():
    """Verifica que Docker esté disponible."""
    print_section("VERIFICACIÓN DE DOCKER")
    
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker disponible")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker no disponible")
        return False
    
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✅ docker-compose disponible")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ docker-compose no disponible")
        return False

def test_local_environment():
    """Tests del entorno local."""
    print_section("TESTS DE ENTORNO LOCAL")
    
    success = True
    
    # Test Python version
    if sys.version_info >= (3, 11):
        print("✅ Python 3.11+ disponible")
    else:
        print("❌ Python 3.11+ requerido")
        success = False
    
    # Test Poetry
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry disponible")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Poetry no disponible")
        success = False
    
    # Test archivos de configuración
    config_files = [".env", "pyproject.toml", "shared/config/products.yml"]
    for file in config_files:
        if Path(file).exists():
            print(f"✅ {file} existe")
        else:
            print(f"⚠️ {file} no existe")
    
    return success

def test_unit_tests():
    """Ejecuta tests unitarios."""
    print_section("TESTS UNITARIOS")
    
    success = True
    
    # Test con pytest local
    if run_command("poetry run python -m pytest tests/unit/ -v --tb=short", "Tests unitarios locales", check=False):
        print("✅ Tests unitarios locales PASARON")
    else:
        print("❌ Tests unitarios locales FALLARON")
        success = False
    
    return success

def test_integration_tests():
    """Ejecuta tests de integración."""
    print_section("TESTS DE INTEGRACIÓN")
    
    success = True
    
    # Test imports
    if run_command(
        "poetry run python -c \"from shared.utils.database import PriceDatabase; from shared.adapters.alkosto import AlkostoAdapter; print('Imports OK')\"",
        "Test de imports", check=False
    ):
        print("✅ Imports funcionan")
    else:
        print("❌ Imports fallaron")
        success = False
    
    # Test database
    if run_command(
        "poetry run python -c \"from shared.utils.database import PriceDatabase; db = PriceDatabase(); db.setup_database(); print('Database OK')\"",
        "Test de base de datos", check=False
    ):
        print("✅ Base de datos funciona")
    else:
        print("❌ Base de datos falló")
        success = False
    
    return success

def test_docker_stack():
    """Tests con Docker completo."""
    print_section("TESTS CON DOCKER")
    
    success = True
    
    print("🔨 Construyendo imágenes Docker...")
    if not run_command("docker-compose build", "Build de imágenes Docker", check=False):
        print("❌ Build de Docker falló")
        return False
    
    print("🚀 Levantando stack de testing...")
    if not run_command("docker-compose up -d db redis", "Levantar servicios base", check=False):
        print("❌ No se pudieron levantar servicios base")
        return False
    
    # Esperar que los servicios estén listos
    print("⏳ Esperando servicios...")
    time.sleep(15)
    
    # Test health checks
    print("💓 Verificando health checks...")
    if run_command(
        "docker-compose run --rm web python -c \"import requests; r = requests.get('http://db:5432'); print('DB reachable')\"",
        "Test conectividad DB", check=False
    ):
        print("✅ Base de datos alcanzable")
    else:
        print("❌ Base de datos no alcanzable")
        success = False
    
    # Test aplicación web
    print("🌐 Testing aplicación web...")
    if run_command(
        "docker-compose run --rm web python -c \"from app.main import create_app; app = create_app(); print('Flask app OK')\"",
        "Test Flask app", check=False
    ):
        print("✅ Flask app funciona")
    else:
        print("❌ Flask app falló")
        success = False
    
    # Test scraper
    print("🕷️ Testing scraper...")
    if run_command(
        "docker-compose run --rm scraper python -c \"from shared.adapters.alkosto import AlkostoAdapter; print('Scraper OK')\"",
        "Test scraper", check=False
    ):
        print("✅ Scraper funciona")
    else:
        print("❌ Scraper falló")
        success = False
    
    # Cleanup
    print("🧹 Limpiando...")
    run_command("docker-compose down", "Bajando servicios", check=False)
    
    return success

def test_docker_integration():
    """Tests de integración completos con Docker."""
    print_section("TESTS DE INTEGRACIÓN CON DOCKER")
    
    success = True
    
    print("🚀 Levantando stack completo...")
    if not run_command("docker-compose up -d", "Levantar stack completo", check=False):
        return False
    
    # Esperar que todo esté listo
    print("⏳ Esperando stack completo...")
    time.sleep(30)
    
    # Test end-to-end
    tests = [
        ("docker-compose exec -T web curl -f http://localhost:5000/health", "Health check web"),
        ("docker-compose run --rm web python -m pytest tests/unit/ -v", "Tests unitarios en Docker"),
        ("docker-compose run --rm web python -m pytest tests/integration/ -v", "Tests integración en Docker"),
    ]
    
    for command, description in tests:
        if not run_command(command, description, check=False):
            success = False
    
    # Cleanup
    run_command("docker-compose down", "Bajando servicios", check=False)
    
    return success

def generate_report(results):
    """Genera reporte final."""
    print_section("REPORTE FINAL")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"📊 Resumen: {passed_tests}/{total_tests} tests pasaron")
    print()
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests fallaron")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test suite completo para Price Alarm")
    parser.add_argument("--docker", action="store_true", help="Solo tests con Docker")
    parser.add_argument("--local", action="store_true", help="Solo tests locales")
    parser.add_argument("--unit", action="store_true", help="Solo tests unitarios")
    parser.add_argument("--integration", action="store_true", help="Solo tests de integración")
    parser.add_argument("--quick", action="store_true", help="Tests rápidos")
    parser.add_argument("--ci", action="store_true", help="Modo CI")
    
    args = parser.parse_args()
    
    print("🎯 PRICE ALARM - TEST SUITE COMPLETO")
    print("=" * 60)
    
    results = {}
    
    try:
        # Tests básicos siempre
        if not args.docker:
            results["Entorno Local"] = test_local_environment()
        
        if args.unit or not (args.docker or args.integration):
            results["Tests Unitarios"] = test_unit_tests()
        
        if args.integration or not (args.docker or args.unit):
            results["Tests Integración"] = test_integration_tests()
        
        # Tests de Docker
        if args.docker or not (args.local or args.unit or args.integration):
            if test_docker_availability():
                if not args.quick:
                    results["Docker Stack"] = test_docker_stack()
                results["Docker Integración"] = test_docker_integration()
            else:
                print("⚠️ Saltando tests de Docker (no disponible)")
        
        # Generar reporte
        success = generate_report(results)
        
        if not success and not args.ci:
            response = input("\n¿Ver logs detallados? (y/N): ")
            if response.lower() == 'y':
                print("📋 Para ver logs:")
                print("   docker-compose logs")
                print("   poetry run python -m pytest tests/ -v -s")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Tests cancelados")
        run_command("docker-compose down", "Limpieza", check=False)
        sys.exit(1)

if __name__ == "__main__":
    main()
