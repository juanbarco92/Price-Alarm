# 🎯 Price Alarm - Guía de Desarrollo Local

## 🚀 Ejecución Local Rápida

### 📋 **Prerequisitos**
- Python 3.11+
- Git

### ⚡ **Setup en 2 pasos**

1. **Clonar y configurar:**
   ```bash
   git clone https://github.com/juanbarco92/Price-Alarm.git
   cd Price-Alarm
   ```

2. **Ejecutar servidor de desarrollo:**
   ```bash
   python dev_server.py
   ```
   
   Este script automáticamente:
   - ✅ Instala Poetry si no lo tienes
   - ✅ Instala todas las dependencias
   - ✅ Crea archivo `.env` desde `.env.example`
   - ✅ Configura directorios necesarios
   - ✅ Inicia la aplicación web

3. **¡Listo!** Accede a:
   - 📱 **Dashboard:** http://localhost:5000
   - ⚙️ **Admin Panel:** http://localhost:5000/admin

### 🔧 **Configurar Telegram**

Edita el archivo `.env` que se creó automáticamente:

```bash
# Reemplaza con tus valores reales
TG_TOKEN=tu_bot_token_aqui
TG_CHAT_ID=tu_chat_id_aqui
```

**¿Cómo obtener estas credenciales?**
- 🤖 **Bot Token:** Habla con [@BotFather](https://t.me/botfather) → `/newbot`
- 🆔 **Chat ID:** Envía mensaje a tu bot → Visita `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`

### 🕷️ **Ejecutar Scraper**

```bash
# En otra terminal, ejecutar scraping una vez
python dev_scraper.py
```

## 🛠️ **Comandos de Desarrollo**

```bash
# Instalar dependencias manualmente
make install

# Solo web app
make web

# Solo scraper  
make scraper

# Tests
make test

# Formatear código
make format

# Ver todos los comandos
make help
```

## 📁 **Estructura del Proyecto**

```
price-alarm/
├── 🌐 app/                    # Flask web dashboard
│   ├── main.py               # API y rutas
│   └── templates/            # UI del dashboard
├── 🕷️ scraper/               # Lógica de web scraping
│   └── track.py             # Script principal
├── 📚 shared/                # Código común
│   ├── adapters/            # Adaptadores de sitios (Alkosto, etc.)
│   ├── config/              # Configuración de productos
│   └── utils/               # Base de datos y alertas
├── 🐳 infra/                 # Docker y deployment
└── 🧪 tests/                 # Tests
```

## 🎯 **¿Qué puedes hacer?**

### En el Dashboard (http://localhost:5000):
- Ver estadísticas de precios
- Gráficos de evolución
- Estado del sistema

### En el Admin Panel (http://localhost:5000/admin):
- Agregar nuevos productos
- Configurar alertas
- Ejecutar scraping manual

### Con el Scraper:
- Monitorear precios automáticamente
- Detectar ofertas promocionales
- Calcular precios por unidad
- Enviar alertas por Telegram

## 🔧 **Agregar Productos**

### Opción 1: Via Web (Recomendada)
1. Ve a http://localhost:5000/admin
2. Llena el formulario
3. ¡Listo!

### Opción 2: Editando YAML
Edita `shared/config/products.yml`:

```yaml
products:
  - name: "Pañales Pampers Cruisers T5"
    alias: "pampers_cruisers_t5"
    presentations:
      - size: "56 unidades"
        unit_count: 56
        stores:
          - name: "Alkosto"
            url: "https://www.alkosto.com/producto-url"
```

## 🐛 **Troubleshooting**

### Error: "Poetry no encontrado"
```bash
# Instalar Poetry
pip install poetry
```

### Error: "No se puede conectar a la base de datos"
```bash
# Crear directorio db
mkdir db
```

### Error: "Telegram token inválido"
- Verifica que `TG_TOKEN` y `TG_CHAT_ID` estén correctos en `.env`
- El bot debe estar iniciado (envía `/start` a tu bot)

### Error: "Playwright navegador no encontrado"
```bash
poetry run playwright install chromium
```

## 🚀 **¿Qué sigue?**

1. **Configura productos** en el admin panel
2. **Ejecuta el scraper** para recopilar datos iniciales
3. **Programa ejecución automática** (cron job local)
4. **Explora el código** para entender cómo funciona
5. **Contribute** al proyecto! 

## 📝 **Para desarrolladores**

### Agregar nueva tienda:
1. Crear adaptador en `shared/adapters/`
2. Registrar en `get_adapter_for_url()`
3. Probar con productos reales

### Estructura de datos:
- Precios oficiales vs promocionales
- Cálculo automático de precio por unidad
- Historial completo para análisis

¿Preguntas? ¡Abre un issue! 🙋‍♂️
