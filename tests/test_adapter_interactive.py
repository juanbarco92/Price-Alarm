"""
Script para testear adaptadores de scraping de forma interactiva.

Este script permite:
1. Probar un adaptador específico con una URL
2. Ver información detallada del HTML extraído
3. Debuggear selectores CSS que no funcionan
4. Guardar screenshots para análisis visual

Uso:
    python tests/test_adapter_interactive.py --url <URL> --adapter <alkosto|test>
    python tests/test_adapter_interactive.py --url "https://www.alkosto.com/producto/p/123" --adapter alkosto
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from adapters import alkosto, test_adapter

def setup_logging(verbose: bool = False):
    """Configura logging para el testing."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_adapter(adapter_name: str):
    """Obtiene el adaptador por nombre."""
    adapters = {
        'alkosto': alkosto,
        'test': test_adapter
    }
    
    return adapters.get(adapter_name.lower())

def debug_selectors(page: Page, url: str):
    """
    Función de debugging que muestra información útil sobre la página.
    """
    print("\n" + "="*80)
    print("🔍 INFORMACIÓN DE DEBUGGING")
    print("="*80)
    
    # Información básica de la página
    print(f"📄 Título de la página: {page.title()}")
    print(f"🌐 URL actual: {page.url}")
    print(f"📏 Dimensiones: {page.viewport_size}")
    
    # Buscar posibles selectores para nombre del producto
    print("\n🏷️  POSIBLES SELECTORES PARA NOMBRE DEL PRODUCTO:")
    name_selectors = [
        'h1', 'h2', '[class*="title"]', '[class*="name"]', 
        '[class*="product"]', '[data-testid*="title"]',
        '[data-testid*="name"]', '.product-title', '.product-name'
    ]
    
    for selector in name_selectors:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"  ✅ {selector}: {len(elements)} elemento(s)")
                for i, elem in enumerate(elements[:3]):  # Solo mostrar primeros 3
                    text = elem.text_content()[:100] if elem.text_content() else "Sin texto"
                    print(f"     [{i+1}] {text}")
        except Exception:
            pass
    
    # Buscar posibles selectores para precios
    print("\n💰 POSIBLES SELECTORES PARA PRECIOS:")
    price_selectors = [
        '[class*="price"]', '[class*="cost"]', '[class*="amount"]',
        '[data-testid*="price"]', '.price', '.cost', '.amount',
        'span[class*="$"]', 'div[class*="$"]'
    ]
    
    for selector in price_selectors:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"  ✅ {selector}: {len(elements)} elemento(s)")
                for i, elem in enumerate(elements[:5]):  # Mostrar más precios
                    text = elem.text_content()[:50] if elem.text_content() else "Sin texto"
                    classes = elem.get_attribute('class') or 'sin-clase'
                    print(f"     [{i+1}] {text} (clases: {classes})")
        except Exception:
            pass
    
    # Buscar elementos que contengan números (posibles precios)
    print("\n🔢 ELEMENTOS CON NÚMEROS (POSIBLES PRECIOS):")
    try:
        # Usar JavaScript para encontrar elementos con números grandes
        js_code = """
        () => {
            const elements = Array.from(document.querySelectorAll('*'));
            const priceElements = [];
            
            elements.forEach(el => {
                const text = el.textContent || '';
                // Buscar números grandes (posibles precios)
                const numbers = text.match(/[\\d,\\.]+/g);
                if (numbers) {
                    numbers.forEach(num => {
                        const cleaned = num.replace(/[^\\d]/g, '');
                        if (cleaned.length >= 4) {  // Números de al menos 4 dígitos
                            priceElements.push({
                                text: text.trim().substring(0, 100),
                                tagName: el.tagName,
                                className: el.className,
                                number: num
                            });
                        }
                    });
                }
            });
            
            return priceElements.slice(0, 10);  // Primeros 10
        }
        """
        
        price_elements = page.evaluate(js_code)
        for i, elem in enumerate(price_elements):
            print(f"  [{i+1}] {elem['tagName']}.{elem['className']}: {elem['text']} (número: {elem['number']})")
            
    except Exception as e:
        print(f"  ❌ Error ejecutando JavaScript: {e}")

