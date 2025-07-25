# 🎯 Price Alarm

Sistema inteligente de monitoreo de precios con dashboard web y alertas automáticas.

## 🚀 Inicio Rápido

### 🐳 **Con Docker (Recomendado)**
```bash
# 0. Asegúrate de que Docker Desktop esté corriendo
# 1. Clonar repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git
cd Price-Alarm

# 2. Setup y ejecutar con Docker
python tools/dev_docker.py setup
python tools/dev_docker.py up
```

### 🐍 **Con Python local**
```bash
# 1. Clonar repositorio
git clone https://github.com/juanbarco92/Price-Alarm.git
cd Price-Alarm

# 2. Ejecutar servidor de desarrollo
python tools/dev_server.py
```

**¡Listo!** Accede a http://localhost:5000

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
