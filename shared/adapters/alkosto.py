"""
Adaptador para extraer preci        # Extraer nombre del producto
        product_name = _extract_product_name(page)
        
        # Extraer precio actual mostrado
        current_displayed_price = _extract_current_price(page)
        
        # Extraer precio tachado (si existe)
        old_tachado_price = _extract_old_price(page)
        
        # Aplicar la nueva lógica:
        # Si hay precio tachado, ese es el oficial y el actual es el descuento
        # Si no hay precio tachado, el actual es el oficial
        if old_tachado_price:
            official_price = old_tachado_price
            discounted_price = current_displayed_price
            logger.info(f"Producto con descuento: {product_name}")
            logger.info(f"Precio oficial: ${official_price:,.0f}, Con descuento: ${discounted_price:,.0f}")
        else:
            official_price = current_displayed_price
            discounted_price = None
            logger.info(f"Producto sin descuento: {product_name} - ${official_price:,.0f}")
        
        return product_name, official_price, discounted_pricecom.
"""

import re
import logging
from typing import Optional, Tuple
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

def get_price(page: Page, url: str) -> Tuple[str, float, Optional[float]]:
    """
    Extrae información de precio de una página de Alkosto.
    
    Args:
        page: Instancia de página de Playwright
        url: URL del producto en Alkosto
    
    Returns:
        Tupla de (nombre_producto, precio_oficial, precio_con_descuento)
        
    Raises:
        ValueError: Si no se puede extraer la información del precio
        PlaywrightTimeoutError: Si la página no carga
    """
    logger.info(f"Extrayendo precio de: {url}")
    
    try:
        # Navegar a la página
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Extraer nombre del producto
        product_name = _extract_product_name(page)
        
        # Extraer precio actual mostrado
        current_displayed_price = _extract_current_price(page)
        
        # Extraer precio tachado (si existe)
        old_tachado_price = _extract_old_price(page)
        
        # Aplicar la nueva lógica:
        # Si hay precio tachado, ese es el oficial y el actual es el descuento
        # Si no hay precio tachado, el actual es el oficial
        if old_tachado_price:
            official_price = old_tachado_price
            discounted_price = current_displayed_price
            logger.info(f"Producto con descuento: {product_name}")
            logger.info(f"Precio oficial: ${official_price:,.0f}, Con descuento: ${discounted_price:,.0f}")
        else:
            official_price = current_displayed_price
            discounted_price = None
            logger.info(f"Producto sin descuento: {product_name} - ${official_price:,.0f}")
        
        return product_name, official_price, discounted_price
        
    except PlaywrightTimeoutError:
        logger.error(f"Timeout al cargar la página: {url}")
        raise
    except Exception as e:
        logger.error(f"Error extrayendo precio de {url}: {e}")
        raise ValueError(f"No se pudo extraer el precio: {e}")

def _extract_product_name(page: Page) -> str:
    """Extrae el nombre del producto."""
    selectors = [
        # Selector específico basado en estructura actual de Alkosto
        'main > section:first-child > div:first-child > div:first-child > div:first-child > h1',
        'main section:first-child h1',  # Versión más flexible
        'main h1',  # Aún más flexible
        # Selectores genéricos como respaldo
        'h1[data-testid="product-title"]',
        'h1.product-title',
        'h1[class*="title"]',
        '.product-name h1',
        'h1'
    ]
    
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=5000)
            if element:
                name = element.text_content().strip()
                if name:
                    return name
        except PlaywrightTimeoutError:
            continue
    
    # TODO: Verificar selector CSS correcto para el nombre del producto
    raise ValueError("No se pudo encontrar el nombre del producto")

def _extract_current_price(page: Page) -> float:
    """Extrae el precio actual del producto."""
    price_selectors = [
        # Selector específico encontrado en la página actual de Alkosto
        '#js-original_price',
        # Selectores específicos basados en estructura actual de Alkosto (respaldo)
        '.session-price',
        '.session-price-padding', 
        '.price-block',
        '.new-container__main-product__pdp-features__pdp_price',
        '.product__details-section__price',
        # Selectores genéricos como respaldo
        '[data-testid="price-current"]',
        '.price-current',
        '.current-price',
        '[class*="price"][class*="current"]',
        '.price .current',
        '.product-price .current',
        # Selectores más amplios para capturar precios
        '[class*="price"]',
        '.price'
    ]
    
    for selector in price_selectors:
        try:
            elements = page.query_selector_all(selector)
            for element in elements:
                price_text = element.text_content()
                if price_text:
                    # Buscar todos los precios en el texto usando regex
                    import re
                    price_matches = re.findall(r'\$?\s*[\d,\.]+', price_text)
                    
                    for match in price_matches:
                        price = _parse_price(match)
                        if price > 0:
                            return price
        except Exception:
            continue
    
    # TODO: Verificar selector CSS correcto para el precio actual
    raise ValueError("No se pudo encontrar el precio actual")

def _extract_old_price(page: Page) -> Optional[float]:
    """Extrae el precio anterior (tachado) si existe."""
    old_price_selectors = [
        # Selector específico encontrado en la página actual de Alkosto
        '#js-original_price_old span',  # Precio anterior
        '#js-original_price_old',       # Contenedor del precio anterior
        # Nota: El % de descuento está en '#js-original_price_old div'
        # Selectores genéricos como respaldo
        '[data-testid="price-old"]',
        '.price-old',
        '.old-price',
        '[class*="price"][class*="old"]',
        '[class*="price"][class*="previous"]',
        '.price .strikethrough',
        '.price .line-through',
        'del',
        's'
    ]
    
    for selector in old_price_selectors:
        try:
            elements = page.query_selector_all(selector)
            for element in elements:
                price_text = element.text_content()
                if price_text:
                    price = _parse_price(price_text)
                    if price > 0:
                        return price
        except Exception:
            continue
    
    return None

def _extract_discount_percentage(page: Page) -> Optional[str]:
    """Extrae el porcentaje de descuento si existe."""
    try:
        # Selector específico para el porcentaje de descuento en Alkosto
        element = page.query_selector('#js-original_price_old div')
        if element:
            discount_text = element.text_content()
            if discount_text and '%' in discount_text:
                return discount_text.strip()
    except Exception:
        pass
    
    return None

def _parse_price(price_text: str) -> float:
    """
    Convierte texto de precio a número flotante.
    
    Ejemplos:
        "$1.234.567" -> 1234567.0
        "$ 1,234,567" -> 1234567.0
        "1.234.567 COP" -> 1234567.0
    """
    if not price_text:
        return 0.0
    
    # Limpiar el texto: quitar símbolos de moneda, espacios, etc.
    cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
    
    if not cleaned:
        return 0.0
    
    # Manejar diferentes formatos de separadores
    # Si hay punto y coma, asumimos formato colombiano: 1.234.567,89
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            # Formato: 1.234.567,89
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Formato: 1,234,567.89
            cleaned = cleaned.replace(',', '')
    elif '.' in cleaned:
        # Determinar si es separador decimal o de miles
        parts = cleaned.split('.')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Probablemente decimal: 1234.56
            pass
        else:
            # Probablemente separador de miles: 1.234.567
            cleaned = cleaned.replace('.', '')
    elif ',' in cleaned:
        # Similar lógica para comas
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Probablemente decimal: 1234,56
            cleaned = cleaned.replace(',', '.')
        else:
            # Probablemente separador de miles: 1,234,567
            cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        logger.warning(f"No se pudo convertir precio: {price_text}")
        return 0.0
