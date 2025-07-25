# 🐳 Desarrollo con Docker

Esta guía te ayuda a desarrollar Price Alarm usando Docker, lo cual es más realista y evita problemas de configuración local.

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git
cd Price-Alarm

# 2. Setup inicial (construye imágenes, inicia DB, configura todo)
python tools/dev_docker.py setup

# 3. Levantar todos los servicios
python tools/dev_docker.py up
```

**¡Listo!** Accede a http://localhost:5000

## 📋 Prerequisitos

- **Docker Desktop** - [Descargar aquí](https://www.docker.com/products/docker-desktop)
  - ⚠️ **IMPORTANTE**: Docker Desktop debe estar **corriendo** antes de continuar
  - En Windows: Inicia Docker Desktop desde el menú de inicio
  - Verifica que funcione: `docker --version`
- **Git** - Para clonar el repositorio
- **Python 3.11+** - Solo para ejecutar los scripts de desarrollo

## 🐳 Servicios Incluidos

El stack de Docker incluye:

### 🌐 **Web App** (Puerto 5000)
- Flask con hot reload para desarrollo
- Dashboard interactivo
- Panel de administración
- API REST

### 🗃️ **PostgreSQL** (Puerto 5432)
- Base de datos production-ready
- Datos persistentes en volumen Docker
- Usuario: `priceuser`, Password: `pricepass`, DB: `pricealarm`

### 📊 **Redis** (Puerto 6379)
- Cache y queue system
- Para funcionalidades futuras

### 🕷️ **Scraper** 
- Playwright con navegadores incluidos
- Ejecuta manualmente con comandos

## 🔧 Comandos Disponibles

### **Setup y Gestión**
```bash
# Setup inicial completo
python tools/dev_docker.py setup

# Construir solo las imágenes
python tools/dev_docker.py build

# Levantar servicios
python tools/dev_docker.py up

# Bajar servicios
python tools/dev_docker.py down

# Ver estado
python tools/dev_docker.py status
```

### **Desarrollo**
```bash
# Ver logs en tiempo real
python tools/dev_docker.py logs

# Acceder a shell del container web
python tools/dev_docker.py shell

# Ejecutar scraper una vez
python tools/dev_docker.py scraper
```

### **Testing**
```bash
# Ejecutar todos los tests
python tools/dev_docker.py test

# Tests específicos dentro del container
docker-compose exec web python -m pytest tests/unit/ -v
docker-compose exec web python -m pytest tests/integration/ -v
```

### **Mantenimiento**
```bash
# Reset completo (¡BORRA TODOS LOS DATOS!)
python tools/dev_docker.py reset
```

## 🔗 URLs de Desarrollo

Con los servicios levantados:

- **🌐 Dashboard:** http://localhost:5000
- **⚙️ Admin Panel:** http://localhost:5000/admin  
- **🔌 Health Check:** http://localhost:5000/health
- **🗃️ PostgreSQL:** `localhost:5432` (usuario: `priceuser`)
- **📊 Redis:** `localhost:6379`

## 📁 Desarrollo con Hot Reload

Los containers están configurados para **hot reload** en desarrollo:

```bash
# Los cambios en estos directorios se reflejan automáticamente:
./app/          # → Container web
./shared/       # → Ambos containers  
./scraper/      # → Container scraper
```

**No necesitas reconstruir** las imágenes cuando cambias código Python.

## 🐛 Debugging

### **Ver logs de servicios**
```bash
# Todos los servicios
docker-compose logs -f

# Solo web app
docker-compose logs -f web

# Solo base de datos
docker-compose logs -f db
```

### **Acceder a containers**
```bash
# Shell en web app
docker-compose exec web /bin/bash

# Shell en scraper
docker-compose exec scraper /bin/bash

# Conectar a PostgreSQL
docker-compose exec db psql -U priceuser -d pricealarm
```

### **Verificar salud de servicios**
```bash
# Estado de containers
docker-compose ps

# Health checks
docker-compose exec web curl http://localhost:5000/health
```

## 🔧 Configuración

### **Variables de Entorno**

El archivo `.env` se crea automáticamente con:

```bash
# Base de datos (automática para Docker)
DATABASE_URL=postgresql://priceuser:pricepass@db:5432/pricealarm

# Redis (automático para Docker)
REDIS_URL=redis://redis:6379/0

# ⚠️ CONFIGURA ESTOS MANUALMENTE:
TG_TOKEN=your_telegram_bot_token_here
TG_CHAT_ID=your_telegram_chat_id_here
```

### **Configurar Telegram**

1. Crea un bot con [@BotFather](https://t.me/botfather)
2. Obtén tu Chat ID enviando un mensaje al bot y visitando:  
   `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
3. Edita `.env` con tus valores reales

### **Agregar Productos**

Opción 1: **Via web** (http://localhost:5000/admin)
Opción 2: **Editando YAML** (`shared/config/products.yml`)

## 🔄 Workflow de Desarrollo

### **1. Desarrollo diario**
```bash
# Levantar servicios
make docker-up     # o python tools/dev_docker.py up

# Hacer cambios en el código
# (hot reload automático)

# Ver logs si es necesario
make docker-logs   # o python tools/dev_docker.py logs

# Al final del día
make docker-down   # o python tools/dev_docker.py down
```

### **2. Testing**
```bash
# Tests antes de commit
make docker-test   # o python tools/dev_docker.py test

# Tests específicos
docker-compose exec web python -m pytest tests/unit/test_adapters.py -v
```

### **3. Reset cuando sea necesario**
```bash
# Si algo se rompe
python tools/dev_docker.py reset
python tools/dev_docker.py setup
```

## 🆚 Docker vs Local

| Aspecto | Docker | Local Python |
|---------|--------|-------------|
| **Setup** | Automático, idéntico en todas las máquinas | Manual, puede variar |
| **Base de datos** | PostgreSQL (production-ready) | SQLite (simple) |
| **Dependencias** | Aisladas en containers | Pueden conflictuar |
| **Performance** | Ligeramente más lento | Más rápido |
| **Realismo** | Idéntico a producción | Diferente a producción |
| **Debugging** | Requiere docker exec | Directo en IDE |

## 🚀 Producción

Las mismas imágenes Docker se usan en producción:

```bash
# Build para producción
docker build -f infra/Dockerfile.web -t price-alarm-web .
docker build -f infra/Dockerfile.scraper -t price-alarm-scraper .

# Deploy en Render.com (automático vía render.yaml)
```

## 🤝 Contribuir

Al desarrollar con Docker:

1. Haz cambios en tu código local
2. Verifica con `make docker-test`
3. Commit y push
4. Las GitHub Actions ejecutarán los mismos tests con Docker

¡Tu código funcionará igual en desarrollo, testing y producción! 🎯
