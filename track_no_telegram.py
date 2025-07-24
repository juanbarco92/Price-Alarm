#!/usr/bin/env python3
"""
Versión simplificada del tracker sin notificaciones de Telegram.
Solo guarda precios en la base de datos y muestra alertas en consola.
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
from utils.database import PriceDatabase
from adapters import alkosto

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
    config_path = Path("config/products.yml")
    
    if not config_path.exists():
        logger.error(f"Archivo de configuración no encontrado: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            products = yaml.safe_load(f)
        
        if not products:
            logger.warning("No hay productos configurados")
            return []
        
        logger.info(f"Cargados {len(products)} productos para monitorear")
        return products
        
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

def send_console_alert(product_name: str, old_price: float, new_price: float, url: str) -> None:
    """Envía alerta por consola (sin Telegram)."""
    discount_percent = ((old_price - new_price) / old_price) * 100
    
    print("\n" + "="*60)
    print("🔥 ¡PRECIO REBAJADO!")
    print("="*60)
    print(f"📦 Producto: {product_name}")
    print(f"💰 Precio anterior: ${old_price:,.0f}")
    print(f"🎯 Precio actual: ${new_price:,.0f}")
    print(f"📉 Descuento: {discount_percent:.1f}%")
    print(f"🛒 URL: {url}")
    print("="*60)
    
    logger.warning(f"ALERTA: {product_name} bajó de ${old_price:,.0f} a ${new_price:,.0f} ({discount_percent:.1f}% descuento)")

def process_product(page: Page, db: PriceDatabase, product: Dict) -> None:
    """
    Procesa un producto individual: extrae precio, compara y alerta.
    """
    url = product['url']
    alias = product.get('alias', url)
    
    logger.info(f"Procesando producto: {alias}")
    
    # Obtener adaptador apropiado
    adapter = get_adapter_for_url(url)
    if not adapter:
        return
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Extraer información del producto
            product_name, current_price, old_price = adapter.get_price(page, url)
            
            # Obtener último precio de la BD
            last_price = db.get_last_price(url)
            
            # Determinar si hay que alertar
            should_alert = False
            alert_reason = ""
            reference_price = None
            
            # Condición 1: Precio bajó ≥ 10%
            if last_price and current_price < last_price:
                discount_percent = (last_price - current_price) / last_price
                if discount_percent >= 0.10:
                    should_alert = True
                    alert_reason = f"Bajó {discount_percent*100:.1f}% desde ${last_price:,.0f}"
                    reference_price = last_price
            
            # Condición 2: Hay precio tachado (oferta especial)
            if old_price and current_price < old_price:
                if not should_alert:  # Solo si no alertamos ya por la otra condición
                    should_alert = True
                    alert_reason = f"Precio tachado detectado: era ${old_price:,.0f}"
                    reference_price = old_price
            
            # Enviar alerta si corresponde (por consola)
            if should_alert and reference_price:
                logger.info(f"Enviando alerta: {product_name} - {alert_reason}")
                send_console_alert(product_name, reference_price, current_price, url)
            else:
                logger.info(f"Sin cambios significativos para: {product_name} (${current_price:,.0f})")
            
            # Guardar precio en BD
            db.save_price(url, product_name, current_price, old_price)
            
            logger.info(f"Producto procesado exitosamente: {alias}")
            break
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Intento {retry_count}/{max_retries} falló para {alias}: {e}")
            
            if retry_count >= max_retries:
                logger.error(f"Error procesando {alias} después de {max_retries} intentos: {e}")
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
    
    logger.info("=== Iniciando monitoreo de precios (SIN TELEGRAM) ===")
    
    # Cargar configuración
    products = load_config()
    if not products:
        logger.info("No hay productos para procesar")
        return
    
    # Crear directorio de BD si no existe
    Path("db").mkdir(exist_ok=True)
    
    # Inicializar base de datos
    db = PriceDatabase()
    
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
            
            # Procesar cada producto
            for i, product in enumerate(products, 1):
                logger.info(f"Procesando producto {i}/{len(products)}")
                process_product(page, db, product)
                
                # Pequeña pausa entre productos para no sobrecargar
                if i < len(products):
                    import time
                    time.sleep(2)
            
        finally:
            browser.close()
    
    logger.info("=== Monitoreo completado ===")

if __name__ == "__main__":
    main()
