#!/usr/bin/env python3
"""
Script de PRUEBA para demostrar el funcionamiento del sistema sin depender de sitios reales.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List
import yaml
from dotenv import load_dotenv

# Importar nuestros módulos
from utils.database import PriceDatabase
from adapters import test_adapter

# Configurar logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def send_console_alert(product_name: str, old_price: float, new_price: float, url: str) -> None:
    """Envía alerta por consola."""
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

def process_product_test(db: PriceDatabase, product: Dict) -> None:
    """Procesa un producto usando el adaptador de prueba."""
    url = product['url']
    alias = product.get('alias', url)
    
    logger.info(f"Procesando producto de prueba: {alias}")
    
    try:
        # Extraer información usando el adaptador de prueba (sin Playwright)
        product_name, current_price, old_price = test_adapter.get_price(None, url)
        
        # Obtener último precio de la BD
        last_price = db.get_last_price(url)
        
        # Mostrar información actual
        print(f"\n📊 {product_name}")
        print(f"   Precio actual: ${current_price:,.0f}")
        if old_price:
            print(f"   Precio tachado: ${old_price:,.0f}")
        if last_price:
            print(f"   Último precio guardado: ${last_price:,.0f}")
        
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
        
        # Enviar alerta si corresponde
        if should_alert and reference_price:
            logger.info(f"¡ALERTA! {product_name} - {alert_reason}")
            send_console_alert(product_name, reference_price, current_price, url)
        else:
            print(f"   ✅ Sin cambios significativos")
        
        # Guardar precio en BD
        db.save_price(url, product_name, current_price, old_price)
        logger.info(f"Precio guardado en BD: {alias}")
        
    except Exception as e:
        logger.error(f"Error procesando {alias}: {e}")

def main():
    """Función principal del script de prueba."""
    load_dotenv()
    
    # Crear directorios necesarios
    Path("db").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("=== INICIO DE PRUEBA DEL SISTEMA ===")
    
    # Cargar configuración de prueba
    config_path = Path("config/products_test.yml")
    with open(config_path, 'r', encoding='utf-8') as f:
        products = yaml.safe_load(f)
    
    logger.info(f"Cargados {len(products)} productos de prueba")
    
    # Inicializar base de datos
    db = PriceDatabase()
    
    # Procesar cada producto
    for i, product in enumerate(products, 1):
        logger.info(f"\n--- Procesando producto {i}/{len(products)} ---")
        process_product_test(db, product)
    
    # Mostrar historial
    print("\n" + "="*60)
    print("📈 HISTORIAL DE PRECIOS")
    print("="*60)
    
    for product in products:
        url = product['url']
        alias = product.get('alias', url)
        
        history = db.get_price_history(url, limit=3)
        print(f"\n📊 {alias}:")
        
        if not history:
            print("   (Sin registros)")
        else:
            for record in history:
                name, price, old_price, timestamp = record
                old_str = f" (era: ${old_price:,.0f})" if old_price else ""
                print(f"   {timestamp}: ${price:,.0f}{old_str}")
    
    logger.info("\n=== PRUEBA COMPLETADA ===")
    print("\n🎉 ¡Prueba completada! Ejecuta el script varias veces para ver diferentes variaciones de precios.")

if __name__ == "__main__":
    main()
