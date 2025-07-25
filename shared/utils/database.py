"""
Utilidades para manejo de base de datos SQLite.
"""

import sqlite3
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PriceDatabase:
    """Maneja las operaciones de base de datos para el sistema de precios."""
    
    def __init__(self, db_path: str = "db/prices.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Crea las tablas necesarias si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabla de productos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    alias TEXT UNIQUE NOT NULL
                )
            """)
            
            # Tabla de presentaciones
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presentations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    size TEXT NOT NULL,
                    unit_count INTEGER NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Tabla de tiendas/URLs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    presentation_id INTEGER NOT NULL,
                    store_name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    FOREIGN KEY (presentation_id) REFERENCES presentations(id)
                )
            """)
            
            # Tabla de precios
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    official_price REAL NOT NULL,
                    discounted_price REAL,
                    price_per_unit REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (store_id) REFERENCES stores(id)
                )
            """)
            
            # Índices para optimizar consultas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_store_timestamp 
                ON prices(store_id, timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_timestamp 
                ON prices(store_id, timestamp DESC)
            """)
    
    def save_price(self, url: str, name: str, official_price: float, discounted_price: Optional[float] = None) -> None:
        """Guarda un precio en la base de datos."""
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                # Obtener store_id de la URL
                cursor = conn.execute("SELECT id, presentation_id FROM stores WHERE url = ?", (url,))
                store_result = cursor.fetchone()
                
                if not store_result:
                    logger.error(f"URL no encontrada en stores: {url}")
                    return
                
                store_id, presentation_id = store_result
                
                # Obtener unit_count para calcular precio por unidad
                cursor = conn.execute("SELECT unit_count FROM presentations WHERE id = ?", (presentation_id,))
                unit_count = cursor.fetchone()[0]
                
                # Calcular precio por unidad (usar precio con descuento si existe)
                effective_price = discounted_price if discounted_price else official_price
                price_per_unit = effective_price / unit_count
                
                conn.execute("""
                    INSERT INTO prices (store_id, product_name, official_price, discounted_price, price_per_unit, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (store_id, name, official_price, discounted_price, price_per_unit, timestamp))
                
                if discounted_price:
                    logger.info(f"Precio guardado: {name} - Oficial: ${official_price:,.0f}, Con descuento: ${discounted_price:,.0f}, Por unidad: ${price_per_unit:,.0f}")
                else:
                    logger.info(f"Precio guardado: {name} - ${official_price:,.0f}, Por unidad: ${price_per_unit:,.0f}")
                    
            except sqlite3.IntegrityError as e:
                logger.warning(f"Error guardando precio para {url}: {e}")
            except Exception as e:
                logger.error(f"Error inesperado guardando precio: {e}")
    
    def get_or_create_product(self, name: str, alias: str) -> int:
        """Obtiene o crea un producto y retorna su ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM products WHERE alias = ?", (alias,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor = conn.execute("INSERT INTO products (name, alias) VALUES (?, ?)", (name, alias))
            return cursor.lastrowid
    
    def get_or_create_presentation(self, product_id: int, size: str, unit_count: int) -> int:
        """Obtiene o crea una presentación y retorna su ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM presentations WHERE product_id = ? AND size = ?", 
                (product_id, size)
            )
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor = conn.execute(
                "INSERT INTO presentations (product_id, size, unit_count) VALUES (?, ?, ?)",
                (product_id, size, unit_count)
            )
            return cursor.lastrowid
    
    def get_or_create_store(self, presentation_id: int, store_name: str, url: str) -> int:
        """Obtiene o crea una tienda y retorna su ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM stores WHERE url = ?", (url,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor = conn.execute(
                "INSERT INTO stores (presentation_id, store_name, url) VALUES (?, ?, ?)",
                (presentation_id, store_name, url)
            )
            return cursor.lastrowid
    
    def setup_product_hierarchy(self, product_config: dict) -> None:
        """Configura la jerarquía completa de un producto desde la configuración."""
        product_id = self.get_or_create_product(product_config['name'], product_config['alias'])
        
        for presentation in product_config['presentations']:
            presentation_id = self.get_or_create_presentation(
                product_id, 
                presentation['size'], 
                presentation['unit_count']
            )
            
            for store in presentation['stores']:
                self.get_or_create_store(
                    presentation_id,
                    store['name'],
                    store['url']
                )
        
        logger.info(f"Jerarquía configurada para producto: {product_config['name']}")
    
    def get_last_price(self, url: str) -> Optional[float]:
        """Obtiene el último precio oficial registrado para una URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT p.official_price 
                FROM prices p
                JOIN stores s ON p.store_id = s.id
                WHERE s.url = ? 
                ORDER BY p.timestamp DESC 
                LIMIT 1
            """, (url,))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_price_history(self, url: str, limit: int = 10) -> list:
        """Obtiene el historial de precios para una URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT p.product_name, p.official_price, p.discounted_price, p.price_per_unit, p.timestamp
                FROM prices p
                JOIN stores s ON p.store_id = s.id
                WHERE s.url = ? 
                ORDER BY p.timestamp DESC 
                LIMIT ?
            """, (url, limit))
            
            return cursor.fetchall()
    
    def get_best_prices_per_unit(self, product_alias: str) -> list:
        """Obtiene los mejores precios por unidad para un producto específico."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
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
            """, (product_alias, product_alias))
            
            return cursor.fetchall()
