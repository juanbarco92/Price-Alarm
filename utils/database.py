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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    old_price REAL,
                    timestamp DATETIME NOT NULL,
                    UNIQUE(url, timestamp)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_url_timestamp 
                ON prices(url, timestamp DESC)
            """)
    
    def save_price(self, url: str, name: str, price: float, old_price: Optional[float] = None) -> None:
        """Guarda un precio en la base de datos."""
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO prices (url, name, price, old_price, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (url, name, price, old_price, timestamp))
                logger.info(f"Precio guardado: {name} - ${price}")
            except sqlite3.IntegrityError:
                logger.warning(f"Precio duplicado para {url} en {timestamp}")
    
    def get_last_price(self, url: str) -> Optional[float]:
        """Obtiene el último precio registrado para una URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT price FROM prices 
                WHERE url = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (url,))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_price_history(self, url: str, limit: int = 10) -> list:
        """Obtiene el historial de precios para una URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name, price, old_price, timestamp 
                FROM prices 
                WHERE url = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (url, limit))
            
            return cursor.fetchall()
