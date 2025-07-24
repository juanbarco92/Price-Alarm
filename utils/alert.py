"""
Sistema de alertas por Telegram.
"""

import os
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramAlert:
    """Maneja el envío de alertas por Telegram."""
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv('TG_TOKEN')
        self.chat_id = chat_id or os.getenv('TG_CHAT_ID')
        
        if not self.token or not self.chat_id:
            raise ValueError("TG_TOKEN y TG_CHAT_ID son requeridos")
        
        self.bot = Bot(token=self.token)
    
    async def send_message(self, message: str) -> bool:
        """Envía un mensaje por Telegram."""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Alerta enviada por Telegram: {message}")
            return True
            
        except TelegramError as e:
            logger.error(f"Error enviando mensaje por Telegram: {e}")
            return False
    
    async def send_price_alert(self, product_name: str, old_price: float, 
                             new_price: float, url: str) -> bool:
        """Envía una alerta específica de precio."""
        discount_percent = ((old_price - new_price) / old_price) * 100
        
        message = f"""
🔥 <b>¡PRECIO REBAJADO!</b>

📦 <b>{product_name}</b>
💰 Precio anterior: <s>${old_price:,.0f}</s>
🎯 Precio actual: <b>${new_price:,.0f}</b>
📉 Descuento: <b>{discount_percent:.1f}%</b>

🛒 <a href="{url}">Ver producto</a>
        """
        
        return await self.send_message(message.strip())

def send_telegram_sync(message: str) -> bool:
    """Versión síncrona para compatibilidad."""
    import asyncio
    
    try:
        alerter = TelegramAlert()
        
        # Verificar si ya hay un loop corriendo
        try:
            loop = asyncio.get_running_loop()
            # Si hay un loop corriendo, usar run_until_complete en un nuevo hilo
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, alerter.send_message(message))
                return future.result()
        except RuntimeError:
            # No hay loop corriendo, usar asyncio.run directamente
            return asyncio.run(alerter.send_message(message))
            
    except Exception as e:
        logger.error(f"Error en alerta síncrona: {e}")
        return False

def send_price_alert_sync(product_name: str, old_price: float, 
                         new_price: float, url: str) -> bool:
    """Versión síncrona para alerta de precio."""
    import asyncio
    
    try:
        alerter = TelegramAlert()
        
        # Verificar si ya hay un loop corriendo
        try:
            loop = asyncio.get_running_loop()
            # Si hay un loop corriendo, usar run_until_complete en un nuevo hilo
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, alerter.send_price_alert(product_name, old_price, new_price, url))
                return future.result()
        except RuntimeError:
            # No hay loop corriendo, usar asyncio.run directamente
            return asyncio.run(alerter.send_price_alert(product_name, old_price, new_price, url))
            
    except Exception as e:
        logger.error(f"Error en alerta de precio síncrona: {e}")
        return False
