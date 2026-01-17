# ==============================================================================
# FGN Savings Bond Application - Makefile
# ==============================================================================
#
# Author: Hedgar Ajakaiye
# License: MIT
#
# Usage: make <target>
#
# Quick Start:
#   make setup    - First-time setup
#   make up       - Start all services (Docker)
#   make dev      - Start local development servers
#   make down     - Stop all services
#
# ==============================================================================

.PHONY: help setup up down restart logs build clean \
        dev dev-backend dev-frontend \
        test test-backend test-frontend \
        test-docker test-docker-backend test-docker-frontend test-docker-frontend-build \
        test-coverage lint lint-fix \
        shell-backend shell-frontend \
        db-backup db-restore \
        status health ps info hash secret

# Default target
.DEFAULT_GOAL := help

# Variables
COMPOSE_FILE := docker-compose.yml
BACKEND_DIR := backend
FRONTEND_DIR := frontend
BACKUP_DIR := ./backups

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ==============================================================================
# HELP
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)FGN Savings Bond Application$(NC)"
	@echo "$(BLUE)=============================$(NC)"
	@echo ""
	@echo "$(GREEN)Quick Start:$(NC)"
	@echo "  make setup        - First-time setup"
	@echo "  make up           - Start Docker services"
	@echo "  make dev          - Start local development"
	@echo "  make down         - Stop all services"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-18s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# SETUP & CONFIGURATION
# ==============================================================================

setup: ## First-time setup: install deps, create env, build images
	@echo "$(BLUE)Setting up FGN Bond Application...$(NC)"
	@# Backend setup
	@if [ ! -f $(BACKEND_DIR)/.env ]; then \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env 2>/dev/null || \
		echo "$(YELLOW)Create $(BACKEND_DIR)/.env from .env.example$(NC)"; \
	fi
	@mkdir -p $(BACKEND_DIR)/data $(BACKEND_DIR)/logs
	@# Frontend setup
	@if [ -d $(FRONTEND_DIR) ] && [ ! -d $(FRONTEND_DIR)/node_modules ]; then \
		echo "$(BLUE)Installing frontend dependencies...$(NC)"; \
		cd $(FRONTEND_DIR) && npm install; \
	fi
	@# Build Docker images
	@$(MAKE) build
	@echo ""
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "Run 'make up' for Docker or 'make dev' for local development"

env: ## Create .env files from examples
	@if [ ! -f $(BACKEND_DIR)/.env ]; then \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env; \
		echo "$(GREEN)Created $(BACKEND_DIR)/.env$(NC)"; \
	else \
		echo "$(YELLOW)$(BACKEND_DIR)/.env already exists$(NC)"; \
	fi

# ==============================================================================
# DOCKER COMPOSE
# ==============================================================================

up: ## Start all services (Docker)
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo ""
	@echo "$(GREEN)Services started!$(NC)"
	@echo "  App:      http://localhost"
	@echo "  Admin:    http://localhost/admin"
	@echo "  API:      http://localhost/api"
	@echo "  API Docs: http://localhost/api/docs"
	@sleep 3
	@$(MAKE) health

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart
	@$(MAKE) health

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)Build complete$(NC)"

rebuild: ## Rebuild Docker images (no cache)
	@echo "$(BLUE)Rebuilding Docker images (no cache)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "$(GREEN)Rebuild complete$(NC)"

logs: ## View logs (all services)
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## View backend logs
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## View frontend logs
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

logs-nginx: ## View nginx logs
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

# ==============================================================================
# LOCAL DEVELOPMENT
# ==============================================================================

dev: ## Start local development (backend + frontend)
	@echo "$(BLUE)Starting local development servers...$(NC)"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend...$(NC)"
	@cd $(BACKEND_DIR) && \
		if [ ! -d venv ]; then python3.12 -m venv venv; fi && \
		. venv/bin/activate && \
		pip install -q -r requirements.txt && \
		uvicorn app.main:app --reload --port 8000

dev-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	@cd $(BACKEND_DIR) && \
		if [ ! -d venv ]; then python3.12 -m venv venv; fi && \
		. venv/bin/activate && \
		pip install -r requirements.txt
	@echo "$(GREEN)Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)Frontend dependencies installed$(NC)"

# ==============================================================================
# STATUS & HEALTH
# ==============================================================================

ps: ## Show running containers
	docker-compose -f $(COMPOSE_FILE) ps

status: ps ## Alias for ps

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@printf "Backend:  "
	@curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo "DOWN"
	@echo ""
	@printf "Frontend: "
	@curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/ 2>/dev/null || echo "DOWN"
	@echo ""
	@printf "Nginx:    "
	@curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>/dev/null || echo "DOWN"
	@echo ""

# ==============================================================================
# TESTING
# ==============================================================================

test: test-backend test-frontend ## Run all tests (local)

test-backend: ## Run backend tests (local)
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate 2>/dev/null || true && \
		pytest tests/ -v

test-frontend: ## Run frontend tests (local)
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd $(FRONTEND_DIR) && npm run test:run

test-docker: test-docker-backend test-docker-frontend ## Run all tests (Docker)

test-docker-backend: ## Run backend tests via Docker
	@echo "$(BLUE)Running backend tests (Docker)...$(NC)"
	docker-compose run --rm backend pytest tests/ -v
	@echo "$(GREEN)Backend tests complete$(NC)"

test-docker-frontend: ## Run frontend tests via Docker
	@echo "$(BLUE)Running frontend tests (Docker)...$(NC)"
	docker-compose --profile test run --rm frontend-test
	@echo "$(GREEN)Frontend tests complete$(NC)"

