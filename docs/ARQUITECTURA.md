# 🏗️ Arquitectura del Sistema

## 🎯 Visión General

Price Alarm está diseñado como un **sistema distribuido** con arquitectura de microservicios que permite escalabilidad y mantenimiento independiente.

## 📋 Principios de Diseño

### 🔄 **Separación de Responsabilidades**
- **App**: Interfaz web, API REST, administración
- **Scraper**: Web scraping, procesamiento de datos, alertas
- **Shared**: Código común, modelos, utilidades

### 📊 **Base de Datos Semántica**
```
Products (Producto conceptual)
    ↓
Presentations (Talla/peso específico)
    ↓ 
Stores (Tienda específica)
    ↓
Prices (Precio específico en momento dado)
```

### 🌐 **API-First**
- REST API para todas las operaciones
- Interfaz web construida sobre la API
- Fácil integración con sistemas externos

## 📁 Estructura Detallada

```
price-alarm/
├── 🌐 app/                    # Flask Web Application
│   ├── main.py               # Factory pattern, rutas principales
│   ├── api/                  # API REST endpoints
│   │   ├── products.py       # CRUD productos
│   │   ├── prices.py         # Consultas de precios
│   │   └── admin.py          # Operaciones administrativas
│   ├── templates/            # Jinja2 templates
│   │   ├── dashboard.html    # Panel principal
│   │   ├── admin.html        # Panel administrativo
│   │   └── components/       # Componentes reutilizables
│   └── static/               # CSS, JS, imágenes
│       ├── css/
│       ├── js/
│       └── img/
│
├── 🕷️ scraper/               # Web Scraping Logic
│   ├── track.py             # Script principal de scraping
│   ├── scheduler.py         # Programación automática
│   └── processors/          # Procesadores específicos
│       ├── price_processor.py
│       └── alert_processor.py
│
├── 📚 shared/                # Código Común
│   ├── models/              # Modelos de datos
│   │   ├── product.py       # Producto, Presentación
│   │   ├── store.py         # Tienda
│   │   └── price.py         # Precio, Histórico
│   ├── adapters/            # Adaptadores por tienda
│   │   ├── base.py          # Adaptador base
│   │   ├── alkosto.py       # Implementación Alkosto
│   │   └── falabella.py     # Implementación Falabella (futuro)
│   ├── utils/               # Utilidades comunes
│   │   ├── database.py      # Gestión de BD
│   │   ├── alert.py         # Sistema de alertas
│   │   └── email_alert.py   # Alertas por email
│   └── config/              # Configuración
│       ├── products.yml     # Definición de productos
│       └── settings.py      # Settings globales
│
├── 🐳 infra/                 # Infrastructure as Code
│   ├── Dockerfile.web       # Container web app
│   ├── Dockerfile.scraper   # Container scraper
│   ├── docker-compose.yml   # Desarrollo local
│   └── k8s/                 # Kubernetes manifests (futuro)
│
├── 🧪 tests/                 # Test Suites
│   ├── unit/                # Tests unitarios
│   ├── integration/         # Tests de integración
│   └── e2e/                 # Tests end-to-end
│
├── 🔧 tools/                 # Development Tools
│   ├── dev_server.py        # Servidor de desarrollo
│   ├── dev_scraper.py       # Scraper de desarrollo
│   ├── migrate_data.py      # Migraciones de datos
│   └── setup_env.py         # Setup del entorno
│
├── 📋 examples/              # Ejemplos y Testing
│   ├── test_telegram.py     # Pruebas de Telegram
│   ├── test_adapters.py     # Pruebas de adaptadores
│   └── sample_configs/      # Configuraciones de ejemplo
│
└── 📖 docs/                  # Documentación
    ├── DESARROLLO_LOCAL.md   # Guía de desarrollo
    ├── ARQUITECTURA.md       # Este archivo
    ├── DEPLOYMENT.md         # Guías de despliegue
    └── API.md               # Documentación de API
```

## 🔄 Flujo de Datos

### 1. **Configuración**
```yaml
# shared/config/products.yml
products:
  - name: "Pañales Pampers"
    presentations:
      - size: "T5 - 56 unidades"
        stores:
          - name: "Alkosto"
            url: "https://..."
```

### 2. **Scraping Process**
```python
# scraper/track.py
for product in products:
    for presentation in product.presentations:
        for store in presentation.stores:
            adapter = get_adapter(store.url)
            price_data = adapter.extract_price(store.url)
            save_price(presentation, store, price_data)
            check_alerts(price_data)
```

### 3. **Alert System**
```python
# shared/utils/alert.py
if price_drop >= 10% or is_special_offer:
    send_telegram_alert(product, old_price, new_price)
    log_alert(alert_data)
```

### 4. **Web Dashboard**
```python
# app/main.py
@app.route('/api/prices/<product_id>')
def get_prices(product_id):
    prices = db.get_price_history(product_id)
    return jsonify(prices)
```

## 🔧 Tecnologías

### **Backend**
- **Python 3.11**: Lenguaje principal
- **Flask**: Framework web ligero y flexible
- **Playwright**: Scraping de sitios modernos (JS-heavy)
- **SQLite/PostgreSQL**: Base de datos (SQLite dev, PostgreSQL prod)
- **Poetry**: Gestión de dependencias

### **Frontend**
- **Jinja2**: Templates del lado del servidor
- **Chart.js**: Gráficos interactivos
- **Bootstrap**: Framework CSS
- **JavaScript vanilla**: Interactividad

### **DevOps**
- **Docker**: Containerización
- **Render.com**: Deployment cloud
- **GitHub Actions**: CI/CD (futuro)

## 🚀 Escalabilidad

### **Horizontal Scaling**
- Múltiples instancias de scraper para diferentes tiendas
- Load balancer para la web app
- Queue system para scraping masivo (Redis/Celery)

### **Vertical Scaling**
- Optimización de queries de BD
- Caching con Redis
- CDN para assets estáticos

## 🔐 Consideraciones de Seguridad

### **API Security**
- Rate limiting por IP
- API keys para acceso programático
- Validación de inputs

### **Scraping Ethics**
- Respeto a robots.txt
- Rate limiting en requests
- User-Agent rotation

### **Data Privacy**
- No almacenamiento de datos personales
- Logs con información mínima
- Encriptación de tokens/keys

## 🔮 Roadmap Técnico

### **Fase 1: Core Features** ✅
- [x] Scraping básico
- [x] Base de datos semántica
- [x] Alertas por Telegram
- [x] Dashboard web

### **Fase 2: Escalabilidad** 🚧
- [ ] Queue system (Celery + Redis)
- [ ] API authentication
- [ ] Multiple stores support
- [ ] Performance optimizations

### **Fase 3: Enterprise** 🔮
- [ ] Kubernetes deployment
- [ ] Microservices architecture
- [ ] Event sourcing
- [ ] Analytics dashboard

## 🤝 Contribuciones

### **Para agregar nueva tienda:**
1. Crear adaptador en `shared/adapters/nueva_tienda.py`
2. Implementar interface `BaseAdapter`
3. Registrar en `get_adapter_for_url()`
4. Agregar tests

### **Para agregar nueva funcionalidad:**
1. Identificar qué servicio la debe contener
2. Implementar en el servicio apropiado
3. Agregar tests
4. Actualizar documentación

Este diseño permite que Price Alarm crezca de un script simple a una plataforma empresarial manteniendo limpieza y flexibilidad. 🎯
