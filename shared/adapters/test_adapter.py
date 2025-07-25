"""
Adaptador de prueba que simula la extracción de precios para demostrar el funcionamiento.
"""

import random
import logging
from typing import Optional, Tuple
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

def get_price(page: Page, url: str) -> Tuple[str, float, Optional[float]]:
    """
    Simulador de extracción de precios para pruebas.
    
    Returns:
        Tupla de (nombre_producto, precio_actual, precio_anterior)
    """
    logger.info(f"[PRUEBA] Simulando extracción de precio para: {url}")
    
    # Simular nombres de productos según la URL
    if "pampers" in url.lower():
        product_name = "Pañal Pampers Cruisers 360 Fit Talla 5 x56 Unidades"
        base_price = 45000
    else:
        product_name = "Producto de Prueba"
        base_price = 30000
    
    # Simular variación de precio (±15%)
    variation = random.uniform(-0.15, 0.15)
    current_price = base_price * (1 + variation)
    current_price = round(current_price, -2)  # Redondear a centenas
    
    # 30% de probabilidad de tener precio anterior (oferta)
    old_price = None
    if random.random() < 0.3:
        old_price = current_price * random.uniform(1.1, 1.4)  # 10-40% más caro
        old_price = round(old_price, -2)
    
    logger.info(f"[PRUEBA] Producto: {product_name}")
    logger.info(f"[PRUEBA] Precio actual: ${current_price:,.0f}")
    if old_price:
        logger.info(f"[PRUEBA] Precio anterior: ${old_price:,.0f}")
    
    return product_name, current_price, old_price
