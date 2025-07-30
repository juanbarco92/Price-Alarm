"""
Utilidades para manejo de base de datos PostgreSQL.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional, List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class PriceDatabase:
    """Maneja las operaciones de base de datos para el sistema de precios."""
    
    def __init__(self):
        # Obtener configuración de variables de entorno
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'pricealarm')
        self.username = os.getenv('DB_USER', 'priceuser')
        self.password = os.getenv('DB_PASSWORD', 'pricepass')
        
        # String de conexión
        self.connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        # Crear tablas al inicializar
        self._create_tables()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos."""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password
        )
    
    def _create_tables(self) -> None:
        """Crea las tablas necesarias si no existen."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Tabla de productos
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS products (
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            alias TEXT UNIQUE NOT NULL
                        )
                    """)
                    
                    # Tabla de presentaciones
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS presentations (
                            id SERIAL PRIMARY KEY,
                            product_id INTEGER NOT NULL,
                            size TEXT NOT NULL,
                            unit_count INTEGER NOT NULL,
                            FOREIGN KEY (product_id) REFERENCES products(id)
                        )
                    """)
                    
                    # Tabla de tiendas/URLs
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS stores (
                            id SERIAL PRIMARY KEY,
                            presentation_id INTEGER NOT NULL,
                            store_name TEXT NOT NULL,
                            url TEXT UNIQUE NOT NULL,
                            FOREIGN KEY (presentation_id) REFERENCES presentations(id)
                        )
                    """)
                    
                    # Tabla de precios
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS prices (
                            id SERIAL PRIMARY KEY,
                            store_id INTEGER NOT NULL,
                            product_name TEXT NOT NULL,
                            official_price DECIMAL(10,2) NOT NULL,
                            discounted_price DECIMAL(10,2),
                            price_per_unit DECIMAL(10,2) NOT NULL,
                            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (store_id) REFERENCES stores(id)
                        )
                    """)
                    
                    # Índices para optimizar consultas
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_store_timestamp 
                        ON prices(store_id, timestamp DESC)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_product_timestamp 
                        ON prices(store_id, timestamp DESC)
                    """)
                    
                    conn.commit()
                    logger.info("Tablas de base de datos creadas/verificadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            raise
    
    def save_price(self, url: str, name: str, official_price: float, discounted_price: Optional[float] = None) -> None:
        """Guarda un precio en la base de datos."""
        timestamp = datetime.now()
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Obtener store_id de la URL
                    cursor.execute("SELECT id, presentation_id FROM stores WHERE url = %s", (url,))
                    store_result = cursor.fetchone()
                    
                    if not store_result:
                        logger.error(f"URL no encontrada en stores: {url}")
                        return
                    
                    store_id, presentation_id = store_result
                    
                    # Obtener unit_count para calcular precio por unidad
                    cursor.execute("SELECT unit_count FROM presentations WHERE id = %s", (presentation_id,))
                    unit_count_result = cursor.fetchone()
                    if not unit_count_result:
                        logger.error(f"Presentación no encontrada: {presentation_id}")
                        return
                    
                    unit_count = unit_count_result[0]
                    
                    # Calcular precio por unidad (usar precio con descuento si existe)
                    effective_price = discounted_price if discounted_price else official_price
                    price_per_unit = effective_price / unit_count
                    
                    # Insertar precio
                    cursor.execute("""
                        INSERT INTO prices (store_id, product_name, official_price, discounted_price, price_per_unit, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (store_id, name, official_price, discounted_price, price_per_unit, timestamp))
                    
                    if discounted_price:
                        logger.info(f"Precio guardado: {name} - Oficial: ${official_price:,.0f}, Con descuento: ${discounted_price:,.0f}, Por unidad: ${price_per_unit:,.0f}")
                    else:
                        logger.info(f"Precio guardado: {name} - ${official_price:,.0f}, Por unidad: ${price_per_unit:,.0f}")
                        
                    conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando precio para {url}: {e}")
    
    def get_or_create_product(self, name: str, alias: str) -> int:
        """Obtiene o crea un producto y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM products WHERE alias = %s", (alias,))
                    result = cursor.fetchone()
                    
                    if result:
                        return result[0]
                    
                    cursor.execute("INSERT INTO products (name, alias) VALUES (%s, %s) RETURNING id", (name, alias))
                    product_id = cursor.fetchone()[0]
                    conn.commit()
                    return product_id
        except Exception as e:
            logger.error(f"Error creando/obteniendo producto {alias}: {e}")
            raise
    
    def get_or_create_presentation(self, product_id: int, size: str, unit_count: int) -> int:
        """Obtiene o crea una presentación y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM presentations WHERE product_id = %s AND size = %s", 
                        (product_id, size)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        return result[0]
                    
                    cursor.execute(
                        "INSERT INTO presentations (product_id, size, unit_count) VALUES (%s, %s, %s) RETURNING id",
                        (product_id, size, unit_count)
                    )
                    presentation_id = cursor.fetchone()[0]
                    conn.commit()
                    return presentation_id
        except Exception as e:
            logger.error(f"Error creando/obteniendo presentación: {e}")
            raise
    
    def get_or_create_store(self, presentation_id: int, store_name: str, url: str) -> int:
        """Obtiene o crea una tienda y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM stores WHERE url = %s", (url,))
                    result = cursor.fetchone()
                    
                    if result:
                        return result[0]
                    
                    cursor.execute(
                        "INSERT INTO stores (presentation_id, store_name, url) VALUES (%s, %s, %s) RETURNING id",
                        (presentation_id, store_name, url)
                    )
                    store_id = cursor.fetchone()[0]
                    conn.commit()
                    return store_id
        except Exception as e:
            logger.error(f"Error creando/obteniendo store: {e}")
            raise
    
    def setup_product_hierarchy(self, product_config: dict) -> None:
        """Configura la jerarquía completa de un producto desde la configuración."""
        try:
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
        except Exception as e:
            logger.error(f"Error configurando jerarquía para {product_config.get('name', 'unknown')}: {e}")
            raise
    
    def get_last_price(self, url: str) -> Optional[float]:
        """Obtiene el último precio oficial registrado para una URL."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT p.official_price 
                        FROM prices p
                        JOIN stores s ON p.store_id = s.id
                        WHERE s.url = %s 
                        ORDER BY p.timestamp DESC 
                        LIMIT 1
                    """, (url,))
                    
                    result = cursor.fetchone()
                    return float(result[0]) if result else None
        except Exception as e:
            logger.error(f"Error obteniendo último precio para {url}: {e}")
            return None
    
    def get_price_history(self, url: str, limit: int = 10) -> List[Tuple]:
        """Obtiene el historial de precios para una URL."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT p.product_name, p.official_price, p.discounted_price, p.price_per_unit, p.timestamp
                        FROM prices p
                        JOIN stores s ON p.store_id = s.id
                        WHERE s.url = %s 
                        ORDER BY p.timestamp DESC 
                        LIMIT %s
                    """, (url, limit))
                    
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo historial de precios para {url}: {e}")
            return []
    
    def get_best_prices_per_unit(self, product_alias: str) -> List[Tuple]:
        """Obtiene los mejores precios por unidad para un producto específico."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            s.store_name,
                            pr.size,
                            MIN(p.price_per_unit) as min_price_per_unit,
                            p.timestamp
                        FROM prices p
                        JOIN stores s ON p.store_id = s.id
                        JOIN presentations pr ON s.presentation_id = pr.id
                        JOIN products prod ON pr.product_id = prod.id
                        WHERE prod.alias = %s
                        GROUP BY s.store_name, pr.size, p.timestamp
                        ORDER BY min_price_per_unit ASC
                        LIMIT 10
                    """, (product_alias,))
                    
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo mejores precios para {product_alias}: {e}")
            return []
    
    def create_product(self, name: str, alias: str) -> int:
        """Crea un nuevo producto y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO products (name, alias, created_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (name, alias))
                    
                    product_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Producto creado: {name} (ID: {product_id})")
                    return product_id
        except Exception as e:
            logger.error(f"Error creando producto {name}: {e}")
            raise
    
    def create_presentation(self, product_id: int, size: str, unit_count: int) -> int:
        """Crea una nueva presentación para un producto y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO presentations (product_id, size, unit_count, created_at)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (product_id, size, unit_count))
                    
                    presentation_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Presentación creada: {size} (ID: {presentation_id})")
                    return presentation_id
        except Exception as e:
            logger.error(f"Error creando presentación {size}: {e}")
            raise
    
    def create_store(self, presentation_id: int, store_name: str, url: str) -> int:
        """Crea una nueva tienda para una presentación y retorna su ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO stores (presentation_id, store_name, url, created_at)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (presentation_id, store_name, url))
                    
                    store_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Tienda creada: {store_name} (ID: {store_id})")
                    return store_id
        except Exception as e:
            logger.error(f"Error creando tienda {store_name}: {e}")
            raise
    
    def get_all_products_with_details(self) -> List[Dict]:
        """Obtiene todos los productos con sus presentaciones y tiendas."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Obtener productos
                    cursor.execute("SELECT * FROM products ORDER BY name")
                    products = cursor.fetchall()
                    
                    result = []
                    for product in products:
                        product_dict = dict(product)
                        
                        # Obtener presentaciones para este producto
                        cursor.execute("""
                            SELECT * FROM presentations 
                            WHERE product_id = %s 
                            ORDER BY size
                        """, (product['id'],))
                        presentations = cursor.fetchall()
                        
                        product_dict['presentations'] = []
                        for presentation in presentations:
                            pres_dict = dict(presentation)
                            
                            # Obtener tiendas para esta presentación
                            cursor.execute("""
                                SELECT * FROM stores 
                                WHERE presentation_id = %s 
                                ORDER BY store_name
                            """, (presentation['id'],))
                            stores = cursor.fetchall()
                            
                            pres_dict['stores'] = [dict(store) for store in stores]
                            product_dict['presentations'].append(pres_dict)
                        
                        result.append(product_dict)
                    
                    return result
        except Exception as e:
            logger.error(f"Error obteniendo productos con detalles: {e}")
            return []
    
    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto y todos sus datos relacionados."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Las eliminaciones en cascada se manejan por las FK constraints
                    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                    conn.commit()
                    logger.info(f"Producto eliminado: ID {product_id}")
                    return True
        except Exception as e:
            logger.error(f"Error eliminando producto {product_id}: {e}")
            return False
    
    def update_product(self, product_id: int, name: str = None, alias: str = None) -> bool:
        """Actualiza los datos de un producto."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    updates = []
                    params = []
                    
                    if name:
                        updates.append("name = %s")
                        params.append(name)
                    
                    if alias:
                        updates.append("alias = %s")
                        params.append(alias)
                    
                    if updates:
                        params.append(product_id)
                        query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
                        cursor.execute(query, params)
                        conn.commit()
                        logger.info(f"Producto actualizado: ID {product_id}")
                        return True
                    
                    return False
        except Exception as e:
            logger.error(f"Error actualizando producto {product_id}: {e}")
            return False
    
    def get_price_history_by_alias(self, product_alias: str, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de precios para un producto por su alias."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            p.product_name,
                            p.official_price,
                            p.discounted_price,
                            p.price_per_unit,
                            p.timestamp,
                            s.store_name,
                            s.url,
                            pr.size
                        FROM prices p
                        JOIN stores s ON p.store_id = s.id
                        JOIN presentations pr ON s.presentation_id = pr.id
                        JOIN products prod ON pr.product_id = prod.id
                        WHERE prod.alias = %s
                        ORDER BY p.timestamp DESC
                        LIMIT %s
                    """, (product_alias, limit))
                    
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo historial de precios para {product_alias}: {e}")
            return []
