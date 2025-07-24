"""
Script para testing completo del adaptador de Alkosto con información detallada.

Este script extrae toda la información disponible incluyendo:
- Nombre del producto
- Precio actual
- Precio anterior
- Porcentaje de descuento
- Información adicional de debugging
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
from adapters import alkosto

def test_alkosto_complete(url: str):
    """
    Test completo del adaptador de Alkosto mostrando toda la información disponible.
    """
    print(f"🧪 Testing completo de Alkosto: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Navegar a la página
            print("📡 Navegando a la página...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            print("\n" + "="*80)
            print("📊 INFORMACIÓN EXTRAÍDA")
            print("="*80)
            
            # Extraer información usando el adaptador
            try:
                product_name, current_price, old_price = alkosto.get_price(page, url)
                
                print(f"📦 Producto: {product_name}")
                print(f"💰 Precio actual: ${current_price:,.0f}")
                
                if old_price:
                    print(f"💸 Precio anterior: ${old_price:,.0f}")
                    discount_amount = old_price - current_price
                    discount_percent = (discount_amount / old_price) * 100
                    print(f"💵 Ahorro: ${discount_amount:,.0f}")
                    print(f"📈 Descuento calculado: {discount_percent:.1f}%")
                else:
                    print("💸 Precio anterior: No encontrado")
                
                # Intentar extraer porcentaje de descuento de la página
                try:
                    discount_text = alkosto._extract_discount_percentage(page)
                    if discount_text:
                        print(f"🏷️  Descuento mostrado en página: {discount_text}")
                    else:
                        print("🏷️  Descuento mostrado en página: No encontrado")
                except Exception as e:
                    print(f"🏷️  Descuento mostrado en página: Error - {e}")
                
                print("\n✅ Extracción exitosa")
                
            except Exception as e:
                print(f"❌ Error en extracción: {e}")
                return False
            
            # Información adicional de debugging
            print("\n" + "="*80)
            print("🔍 INFORMACIÓN DE DEBUGGING")
            print("="*80)
            
            # Verificar elementos específicos
            elements_to_check = [
                ('#js-original_price', 'Precio actual'),
                ('#js-original_price_old span', 'Precio anterior'),
                ('#js-original_price_old div', 'Porcentaje descuento'),
                ('main h1', 'Título del producto')
            ]
            
            for selector, description in elements_to_check:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()[:100] if element.text_content() else "Sin texto"
                        print(f"✅ {description} ({selector}): {text}")
                    else:
                        print(f"❌ {description} ({selector}): No encontrado")
                except Exception as e:
                    print(f"⚠️  {description} ({selector}): Error - {e}")
            
            return True
            
        finally:
            browser.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Testing completo del adaptador de Alkosto")
    parser.add_argument("--url", required=True, help="URL del producto a testear")
    
    args = parser.parse_args()
    
    success = test_alkosto_complete(args.url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
