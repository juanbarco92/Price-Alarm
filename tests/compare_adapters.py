"""
Script para comparar precios entre múltiples adaptadores y sitios web.

Este script permite probar varios productos de diferentes sitios
y comparar resultados, útil para validar la consistencia de adaptadores.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from adapters import alkosto, test_adapter

@dataclass
class ProductResult:
    """Resultado de extracción de un producto."""
    url: str
    adapter: str
    success: bool
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    old_price: Optional[float] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

def get_adapter(url: str):
    """Determina qué adaptador usar según la URL."""
    if 'alkosto.com' in url.lower():
        return alkosto, 'alkosto'
    else:
        return test_adapter, 'test'

def test_multiple_products(urls: List[str], headless: bool = True) -> List[ProductResult]:
    """
    Testea múltiples productos y devuelve resultados.
    
    Args:
        urls: Lista de URLs de productos
        headless: Si ejecutar navegador en modo headless
    
    Returns:
        Lista de ProductResult con los resultados
    """
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 720})
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            for i, url in enumerate(urls, 1):
                print(f"\n📦 Procesando producto {i}/{len(urls)}: {url}")
                
                adapter, adapter_name = get_adapter(url)
                
                try:
                    product_name, current_price, old_price = adapter.get_price(page, url)
                    
                    result = ProductResult(
                        url=url,
                        adapter=adapter_name,
                        success=True,
                        product_name=product_name,
                        current_price=current_price,
                        old_price=old_price
                    )
                    
                    print(f"✅ {product_name} - ${current_price:,.0f}")
                    if old_price:
                        print(f"   💸 Precio anterior: ${old_price:,.0f}")
                    
                except Exception as e:
                    result = ProductResult(
                        url=url,
                        adapter=adapter_name,
                        success=False,
                        error=str(e)
                    )
                    print(f"❌ Error: {e}")
                
                results.append(result)
                
                # Pausa entre productos
                if i < len(urls):
                    import time
                    time.sleep(2)
        
        finally:
            browser.close()
    
    return results

def save_results(results: List[ProductResult], output_file: str = None):
    """Guarda resultados en archivo JSON."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"tests/results_{timestamp}.json"
    
    # Convertir a diccionarios para JSON
    results_dict = [asdict(result) for result in results]
    
    Path(output_file).parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}")

def print_summary(results: List[ProductResult]):
    """Imprime resumen de resultados."""
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    print(f"Total de productos: {total}")
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(successful/total)*100:.1f}%")
    
    if failed > 0:
        print("\n🔍 PRODUCTOS FALLIDOS:")
        for result in results:
            if not result.success:
                print(f"  • {result.url}")
                print(f"    Adaptador: {result.adapter}")
                print(f"    Error: {result.error}")
    
    # Estadísticas de precios
    successful_results = [r for r in results if r.success and r.current_price]
    if successful_results:
        prices = [r.current_price for r in successful_results]
        print(f"\n💰 ESTADÍSTICAS DE PRECIOS:")
        print(f"  Precio mínimo: ${min(prices):,.0f}")
        print(f"  Precio máximo: ${max(prices):,.0f}")
        print(f"  Precio promedio: ${sum(prices)/len(prices):,.0f}")
        
        # Productos con descuento
        discounted = [r for r in successful_results if r.old_price and r.old_price > r.current_price]
        if discounted:
            print(f"  🎯 Productos con descuento: {len(discounted)}")
            for result in discounted:
                discount = (result.old_price - result.current_price) / result.old_price * 100
                print(f"    • {result.product_name}: {discount:.1f}% descuento")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Comparador de precios multi-adaptador")
    parser.add_argument("--urls", nargs="+", help="URLs de productos a testear")
    parser.add_argument("--file", help="Archivo con URLs (una por línea)")
    parser.add_argument("--output", help="Archivo de salida para resultados JSON")
    parser.add_argument("--no-headless", action="store_true", help="Ejecutar navegador visible")
    
    args = parser.parse_args()
    
    # Obtener URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip()]
                urls.extend(file_urls)
        else:
            print(f"❌ Archivo no encontrado: {args.file}")
            return
    
    if not urls:
        print("❌ No se proporcionaron URLs para testear")
        print("Uso:")
        print("  python tests/compare_adapters.py --urls URL1 URL2 URL3")
        print("  python tests/compare_adapters.py --file urls.txt")
        return
    
    print(f"🚀 Iniciando comparación de {len(urls)} productos...")
    
    # Ejecutar tests
    results = test_multiple_products(urls, headless=not args.no_headless)
    
    # Mostrar resumen
    print_summary(results)
    
    # Guardar resultados
    save_results(results, args.output)

if __name__ == "__main__":
    main()
