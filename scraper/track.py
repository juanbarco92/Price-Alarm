#!/usr/bin/env python3
"""
Script principal para el monitoreo de precios.

Este script:
1. Lee la configuración de productos desde config/products.yml
2. Para cada producto, extrae el precio usando el adaptador apropiado
3. Compara con el último precio guardado en la BD
4. Envía alerta por Telegram si detecta una baja significativa
5. Guarda el nuevo precio en la base de datos

Uso:
    python track.py

Variables de entorno requeridas:
    TG_TOKEN: Token del bot de Telegram
    TG_CHAT_ID: ID del chat donde enviar alertas
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List
import yaml
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Browser, Page
from urllib.parse import urlparse

# Importar nuestros módulos
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.utils.database import PriceDatabase
from shared.utils.alert import send_price_alert_sync
from shared.adapters import alkosto

# Configurar logging
def setup_logging():
    """Configura el sistema de logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configurar formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler('logs/track.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

def load_config() -> List[Dict]:
    """Carga la configuración de productos desde el archivo YAML."""
    config_path = Path(__file__).parent.parent / "shared" / "config" / "products.yml"
    
    if not config_path.exists():
        logger.error(f"Archivo de configuración no encontrado: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config or 'products' not in config:
            logger.warning("No hay productos configurados")
            return []
        
        # Aplanar la estructura jerárquica para el procesamiento
        urls_to_process = []
        for product in config['products']:
            for presentation in product['presentations']:
                for store in presentation['stores']:
                    urls_to_process.append({
                        'url': store['url'],
                        'product_name': product['name'],
                        'alias': product['alias'],
                        'store_name': store['name'],
                        'presentation_size': presentation['size'],
                        'unit_count': presentation['unit_count']
                    })
        
        logger.info(f"Cargadas {len(urls_to_process)} URLs para monitorear de {len(config['products'])} productos")
        return config['products'], urls_to_process
        
    except yaml.YAMLError as e:
        logger.error(f"Error leyendo configuración YAML: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        sys.exit(1)

def get_adapter_for_url(url: str):
    """Determina qué adaptador usar según la URL."""
    domain = urlparse(url).netloc.lower()
    
    if 'alkosto.com' in domain:
        return alkosto
    else:
        logger.error(f"No hay adaptador disponible para: {domain}")
        return None

def process_product(page: Page, db: PriceDatabase, url_info: Dict) -> None:
    """
    Procesa un producto individual: extrae precio, compara y alerta.
    
    Args:
        page: Página de Playwright para scraping
        db: Instancia de base de datos
        url_info: Diccionario con información de la URL a procesar
    """
    url = url_info['url']
    product_name = url_info['product_name']
    store_name = url_info['store_name']
    
    logger.info(f"Procesando: {product_name} en {store_name}")
    
    # Obtener adaptador apropiado
    adapter = get_adapter_for_url(url)
    if not adapter:
        return
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Extraer información del producto
            extracted_name, official_price, discounted_price = adapter.get_price(page, url)
            
            # Obtener último precio oficial de la BD
            last_official_price = db.get_last_price(url)
            
            # Determinar si hay que alertar
            should_alert = False
            alert_reason = ""
            
            # Condición 1: Precio oficial bajó ≥ 10% (descuento histórico)
            if last_official_price and official_price < last_official_price:
                discount_percent = (last_official_price - official_price) / last_official_price
                if discount_percent >= 0.10:
                    should_alert = True
                    alert_reason = f"Precio oficial bajó {discount_percent*100:.1f}% desde ${last_official_price:,.0f}"
            
            # Condición 2: Hay precio con descuento (oferta promocional)
            if discounted_price:
                if not should_alert:  # Solo si no alertamos ya por la otra condición
                    should_alert = True
                    alert_reason = f"Oferta promocional detectada: ${official_price:,.0f} → ${discounted_price:,.0f}"
            
            # Enviar alerta si corresponde
            if should_alert:
                logger.info(f"Enviando alerta: {product_name} en {store_name} - {alert_reason}")
                # Usar el precio efectivo (con descuento si existe, sino el oficial)
                effective_price = discounted_price if discounted_price else official_price
                reference_price = last_official_price if last_official_price else official_price
                send_price_alert_sync(f"{product_name} ({store_name})", reference_price, effective_price, url)
            
            # Guardar precio en BD
            db.save_price(url, extracted_name, official_price, discounted_price)
            
            logger.info(f"Producto procesado exitosamente: {product_name} en {store_name}")
            break
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Intento {retry_count}/{max_retries} falló para {product_name} en {store_name}: {e}")
            
            if retry_count >= max_retries:
                logger.error(f"Error procesando {product_name} en {store_name} después de {max_retries} intentos: {e}")
            else:
                # Esperar antes del siguiente intento
                import time
                time.sleep(2 ** retry_count)  # Backoff exponencial

def main():
    """Función principal del script."""
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar logging
    setup_logging()
    
    logger.info("=== Iniciando monitoreo de precios ===")
    
    # Verificar variables de entorno
    if not os.getenv('TG_TOKEN') or not os.getenv('TG_CHAT_ID'):
        logger.error("Variables TG_TOKEN y TG_CHAT_ID son requeridas")
        sys.exit(1)
    
    # Cargar configuración
    product_configs, urls_to_process = load_config()
    if not urls_to_process:
        logger.info("No hay productos para procesar")
        return
    
    # Crear directorio de BD si no existe
    Path("db").mkdir(exist_ok=True)
    
    # Inicializar base de datos
    db = PriceDatabase()
    
    # Configurar jerarquía de productos en la BD
    for product_config in product_configs:
        db.setup_product_hierarchy(product_config)
    
    # Inicializar Playwright
    with sync_playwright() as p:
        logger.info("Iniciando navegador...")
        browser: Browser = p.chromium.launch(headless=True)
        
        try:
            page: Page = browser.new_page()
            
            # Configurar página
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Procesar cada URL
            for i, url_info in enumerate(urls_to_process, 1):
                logger.info(f"Procesando URL {i}/{len(urls_to_process)}")
                process_product(page, db, url_info)
                
                # Pequeña pausa entre productos para no sobrecargar
                if i < len(urls_to_process):
                    import time
                    time.sleep(2)
            
        finally:
            browser.close()
    
    logger.info("=== Monitoreo completado ===")

if __name__ == "__main__":
    main()
