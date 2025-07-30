# 🎯 Price Alarm

Sistema inteligente de monitoreo de precios con dashboard web y alertas automáticas.

## 🚀 Inicio Rápido

### 🐳 **Docker (Única opción local)**

```bash
# 1. Clonar repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git
cd Price-Alarm

# 2. Setup inicial  
make setup

# 3. Desarrollo diario
make dev

# 4. Testing pre-deploy
make prod
```

**¡Listo!** Accede a http://localhost:5000

## 🛠️ **Comandos Disponibles**

```bash
make help       # 📋 Ver todos los comandos
make setup      # 📦 Configuración inicial
make dev        # 🛠️ Ambiente desarrollo (hot reload)
make prod       # 🏭 Ambiente producción (replica Render)
make test       # 🧪 Ejecutar tests
make scraper    # 🔍 Scraper manual
make logs       # 📄 Ver logs
make down       # 🔴 Parar servicios
make clean      # 🧹 Limpiar todo
```

## 🌐 Despliegue en Producción

El proyecto está configurado para **Render.com**:
- **Web Service**: Dashboard Flask con gunicorn
- **Cron Job**: Scraping automático a las 6 AM y 6 PM  
- **PostgreSQL**: Base de datos gestionada
- **Variables**: TG_TOKEN, TG_CHAT_ID en Render

## 📖 Documentación

- **[� Desarrollo con Docker](docs/DOCKER_DESARROLLO.md)** - Desarrollo con containers (recomendado)
- **[�📋 Guía completa de desarrollo](docs/DESARROLLO_LOCAL.md)** - Setup detallado, configuración, troubleshooting
- **[🏗️ Arquitectura](docs/ARQUITECTURA.md)** - Estructura del proyecto y decisiones técnicas  
- **[🐳 Deployment](docs/DEPLOYMENT.md)** - Guías de despliegue y producción

## 📁 Estructura del Proyecto

```
price-alarm/
├── 🌐 app/           # Flask web dashboard
├── 🕷️ scraper/       # Web scraping logic  
├── 📚 shared/        # Código común (utils, adapters, config)
├── 🐳 infra/         # Docker y deployment configs
├── 🧪 tests/         # Test suites
├── 🔧 tools/         # Scripts de desarrollo
├── 📋 examples/      # Scripts de ejemplo y testing
└── 📖 docs/          # Documentación completa
```

## ✨ Características

- **Dashboard web** para visualización y administración
- **Scraper automático** que rastrea precios 24/7  
- **Alertas inteligentes** por Telegram
- **Base de datos semántica** con histórico completo
- **Arquitectura profesional** separada en microservicios
- **Deploy automático** a Render.com con Docker

## 🤝 Contribuir

1. Fork el repositorio
2. Crea tu rama: `git checkout -b feature/nueva-caracteristica`
3. Commitea: `git commit -m 'Agrega nueva característica'`
4. Push: `git push origin feature/nueva-caracteristica`
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver [docs/LICENSE](docs/LICENSE)

---

**¿Preguntas?** Abre un [issue](https://github.com/juanbarco92/Price-Alarm/issues) 🙋‍♂️
