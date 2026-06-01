# AI Music Producer — Makefile

.PHONY: help build up down logs test lint format clean migrate seed

# ─── Docker ────────────────────────────────────────────────────────

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-logs: ## Start all services and attach to logs
	docker-compose up

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes
	docker-compose down -v

restart: down up ## Restart all services

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View API gateway logs
	docker-compose logs -f api-gateway

logs-worker: ## View worker logs
	docker-compose logs -f midi-worker sound-worker mix-worker master-worker

ps: ## List running containers
	docker-compose ps

# ─── Development ───────────────────────────────────────────────────

dev-api: ## Run API gateway in development mode
	cd services/api-gateway && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard: ## Run admin dashboard in development mode
	cd frontend/admin-dashboard && npm run dev

# ─── Database ──────────────────────────────────────────────────────

migrate: ## Run database migrations
	docker-compose exec api-gateway alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Migration message: " msg; \
	docker-compose exec api-gateway alembic revision --autogenerate -m "$$msg"

seed: ## Seed database with initial data
	@echo "Seeding database..."
	@docker-compose exec -T postgres psql -U aimusic -d aimusic < migrations/seed.sql

psql: ## Open PostgreSQL console
	docker-compose exec postgres psql -U aimusic -d aimusic

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

# ─── Testing ───────────────────────────────────────────────────────

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests
	pytest tests/unit -v

test-integration: ## Run integration tests
	pytest tests/integration -v

# ─── Code Quality ──────────────────────────────────────────────────

lint: ## Run linters
	flake8 services/ shared/ --max-line-length=120
	pylint services/ shared/

format: ## Format code with black
	black services/ shared/ tests/

format-check: ## Check code formatting
	black --check services/ shared/ tests/

# ─── Maintenance ───────────────────────────────────────────────────

clean: ## Clean up generated files and Docker artifacts
	docker-compose down -v
	docker system prune -f
	rm -rf output/beats/* output/stems/* output/previews/* output/midi/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

update-deps: ## Update Python dependencies
	pip-compile services/api-gateway/requirements.in
	pip-compile services/composition-engine/requirements.in
	pip-compile services/sound-engine/requirements.in
	pip-compile services/mixing-engine/requirements.in
	pip-compile services/mastering-engine/requirements.in
	pip-compile services/quality-scoring/requirements.in
	pip-compile services/export-pipeline/requirements.in

# ─── Monitoring ────────────────────────────────────────────────────

flower: ## Open Flower (Celery monitor) in browser
	@echo "Flower available at http://localhost:5555"
	@python -m webbrowser http://localhost:5555

docs: ## Open API docs in browser
	@echo "API docs available at http://localhost:8000/docs"
	@python -m webbrowser http://localhost:8000/docs

dashboard: ## Open admin dashboard in browser
	@echo "Dashboard available at http://localhost:3000"
	@python -m webbrowser http://localhost:3000

# ─── Utilities ─────────────────────────────────────────────────────

backup-db: ## Backup PostgreSQL database
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U aimusic aimusic > backups/aimusic_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/"

shell-api: ## Open shell in API container
	docker-compose exec api-gateway bash

shell-worker: ## Open shell in worker container
	docker-compose exec midi-worker bash

# ─── Help ──────────────────────────────────────────────────────────

help: ## Show this help message
	@echo "AI Music Producer — Available Commands"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
