#!/usr/bin/env python3
"""
Explorador avanzado de la base de datos jerárquica de precios.

Este script muestra:
- Estadísticas generales de la base de datos
- Productos con sus presentaciones y tiendas
- Comparación de precios por unidad entre tiendas
- Mejores ofertas actuales
- Historial de precios por tienda

Uso:
    python explore_db_advanced.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

def explore_database_advanced(db_path: str = "db/prices.db"):
    """Explora y muestra estadísticas avanzadas de la base de datos jerárquica."""
    
    # Verificar que existe la base de datos
    if not Path(db_path).exists():
        print(f"❌ No se encontró la base de datos: {db_path}")
        return
    
    print("🔍 Explorando base de datos jerárquica de precios...")
    print("=" * 60)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM prices")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM presentations")
        total_presentations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM stores")
        total_stores = cursor.fetchone()[0]
        
        print(f"📊 Estadísticas generales:")
        print(f"   • Productos: {total_products}")
        print(f"   • Presentaciones: {total_presentations}")
        print(f"   • Tiendas/URLs: {total_stores}")
        print(f"   • Registros de precios: {total_records:,}")
        
        if total_records == 0:
            print("❌ No hay datos de precios en la base de datos")
            return
        
        # 2. Rango de fechas
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM prices")
        min_date, max_date = cursor.fetchone()
        
        if min_date and max_date:
            min_dt = datetime.fromisoformat(min_date)
            max_dt = datetime.fromisoformat(max_date)
            days_diff = (max_dt - min_dt).days
            
            print(f"📅 Período de monitoreo:")
            print(f"   • Desde: {min_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"   • Hasta: {max_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"   • Duración: {days_diff} días")
        
        print("\n" + "=" * 60)
        print("🛍️ PRODUCTOS Y PRESENTACIONES:")
        print("=" * 60)
        
        # 3. Productos con sus presentaciones
        cursor.execute("""
            SELECT 
                prod.name,
                prod.alias,
                COUNT(DISTINCT pr.id) as presentaciones,
                COUNT(DISTINCT s.id) as tiendas,
                COUNT(p.id) as registros_precio
            FROM products prod
            LEFT JOIN presentations pr ON prod.id = pr.product_id
            LEFT JOIN stores s ON pr.id = s.presentation_id
            LEFT JOIN prices p ON s.id = p.store_id
            GROUP BY prod.id, prod.name, prod.alias
            ORDER BY prod.name
        """)
        
        products = cursor.fetchall()
        
        for name, alias, presentations_count, stores_count, price_records in products:
            print(f"\n📦 {name} ({alias})")
            print(f"   • Presentaciones: {presentations_count}")
            print(f"   • Tiendas: {stores_count}")
            print(f"   • Registros de precio: {price_records}")
            
            # Detalles de presentaciones
            cursor.execute("""
                SELECT pr.size, pr.unit_count, COUNT(s.id) as tiendas
                FROM presentations pr
                LEFT JOIN stores s ON pr.id = s.presentation_id
                JOIN products prod ON pr.product_id = prod.id
                WHERE prod.alias = ?
                GROUP BY pr.id, pr.size, pr.unit_count
                ORDER BY pr.unit_count
            """, (alias,))
            
            presentations = cursor.fetchall()
            for size, unit_count, store_count in presentations:
                print(f"     └─ {size} ({unit_count} unidades) - {store_count} tienda(s)")
        
        print("\n" + "=" * 60)
        print("🏆 MEJORES PRECIOS POR UNIDAD (ACTUALES):")
        print("=" * 60)
        
        # 4. Mejores precios por unidad para cada producto
        for name, alias, _, _, _ in products:
            print(f"\n💰 {name}:")
            
            cursor.execute("""
                SELECT 
                    s.store_name,
                    pr.size,
                    p.official_price,
                    p.discounted_price,
                    p.price_per_unit,
                    p.timestamp
                FROM prices p
                JOIN stores s ON p.store_id = s.id
                JOIN presentations pr ON s.presentation_id = pr.id
                JOIN products prod ON pr.product_id = prod.id
                WHERE prod.alias = ?
                AND p.id IN (
                    SELECT MAX(p2.id)
                    FROM prices p2
                    JOIN stores s2 ON p2.store_id = s2.id
                    JOIN presentations pr2 ON s2.presentation_id = pr2.id
                    JOIN products prod2 ON pr2.product_id = prod2.id
                    WHERE prod2.alias = ?
                    GROUP BY s2.id
                )
                ORDER BY p.price_per_unit ASC
            """, (alias, alias))
            
            current_prices = cursor.fetchall()
            
            if not current_prices:
                print("   └─ No hay datos de precios")
                continue
                
            for i, (store, size, official, discounted, per_unit, timestamp) in enumerate(current_prices, 1):
                dt = datetime.fromisoformat(timestamp)
                
                if discounted:
                    price_display = f"${discounted:,.0f} (antes ${official:,.0f})"
                    discount_pct = ((official - discounted) / official) * 100
                    discount_str = f" 🏷️ {discount_pct:.1f}% OFF"
                else:
                    price_display = f"${official:,.0f}"
                    discount_str = ""
                
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                
                print(f"   {rank_emoji} {store} - {size}")
                print(f"      💵 {price_display}{discount_str}")
                print(f"      📊 ${per_unit:,.0f} por unidad")
                print(f"      🕒 {dt.strftime('%Y-%m-%d %H:%M')}")
                print()
        
        print("=" * 60)
        print("📈 ÚLTIMOS 10 REGISTROS:")
        print("=" * 60)
        
        # 5. Últimos registros
        cursor.execute("""
            SELECT 
                prod.name,
                s.store_name,
                pr.size,
                p.official_price,
                p.discounted_price,
                p.price_per_unit,
                p.timestamp
            FROM prices p
            JOIN stores s ON p.store_id = s.id
            JOIN presentations pr ON s.presentation_id = pr.id
            JOIN products prod ON pr.product_id = prod.id
            ORDER BY p.timestamp DESC 
            LIMIT 10
        """)
        
        recent_records = cursor.fetchall()
        
        for name, store, size, official, discounted, per_unit, timestamp in recent_records:
            dt = datetime.fromisoformat(timestamp)
            
            if discounted:
                price_str = f"${discounted:,.0f} (oficial: ${official:,.0f})"
            else:
                price_str = f"${official:,.0f}"
                
            print(f"• {dt.strftime('%Y-%m-%d %H:%M')} - {name}")
            print(f"  📍 {store} - {size}")
            print(f"  💰 {price_str} (${per_unit:,.0f}/unidad)")
            print()
        
        print("=" * 60)
        print("💾 Exploración completada")

def main():
    """Función principal."""
    try:
        explore_database_advanced()
    except Exception as e:
        print(f"❌ Error explorando la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