def take_screenshot(page: Page, adapter_name: str, url: str) -> str:
    """Toma un screenshot de la página para análisis visual."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = Path("tests") / "screenshots" / f"{adapter_name}_{timestamp}.png"
    screenshot_path.parent.mkdir(exist_ok=True)
    
    page.screenshot(path=str(screenshot_path), full_page=True)
    return str(screenshot_path)

def test_adapter(adapter_name: str, url: str, debug: bool = False, screenshot: bool = False, headless: bool = True):
    """
    Testea un adaptador específico con una URL.
    
    Args:
        adapter_name: Nombre del adaptador (alkosto, test)
        url: URL del producto a testear
        debug: Si mostrar información de debugging
        screenshot: Si tomar screenshot
        headless: Si ejecutar el navegador en modo headless
    """
    adapter = get_adapter(adapter_name)
    if not adapter:
        print(f"❌ Adaptador '{adapter_name}' no encontrado")
        print(f"Adaptadores disponibles: alkosto, test")
        return False
    
    print(f"🧪 Testeando adaptador '{adapter_name}' con URL: {url}")
    
    with sync_playwright() as p:
        print("🚀 Iniciando navegador...")
        browser: Browser = p.chromium.launch(headless=headless)
        
        try:
            page: Page = browser.new_page()
            
            # Configurar página como en el script principal
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            # Ejecutar debugging antes del adaptador si se solicita
            if debug:
                try:
                    print("📡 Navegando a la página para debugging...")
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    debug_selectors(page, url)
                except Exception as e:
                    print(f"❌ Error durante debugging: {e}")
            
            # Tomar screenshot si se solicita
            screenshot_path = None
            if screenshot:
                try:
                    if not debug:  # Si no hicimos debugging, navegar ahora
                        page.goto(url, wait_until="networkidle", timeout=30000)
                    screenshot_path = take_screenshot(page, adapter_name, url)
                    print(f"📸 Screenshot guardado en: {screenshot_path}")
                except Exception as e:
                    print(f"❌ Error tomando screenshot: {e}")
            
            # Probar el adaptador
            print(f"\n🔬 Ejecutando adaptador '{adapter_name}'...")
            try:
                product_name, current_price, old_price = adapter.get_price(page, url)
                
                print("\n" + "="*60)
                print("✅ RESULTADO EXITOSO")
                print("="*60)
                print(f"📦 Producto: {product_name}")
                print(f"💰 Precio actual: ${current_price:,.0f}")
                if old_price:
                    print(f"💸 Precio anterior: ${old_price:,.0f}")
                    discount = (old_price - current_price) / old_price * 100
                    print(f"🎯 Descuento: {discount:.1f}%")
                else:
                    print("💸 Precio anterior: No encontrado")
                
                return True
                
            except Exception as e:
                print(f"\n❌ ERROR DEL ADAPTADOR: {e}")
                print("💡 Sugerencias:")
                print("   - Ejecuta con --debug para ver selectores disponibles")
                print("   - Ejecuta con --screenshot para análisis visual")
                print("   - Verifica que la URL sea correcta")
                return False
                
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Tester interactivo para adaptadores de scraping")
    parser.add_argument("--url", required=True, help="URL del producto a testear")
    parser.add_argument("--adapter", required=True, choices=['alkosto', 'test'], 
                       help="Adaptador a usar")
    parser.add_argument("--debug", action="store_true", 
                       help="Mostrar información de debugging")
    parser.add_argument("--screenshot", action="store_true", 
                       help="Tomar screenshot de la página")
    parser.add_argument("--no-headless", action="store_true", 
                       help="Ejecutar navegador visible (no headless)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Logging verbose")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    success = test_adapter(
        adapter_name=args.adapter,
        url=args.url,
        debug=args.debug,
        screenshot=args.screenshot,
        headless=not args.no_headless
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
