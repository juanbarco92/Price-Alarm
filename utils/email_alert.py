"""
Sistema de alertas por correo electrónico como alternativa a Telegram.
"""

import os
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional

logger = logging.getLogger(__name__)

class EmailAlert:
    """Maneja el envío de alertas por correo electrónico."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 email: str = None, password: str = None, to_email: str = None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.email = email or os.getenv('EMAIL_FROM')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.to_email = to_email or os.getenv('EMAIL_TO')
        
        if not all([self.email, self.password, self.to_email]):
            logger.warning("Configuración de email incompleta. Usando alertas por consola.")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_price_alert(self, product_name: str, old_price: float, 
                        new_price: float, url: str) -> bool:
        """Envía una alerta específica de precio por email."""
        if not self.enabled:
            return False
            
        discount_percent = ((old_price - new_price) / old_price) * 100
        
        subject = f"🔥 Precio rebajado: {product_name}"
        
        body = f"""
        <h2>¡Precio Rebajado!</h2>
        <p><strong>Producto:</strong> {product_name}</p>
        <p><strong>Precio anterior:</strong> <del>${old_price:,.0f}</del></p>
        <p><strong>Precio actual:</strong> <span style="color: green; font-size: 1.2em;">${new_price:,.0f}</span></p>
        <p><strong>Descuento:</strong> {discount_percent:.1f}%</p>
        <p><a href="{url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Producto</a></p>
        """
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.email
            msg['To'] = self.to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Alerta enviada por email: {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False

def send_email_alert_sync(product_name: str, old_price: float, 
                         new_price: float, url: str) -> bool:
    """Función simplificada para enviar alerta por email."""
    alerter = EmailAlert()
    return alerter.send_price_alert(product_name, old_price, new_price, url)
