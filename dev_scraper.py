#!/usr/bin/env python3
"""
Script para ejecutar el scraper localmente.

Uso:
    python dev_scraper.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_scraper():
    """Ejecuta el scraper una vez."""
    print("🕷️  Ejecutando scraper...")
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    try:
        subprocess.run(
            ["poetry", "run", "python", "scraper/track.py"],
            env=env,
            check=True
        )
        print("✅ Scraper completado")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando scraper: {e}")
    except KeyboardInterrupt:
        print("\n👋 Scraper interrumpido")

def main():
    """Función principal."""
    print("🕷️  Price Alarm - Scraper Local")
    print("=" * 30)
    
    # Verificar que .env existe
    if not Path(".env").exists():
        print("❌ Archivo .env no encontrado")
        print("💡 Ejecuta primero: python dev_server.py")
        sys.exit(1)
    
    run_scraper()

if __name__ == "__main__":
    main()
