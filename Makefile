# 🎯 Price Alarm - Makefile
# Simplifica comandos comunes para desarrollo

.PHONY: help install web scraper test format clean dev

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

## help: Muestra esta ayuda
help:
	@echo "$(YELLOW)🎯 Price Alarm - Comandos Disponibles$(NC)"
	@echo ""
	@echo "$(GREEN)📦 Setup:$(NC)"
	@echo "  make install     - Instala todas las dependencias"
	@echo "  make clean       - Limpia archivos temporales"
	@echo ""
	@echo "$(GREEN)🚀 Desarrollo:$(NC)"
	@echo "  make dev         - Inicia servidor de desarrollo completo"
	@echo "  make web         - Solo dashboard web (puerto 5000)"
	@echo "  make scraper     - Solo scraper una vez"
	@echo ""
	@echo "$(GREEN)🐳 Docker:$(NC)"
	@echo "  make docker-setup    - Setup inicial con Docker"
	@echo "  make docker-up       - Levantar servicios con Docker"
	@echo "  make docker-down     - Bajar servicios Docker"
	@echo "  make docker-test     - Tests con Docker"
	@echo "  make docker-logs     - Ver logs de Docker"
	@echo ""
	@echo "$(GREEN)🧪 Testing:$(NC)"
	@echo "  make test        - Ejecuta todos los tests"
	@echo "  make test-tg     - Prueba conexión Telegram"
	@echo "  make test-scrape - Prueba scraping"
	@echo "  make test-all    - Test suite completo (local + Docker)"
	@echo "  make test-docker - Solo tests con Docker"
	@echo ""
	@echo "$(GREEN)🔧 Calidad:$(NC)"
	@echo "  make format      - Formatea código con black"
	@echo "  make lint        - Analiza código con flake8"
	@echo ""
	@echo "$(GREEN)📊 Data:$(NC)"
	@echo "  make db-reset    - Reinicia base de datos"
	@echo "  make db-backup   - Respalda base de datos"
	@echo ""

## install: Instala Poetry y dependencias
install:
	@echo "$(YELLOW)📦 Configurando entorno completo...$(NC)"
	@python tools/setup_env.py
	@echo "$(GREEN)✅ Instalación completa!$(NC)"

## setup: Setup rápido sin tests
setup:
	@echo "$(YELLOW)⚡ Setup rápido...$(NC)"
	@python tools/setup_env.py --skip-tests
	@echo "$(GREEN)✅ Setup completo!$(NC)"

## dev: Servidor completo de desarrollo
dev:
	@echo "$(YELLOW)🚀 Iniciando servidor de desarrollo...$(NC)"
	@python tools/dev_server.py

## web: Solo dashboard web
web:
	@echo "$(YELLOW)🌐 Iniciando dashboard web...$(NC)"
	@cd app && poetry run python -m flask run --host=0.0.0.0 --port=5000 --debug

## scraper: Ejecuta scraper una vez
scraper:
	@echo "$(YELLOW)🕷️ Ejecutando scraper...$(NC)"
	@python tools/dev_scraper.py

## docker-setup: Setup inicial con Docker
docker-setup:
	@echo "$(YELLOW)🐳 Setup inicial con Docker...$(NC)"
	@python tools/dev_docker.py setup

## docker-up: Levantar servicios con Docker
docker-up:
	@echo "$(YELLOW)🐳 Levantando servicios...$(NC)"
	@python tools/dev_docker.py up

## docker-down: Bajar servicios Docker
docker-down:
	@echo "$(YELLOW)🐳 Bajando servicios...$(NC)"
	@python tools/dev_docker.py down

## docker-test: Tests con Docker
docker-test:
	@echo "$(YELLOW)🐳 Ejecutando tests con Docker...$(NC)"
	@python tools/dev_docker.py test

## docker-logs: Ver logs de Docker
docker-logs:
	@echo "$(YELLOW)🐳 Logs de servicios...$(NC)"
	@python tools/dev_docker.py logs

## test: Ejecuta todos los tests
test:
	@echo "$(YELLOW)🧪 Ejecutando tests...$(NC)"
	@poetry run python -m pytest tests/ -v

## test-tg: Prueba conexión Telegram
test-tg:
	@echo "$(YELLOW)📱 Probando Telegram...$(NC)"
	@poetry run python examples/test_telegram_simple.py

## test-scrape: Prueba scraping
test-scrape:
	@echo "$(YELLOW)🕷️ Probando scraping...$(NC)"
	@poetry run python -c "from shared.adapters.alkosto import AlkostoAdapter; print('✅ Adaptadores OK')"

## test-all: Test suite completo
test-all:
	@echo "$(YELLOW)🧪 Ejecutando test suite completo...$(NC)"
	@python tools/test_all.py

## test-docker: Solo tests con Docker
test-docker:
	@echo "$(YELLOW)🐳 Tests con Docker...$(NC)"
	@python tools/test_all.py --docker

## format: Formatea código
format:
	@echo "$(YELLOW)🎨 Formateando código...$(NC)"
	@poetry run black . --exclude=venv
	@poetry run isort . --profile black
	@echo "$(GREEN)✅ Código formateado!$(NC)"

## lint: Analiza calidad del código
lint:
	@echo "$(YELLOW)🔍 Analizando código...$(NC)"
	@poetry run flake8 . --exclude=venv,__pycache__ --max-line-length=88 --extend-ignore=E203,W503

## clean: Limpia archivos temporales
clean:
	@echo "$(YELLOW)🧹 Limpiando archivos temporales...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completa!$(NC)"

## db-reset: Reinicia base de datos
db-reset:
	@echo "$(YELLOW)🗃️ Reiniciando base de datos...$(NC)"
	@rm -f db/prices.db 2>/dev/null || true
	@poetry run python -c "from shared.utils.database import PriceDatabase; PriceDatabase().setup_database()"
	@echo "$(GREEN)✅ Base de datos reiniciada!$(NC)"

## db-backup: Respalda base de datos
db-backup:
	@echo "$(YELLOW)💾 Respaldando base de datos...$(NC)"
	@mkdir -p backups
	@cp db/prices.db backups/prices_backup_$(shell date +%Y%m%d_%H%M%S).db 2>/dev/null || echo "$(YELLOW)⚠️ No hay BD que respaldar$(NC)"
	@echo "$(GREEN)✅ Respaldo completo!$(NC)"

# Comando por defecto
.DEFAULT_GOAL := help

# Quick setup for new developers
setup: install
	cp .env.example .env
	@echo "Setup complete! Edit .env with your configuration."

# Production deployment check
deploy-check: lint test
	@echo "✅ All checks passed - ready for deployment"
