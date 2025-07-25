# 🎯 Price Alarm

Sistema inteligente de monitoreo de precios con dashboard web y alertas automáticas por Telegram.

## 🚀 **¿Quieres empezar ya?**

### Para desarrollo local:
```bash
git clone https://github.com/juanbarco92/Price-Alarm.git
cd Price-Alarm
python dev_server.py  # ¡Todo automático!
```

**📖 [Ver guía completa de desarrollo local →](DESARROLLO_LOCAL.md)**

### Para producción:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## � **Descripción**

Price Alarm es un **sistema completo** de monitoreo de precios que incluye:
- 🌐 **Dashboard web** para visualización y administración
- 🕷️ **Scraper automático** que rastrea precios 24/7
- 📱 **Alertas inteligentes** por Telegram
- � **Análisis histórico** con gráficos y tendencias

### ✨ **¿Qué hace especial a Price Alarm?**
- **Arquitectura profesional:** Separación clara entre web app y scraper
- **Detección inteligente:** Distingue entre precios oficiales y promocionales
- **Escalable:** Fácil agregar nuevas tiendas y productos
- **Desplegable:** Lista para producción con Docker y Render.com

---

## 📋 **Características**

### 🌐 **Dashboard Web**
- Panel administrativo para gestión de productos
- Gráficos interactivos de evolución de precios
- API REST para integraciones
- Interfaz moderna con Chart.js

### 🕷️ **Scraping Inteligente**
- Playwright para sitios modernos (JS-heavy)
- Adaptadores específicos por tienda
- Cálculo automático de precio por unidad
- Detección de ofertas y descuentos

### 📊 **Base de Datos Semántica**
- Estructura jerárquica: Productos → Presentaciones → Tiendas
- Distinción clara: precio oficial vs precio promocional
- Histórico completo para análisis de tendencias
- Optimizada para consultas y reportes

### 📱 **Alertas Inteligentes**
- Telegram instantáneo cuando hay descuentos ≥ 10%
- Notificaciones de ofertas especiales ("precio tachado")
- Alertas de nuevos precios mínimos históricos
- Resúmenes programados

### Con pip tradicional:
```bash
# Activar entorno virtual primero
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Ejecutar una vez manualmente
python track.py

# Ver logs
tail -f logs/track.log
```

### Programación con cron:
```bash
# Ejecutar: crontab -e
# Agregar línea para Poetry:
0 * * * * cd /ruta/al/proyecto && poetry run python track.py

# O para pip tradicional:
0 * * * * cd /ruta/al/proyecto && source venv/bin/activate && python track.py
```

## Cómo obtener el Token de Telegram

1. **Crear un bot**:
   - Envía `/newbot` a [@BotFather](https://t.me/botfather)
   - Sigue las instrucciones y guarda el token

2. **Obtener tu Chat ID**:
   - Envía un mensaje a [@userinfobot](https://t.me/userinfobot)
   - O envía un mensaje a tu bot y visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`

## Agregar nuevas tiendas

Para soportar una nueva tienda, crea un archivo en `adapters/`:

```python
# adapters/nuevatienda.py
from typing import Optional, Tuple
from playwright.sync_api import Page

def get_price(page: Page, url: str) -> Tuple[str, float, Optional[float]]:
    """
    Returns: (product_name, current_price, old_price)
    """
    # Implementa la lógica de scraping específica
    pass
```

## Estructura del proyecto

```
discount_watcher/
├─ adapters/
│  ├─ __init__.py
│  └─ alkosto.py          # Scraper para Alkosto
├─ config/
│  └─ products.yml        # Configuración de productos
├─ db/                    # Base de datos SQLite (auto-creada)
├─ logs/                  # Archivos de log (auto-creados)  
├─ utils/
│  ├─ __init__.py
│  ├─ alert.py           # Notificaciones Telegram
│  └─ database.py        # Operaciones de BD
├─ track.py              # Script principal
├─ requirements.txt      # Dependencias Python
├─ .env.example         # Plantilla de variables de entorno
└─ README.md
```

## Logs y monitoreo

Los logs se guardan en `logs/track.log` y también se muestran en consola:

```bash
# Ver logs en tiempo real
tail -f logs/track.log

# Ver solo errores
grep ERROR logs/track.log
```

## Desarrollo

### Configuración para desarrollo:
```bash
# Instalar dependencias de desarrollo
poetry install

# Instalar pre-commit hooks (opcional)
poetry run pre-commit install

# Usar Makefile para comandos comunes
make help
make dev  # Configuración completa para desarrollo
```

### Comandos útiles:
```bash
# Formatear código
poetry run black .

# Linting
poetry run flake8 .
poetry run mypy .

# Ejecutar pruebas
poetry run pytest

# O usar Makefile
make format
make lint
make test
```

## Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Instala dependencias de desarrollo (`poetry install`)
4. Haz tus cambios y prueba (`make test lint`)
5. Commit tus cambios (`git commit -am 'Añade nueva característica'`)
6. Push a la rama (`git push origin feature/nueva-caracteristica`)
7. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

**juanbarco92** - [GitHub](https://github.com/juanbarco92)
