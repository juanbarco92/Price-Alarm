import time
import logging
import sys
import os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Añadir el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos del proyecto
from shared.utils.database import PriceDatabase
from scraper.track import load_config, process_product

# Cargar variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_all_products():
    """
    Obtiene todos los productos del archivo de configuración y actualiza sus precios.
    """
    logger.info("Iniciando ciclo de scraping de todos los productos.")
    
    try:
        # Cargar configuración de productos
        products, urls_to_process = load_config()
        if not urls_to_process:
            logger.info("No se encontraron productos en la configuración para scrapear.")
            return

        logger.info(f"Se encontraron {len(products)} productos para scrapear.")

        # Inicializar base de datos
        db = PriceDatabase()

        # Usar Playwright para crear una instancia de navegador
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Configurar user agent y headers como en el track.py original
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            # Procesar cada producto
            for url_info in urls_to_process:
                try:
                    logger.info(f"Procesando: {url_info.get('product_name', 'Producto sin nombre')} - {url_info.get('url', 'URL no encontrada')}")
                    process_product(page, db, url_info)
                except Exception as e:
                    logger.error(f"Error al procesar producto {url_info.get('product_name', 'desconocido')}: {e}")
                    continue  # Continuar con el siguiente producto

            browser.close()

        logger.info("Ciclo de scraping completado exitosamente.")

    except Exception as e:
        logger.error(f"Error en el ciclo de scraping: {e}")


if __name__ == '__main__':
    # Para un inicio más rápido en el primer ciclo, ejecutar inmediatamente
    scrape_all_products()

    scheduler = BackgroundScheduler()
    # Programar la ejecución cada hora. Para probar, puedes cambiar 'hours=1' a 'minutes=5' o 'seconds=30'
    scheduler.add_job(scrape_all_products, 'interval', hours=1)
    scheduler.start()
    
    logger.info("Scheduler iniciado. El scraper se ejecutará cada hora.")
    logger.info("Presiona Ctrl+C para salir.")

    try:
        # Mantener el script principal vivo para que el scheduler siga corriendo en segundo plano
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler detenido.")
