#!/usr/bin/env python3
"""
Script para explorar básicamente la base de datos de precios.

Este script muestra:
- Número total de registros
- Productos únicos monitoreados  
- Rango de fechas de los datos almacenados
- Estadísticas básicas por producto

Uso:
    python explore_db.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

def explore_database(db_path: str = "db/prices.db"):
    """Explora y muestra estadísticas básicas de la base de datos."""
    
    # Verificar que existe la base de datos
    if not Path(db_path).exists():
        print(f"❌ No se encontró la base de datos: {db_path}")
        return
    
    print("🔍 Explorando base de datos de precios...")
    print("=" * 50)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Número total de registros
        cursor.execute("SELECT COUNT(*) FROM prices")
        total_records = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total_records:,}")
        
        if total_records == 0:
            print("❌ No hay datos en la base de datos")
            return
        
        # 2. Productos únicos
        cursor.execute("SELECT COUNT(DISTINCT url) FROM prices")
        unique_products = cursor.fetchone()[0]
        print(f"🛍️  Productos únicos monitoreados: {unique_products}")
        
        # 3. Rango de fechas
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM prices")
        min_date, max_date = cursor.fetchone()
        
        if min_date and max_date:
            min_dt = datetime.fromisoformat(min_date)
            max_dt = datetime.fromisoformat(max_date)
            days_diff = (max_dt - min_dt).days
            
            print(f"📅 Primer registro: {min_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"📅 Último registro: {max_dt.strftime('%Y-%m-%d %H:%M')}")
            print(f"⏱️  Días de monitoreo: {days_diff} días")
        
        print("\n" + "=" * 50)
        print("📋 PRODUCTOS MONITOREADOS:")
        print("=" * 50)
        
        # 4. Lista de productos con estadísticas
        cursor.execute("""
            SELECT 
                name,
                url,
                COUNT(*) as total_registros,
                MIN(official_price) as precio_oficial_min,
                MAX(official_price) as precio_oficial_max,
                AVG(official_price) as precio_oficial_promedio,
                COUNT(CASE WHEN discounted_price IS NOT NULL THEN 1 END) as registros_con_descuento,
                MIN(timestamp) as primer_registro,
                MAX(timestamp) as ultimo_registro
            FROM prices 
            GROUP BY url, name
            ORDER BY total_registros DESC
        """)
        
        products = cursor.fetchall()
        
        for i, (name, url, count, min_price, max_price, avg_price, discount_count, first_date, last_date) in enumerate(products, 1):
            print(f"\n{i}. {name}")
            print(f"   📍 URL: {url[:60]}{'...' if len(url) > 60 else ''}")
            print(f"   📊 Registros: {count}")
            print(f"   💰 Precio oficial mín: ${min_price:,.0f}")
            print(f"   💰 Precio oficial máx: ${max_price:,.0f}")
            print(f"   💰 Precio oficial promedio: ${avg_price:,.0f}")
            print(f"   🏷️  Registros con descuento: {discount_count}/{count}")
            
            if first_date and last_date:
                first_dt = datetime.fromisoformat(first_date)
                last_dt = datetime.fromisoformat(last_date)
                days_monitored = (last_dt - first_dt).days
                print(f"   📅 Monitoreado por: {days_monitored} días")
        
        print("\n" + "=" * 50)
        print("📈 ÚLTIMOS 10 REGISTROS:")
        print("=" * 50)
        
        # 5. Últimos registros
        cursor.execute("""
            SELECT name, official_price, discounted_price, timestamp 
            FROM prices 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        recent_records = cursor.fetchall()
        
        for name, official_price, discounted_price, timestamp in recent_records:
            dt = datetime.fromisoformat(timestamp)
            if discounted_price:
                discount_str = f" 🏷️ Con descuento: ${discounted_price:,.0f}"
            else:
                discount_str = ""
            print(f"• {dt.strftime('%Y-%m-%d %H:%M')} - {name}: ${official_price:,.0f}{discount_str}")
        
        print("\n" + "=" * 50)
        print("💾 Exploración completada")

def main():
    """Función principal."""
    try:
        explore_database()
    except Exception as e:
        print(f"❌ Error explorando la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