test-docker-frontend-build: ## Build frontend test image
	@echo "$(BLUE)Building frontend test image...$(NC)"
	docker-compose --profile test build frontend-test
	@echo "$(GREEN)Frontend test image built$(NC)"

test-coverage: ## Run tests with coverage (local)
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate 2>/dev/null || true && \
		pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
	@cd $(FRONTEND_DIR) && npm run test:coverage
	@echo "$(GREEN)Coverage reports generated$(NC)"
	@echo "  Backend:  $(BACKEND_DIR)/htmlcov/index.html"
	@echo "  Frontend: $(FRONTEND_DIR)/coverage/index.html"

lint: ## Run linting checks
	@echo "$(BLUE)Running linting...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate 2>/dev/null || true && \
		pip install -q flake8 black isort && \
		flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics && \
		black --check app/ && \
		isort --check-only --profile black app/
	@cd $(FRONTEND_DIR) && npm run lint
	@echo "$(GREEN)Linting complete$(NC)"

lint-fix: ## Fix linting issues automatically
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate 2>/dev/null || true && \
		pip install -q black isort && \
		black app/ && \
		isort --profile black app/
	@cd $(FRONTEND_DIR) && npm run format 2>/dev/null || npm run lint -- --fix 2>/dev/null || true
	@echo "$(GREEN)Linting fixes applied$(NC)"

# ==============================================================================
# DATABASE
# ==============================================================================

db-backup: ## Backup SQLite database
	@mkdir -p $(BACKUP_DIR)
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	cp $(BACKEND_DIR)/data/fgn_bonds.db $(BACKUP_DIR)/fgn_bonds_$$TIMESTAMP.db 2>/dev/null && \
	echo "$(GREEN)Backup created: $(BACKUP_DIR)/fgn_bonds_$$TIMESTAMP.db$(NC)" || \
	echo "$(RED)No database file found$(NC)"

db-restore: ## Restore SQLite from latest backup
	@LATEST=$$(ls -t $(BACKUP_DIR)/fgn_bonds_*.db 2>/dev/null | head -1); \
	if [ -z "$$LATEST" ]; then \
		echo "$(RED)No backup files found in $(BACKUP_DIR)$(NC)"; \
		exit 1; \
	fi; \
	echo "$(BLUE)Restoring from: $$LATEST$(NC)"; \
	cp "$$LATEST" $(BACKEND_DIR)/data/fgn_bonds.db; \
	echo "$(GREEN)Restore complete$(NC)"

# ==============================================================================
# SHELL ACCESS
# ==============================================================================

shell-backend: ## Open shell in backend container
	docker-compose -f $(COMPOSE_FILE) exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose -f $(COMPOSE_FILE) exec frontend /bin/sh

shell-nginx: ## Open shell in nginx container
	docker-compose -f $(COMPOSE_FILE) exec nginx /bin/sh

# ==============================================================================
# CLEANUP
# ==============================================================================

clean: ## Remove containers, networks, and volumes
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-images: ## Remove Docker images
	@echo "$(YELLOW)Removing Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --rmi all
	@echo "$(GREEN)Images removed$(NC)"

clean-all: clean clean-images ## Full cleanup (containers, volumes, images)
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -rf $(BACKEND_DIR)/venv
	@rm -rf $(BACKEND_DIR)/__pycache__
	@echo "$(GREEN)Full cleanup complete$(NC)"

prune: ## Prune unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)Prune complete$(NC)"

# ==============================================================================
# UTILITIES
# ==============================================================================

hash: ## Generate bcrypt password hash (usage: make hash PASS=yourpassword)
	@if [ -z "$(PASS)" ]; then \
		echo "$(RED)Usage: make hash PASS=yourpassword$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)bcrypt hash for '$(PASS)':$(NC)"
	@python3 -c "import bcrypt; print(bcrypt.hashpw('$(PASS)'.encode(), bcrypt.gensalt()).decode())"

secret: ## Generate random secret key
	@echo "$(BLUE)Generated JWT_SECRET_KEY:$(NC)"
	@python3 -c "import secrets; print(secrets.token_hex(32))"

password: ## Generate random password
	@echo "$(BLUE)Generated password:$(NC)"
	@openssl rand -base64 24

validate: ## Validate docker-compose file
	@echo "$(BLUE)Validating docker-compose.yml...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) config -q && echo "$(GREEN)Valid$(NC)"

# ==============================================================================
# INFO
# ==============================================================================

info: ## Show project information
	@echo ""
	@echo "$(BLUE)FGN Savings Bond Application$(NC)"
	@echo "=============================="
	@echo ""
	@echo "$(GREEN)Architecture:$(NC)"
	@echo "  - Frontend: React + TypeScript + Tailwind"
	@echo "  - Backend:  FastAPI + SQLAlchemy + SQLite"
	@echo "  - Proxy:    Nginx"
	@echo ""
	@echo "$(GREEN)URLs (Docker):$(NC)"
	@echo "  - App:      http://localhost"
	@echo "  - Admin:    http://localhost/admin"
	@echo "  - API:      http://localhost/api"
	@echo "  - API Docs: http://localhost/api/docs"
	@echo ""
	@echo "$(GREEN)URLs (Local Dev):$(NC)"
	@echo "  - Frontend: http://localhost:5173"
	@echo "  - Backend:  http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "$(GREEN)Default Admin:$(NC)"
	@echo "  - Username: admin"
	@echo "  - Password: admin123"
	@echo ""
