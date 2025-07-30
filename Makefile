# 🎯 Price Alarm - Makefile
# Comandos para desarrollo y producción con Docker

.PHONY: help setup dev dev-build dev-up prod test scraper logs down clean

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

## help: Mostrar ayuda
help:
	@echo "$(YELLOW)🎯 Price Alarm - Comandos Docker$(NC)"
	@echo ""
	@echo "$(GREEN)📦 Setup:$(NC)"
	@echo "  make setup       - Configuración inicial"
	@echo ""
	@echo "$(GREEN)🛠️  Desarrollo:$(NC)"
	@echo "  make dev         - Ambiente desarrollo (hot reload)"
	@echo "  make dev-build   - Solo construir imágenes sin ejecutar"
	@echo "  make dev-up      - Ejecutar sin reconstruir"
	@echo "  make scraper     - Ejecutar scraper manualmente"
	@echo "  make test        - Ejecutar tests"
	@echo ""
	@echo "$(GREEN)🏭 Producción:$(NC)"
	@echo "  make prod        - Simular ambiente producción (replica Render)"
	@echo ""
	@echo "$(GREEN)📋 Utilidades:$(NC)"
	@echo "  make logs        - Ver logs en tiempo real"
	@echo "  make down        - Parar servicios"
	@echo "  make clean       - Limpiar todo (containers + volúmenes)"

## setup: Configuración inicial
setup:
	@echo "$(YELLOW)📦 Configuración inicial...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env && \
		echo "$(GREEN)✅ Archivo .env creado$(NC)"; \
		echo "$(YELLOW)⚠️  EDITA .env con tus tokens de Telegram$(NC)"; \
	else \
		echo "$(GREEN)✅ .env ya existe$(NC)"; \
	fi
	@echo "$(GREEN)✅ Setup completo$(NC)"

## dev: Ambiente desarrollo
dev:
	@echo "$(YELLOW)🛠️  Iniciando ambiente desarrollo...$(NC)"
	@echo "$(YELLOW)📋 Con hot reload y debug habilitado$(NC)"
	@echo "$(YELLOW)📦 Construyendo imágenes y levantando servicios...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

## dev-build: Solo construir imágenes
dev-build:
	@echo "$(YELLOW)🔨 Construyendo imágenes de desarrollo...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --progress=plain

## dev-up: Ejecutar sin reconstruir
dev-up:
	@echo "$(YELLOW)🚀 Iniciando servicios (sin rebuild)...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

## prod: Ambiente producción (simula Render)
prod:
	@echo "$(YELLOW)🏭 Iniciando ambiente producción...$(NC)"
	@echo "$(YELLOW)📋 Simula Render: gunicorn + scheduler automático$(NC)"
	@echo "$(YELLOW)📦 Construyendo imágenes y levantando servicios...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

## test: Ejecutar tests
test:
	@echo "$(YELLOW)🧪 Ejecutando tests...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm web python -m pytest tests/ -v

## scraper: Ejecutar scraper manualmente
scraper:
	@echo "$(YELLOW)🔍 Ejecutando scraper...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm scraper python scraper/track.py

## logs: Ver logs en tiempo real
logs:
	@echo "$(YELLOW)📄 Logs en tiempo real...$(NC)"
	docker-compose logs -f

## down: Parar servicios
down:
	@echo "$(YELLOW)🔴 Parando servicios...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

## clean: Limpiar todo
clean:
	@echo "$(YELLOW)🧹 Limpiando containers, volúmenes e imágenes...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --rmi local
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --rmi local
	docker system prune -f
	@echo "$(GREEN)✅ Limpieza completa$(NC)"

# Comando por defecto
.DEFAULT_GOAL := help
