"""
Script simple para probar la conexión con Telegram usando requests.
"""

import os
import requests
from dotenv import load_dotenv

def test_telegram():
    """Prueba simple de envío de mensaje por Telegram."""
    load_dotenv()
    
    token = os.getenv('TG_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Error: TG_TOKEN y TG_CHAT_ID deben estar configurados en .env")
        return False
    
    print(f"🔧 Probando Telegram...")
    print(f"📱 Chat ID: {chat_id}")
    print(f"🤖 Token: {token[:10]}...")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = """🚨 **PRUEBA DE ALERTA** 🚨

📦 Producto: Celular HONOR X5b Plus 256GB Purpura
💰 Precio actual: $599,900
💸 Precio anterior: $799,900
🎯 Descuento: 25.0% (¡Ahorro de $200,000!)

🔗 URL: https://www.alkosto.com/producto

✅ Sistema de alertas funcionando correctamente"""

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and result.get('ok'):
            print("✅ ¡Mensaje enviado exitosamente por Telegram!")
            print(f"📧 Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Error en respuesta de Telegram: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

def main():
    success = test_telegram()
    if success:
        print("\n🎉 ¡Telegram configurado correctamente!")
        print("💡 Tu sistema de alertas está listo para funcionar")
    else:
        print("\n💔 Hay problemas con la configuración de Telegram")
        print("🔧 Verifica el token y chat ID en el archivo .env")

if __name__ == "__main__":
    main()
