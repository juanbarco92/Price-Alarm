# Price Alarm

Un sistema inteligente de monitoreo de precios que rastrea productos en tiendas en línea y envía alertas por Telegram cuando detecta descuentos significativos.

## Descripción

Price Alarm es un script Python que monitorea automáticamente los precios de productos en diferentes tiendas en línea (inicialmente Alkosto) y te envía notificaciones por Telegram cuando:
- El precio baja ≥ 10%
- Aparece un "precio tachado" (oferta especial)

## Características

- 🕷️ **Web Scraping robusto** con Playwright (maneja sitios JS-heavy)
- 📊 **Persistencia de datos** con SQLite para histórico de precios
- 📱 **Alertas por Telegram** instantáneas
- 🔧 **Fácil configuración** vía archivos YAML
- 🏪 **Arquitectura extensible** para agregar nuevas tiendas
- ⏰ **Programación automática** con cron
- 🛡️ **Manejo de errores** con reintentos automáticos

## Instalación

### Opción 1: Con Poetry (Recomendado)

```bash
# Clona el repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git

# Navega al directorio del proyecto
cd Price-Alarm

# Instala Poetry si no lo tienes
curl -sSL https://install.python-poetry.org | python3 -

# Instala todas las dependencias (incluido el entorno virtual)
poetry install

# Instala los navegadores de Playwright
poetry run playwright install

# Crea el archivo de configuración de entorno
cp .env.example .env
```

### Opción 2: Con pip tradicional

```bash
# Clona el repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git

# Navega al directorio del proyecto
cd Price-Alarm

# Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias Python
pip install -r requirements.txt

# Instala los navegadores de Playwright
playwright install

# Crea el archivo de configuración de entorno
cp .env.example .env
```

## Configuración

1. **Variables de entorno** (`.env`):
```bash
TG_TOKEN=tu_bot_token_de_telegram
TG_CHAT_ID=tu_chat_id_de_telegram
```

2. **Configurar productos** (`config/products.yml`):
```yaml
- url: https://www.alkosto.com/panal-pampers-cruisers-360-fit-s5-56-unidades/p/037000715078
  alias: pampers_cruisers_t5
- url: https://www.alkosto.com/otro-producto/p/123456789
  alias: producto_ejemplo
```

## Uso

### Con Poetry:
```bash
# Ejecutar una vez manualmente
poetry run python track.py

# O usando el script definido
poetry run price-alarm

# Pruebas de configuración
poetry run python setup.py --test-telegram
poetry run python setup.py --test-scraping
poetry run python setup.py --show-history

# Ver logs
tail -f logs/track.log
```

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
