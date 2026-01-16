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
#   make setup    - First-time setup (copy .env, build images)
#   make up       - Start all services
#   make down     - Stop all services
#   make logs     - View logs
#
# ==============================================================================

.PHONY: help setup up down restart logs build clean \
        up-prod down-prod logs-prod \
        dev dev-web dev-admin \
        test lint security-scan \
        db-shell db-backup db-restore \
        shell-web shell-admin \
        status health ps

# Default target
.DEFAULT_GOAL := help

# Variables
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROD_FILE := docker-compose.prod.yml
IMAGE_NAME := fgn-bond-app
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
	@echo "  make setup     - First-time setup"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# SETUP & CONFIGURATION
# ==============================================================================

setup: ## First-time setup: copy .env and build images
	@echo "$(BLUE)Setting up FGN Bond Application...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)Created .env from .env.example$(NC)"; \
		echo "$(YELLOW)Please review and update .env with your settings$(NC)"; \
	else \
		echo "$(YELLOW).env already exists, skipping$(NC)"; \
	fi
	@$(MAKE) build
	@echo ""
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "Run 'make up' to start the application"

env: ## Create .env from .env.example if not exists
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)Created .env from .env.example$(NC)"; \
	else \
		echo "$(YELLOW).env already exists$(NC)"; \
	fi

# ==============================================================================
# DOCKER COMPOSE - DEVELOPMENT
# ==============================================================================

up: ## Start all services (development)
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo ""
	@echo "$(GREEN)Services started!$(NC)"
	@echo "  User App:  http://localhost"
	@echo "  Admin:     http://localhost:8080"
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

logs-web: ## View web app logs
	docker-compose -f $(COMPOSE_FILE) logs -f web

logs-admin: ## View admin app logs
	docker-compose -f $(COMPOSE_FILE) logs -f admin

logs-db: ## View MongoDB logs
	docker-compose -f $(COMPOSE_FILE) logs -f mongodb

logs-nginx: ## View Nginx logs
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

# ==============================================================================
# DOCKER COMPOSE - PRODUCTION
# ==============================================================================

up-prod: ## Start all services (production)
	@echo "$(BLUE)Starting production services...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) up -d
	@echo "$(GREEN)Production services started$(NC)"
	@$(MAKE) health-prod

down-prod: ## Stop production services
	@echo "$(BLUE)Stopping production services...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) down
	@echo "$(GREEN)Production services stopped$(NC)"

logs-prod: ## View production logs
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

build-prod: ## Build production images
	@echo "$(BLUE)Building production images...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) build
	@echo "$(GREEN)Production build complete$(NC)"

# ==============================================================================
# LOCAL DEVELOPMENT (without Docker)
# ==============================================================================

dev: ## Run both apps locally (requires MongoDB)
	@echo "$(YELLOW)Starting local development servers...$(NC)"
	@echo "Make sure MongoDB is running on localhost:27017"
	@$(MAKE) dev-web &
	@$(MAKE) dev-admin &
	@wait

dev-web: ## Run user app locally
	streamlit run src/streamlit_app.py --server.port=8501

dev-admin: ## Run admin app locally
	streamlit run src/admin_app.py --server.port=8502

install: ## Install Python dependencies
	pip install -r requirements.txt

venv: ## Create virtual environment
	python -m venv venv
	@echo "$(GREEN)Virtual environment created$(NC)"
	@echo "Activate with: source venv/bin/activate"

# ==============================================================================
# STATUS & HEALTH
# ==============================================================================

ps: ## Show running containers
	docker-compose -f $(COMPOSE_FILE) ps

status: ps ## Alias for ps

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@sleep 2
	@echo "Web App:  $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8501/_stcore/health 2>/dev/null || echo 'DOWN')"
	@echo "Admin:    $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8502/_stcore/health 2>/dev/null || echo 'DOWN')"
	@echo "Nginx:    $$(curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>/dev/null || echo 'DOWN')"
	@echo ""

health-prod: ## Check health of production services
	@echo "$(BLUE)Checking production health...$(NC)"
	@docker-compose -f $(COMPOSE_PROD_FILE) ps

# ==============================================================================
# DATABASE
# ==============================================================================

db-shell: ## Open MongoDB shell
	docker-compose -f $(COMPOSE_FILE) exec mongodb mongosh -u admin -p password --authenticationDatabase admin

db-backup: ## Backup MongoDB database
	@mkdir -p $(BACKUP_DIR)
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongodump \
		-u admin -p password --authenticationDatabase admin \
		--db fgn_bonds --archive > $(BACKUP_DIR)/backup_$$TIMESTAMP.archive; \
	echo "$(GREEN)Backup created: $(BACKUP_DIR)/backup_$$TIMESTAMP.archive$(NC)"

db-restore: ## Restore MongoDB from latest backup
	@LATEST=$$(ls -t $(BACKUP_DIR)/backup_*.archive 2>/dev/null | head -1); \
	if [ -z "$$LATEST" ]; then \
		echo "$(RED)No backup files found in $(BACKUP_DIR)$(NC)"; \
		exit 1; \
	fi; \
	echo "$(BLUE)Restoring from: $$LATEST$(NC)"; \
	docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongorestore \
		-u admin -p password --authenticationDatabase admin \
		--archive < $$LATEST; \
	echo "$(GREEN)Restore complete$(NC)"

# ==============================================================================
# SHELL ACCESS
# ==============================================================================

shell-web: ## Open shell in web container
	docker-compose -f $(COMPOSE_FILE) exec web /bin/bash

shell-admin: ## Open shell in admin container
	docker-compose -f $(COMPOSE_FILE) exec admin /bin/bash

shell-nginx: ## Open shell in nginx container
	docker-compose -f $(COMPOSE_FILE) exec nginx /bin/sh

# ==============================================================================
# TESTING & LINTING
# ==============================================================================

lint: ## Run linting checks
	@echo "$(BLUE)Running linting...$(NC)"
	@pip install flake8 -q
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "$(GREEN)Linting passed$(NC)"

lint-full: ## Run full linting (includes style)
	@echo "$(BLUE)Running full linting...$(NC)"
	@pip install flake8 -q
	flake8 src/ --count --max-complexity=10 --max-line-length=127 --statistics

test: ## Run tests (placeholder)
	@echo "$(YELLOW)No tests configured yet$(NC)"
	@echo "Add tests to tests/ directory"

security-scan: ## Run security scan on Docker image
	@echo "$(BLUE)Scanning for vulnerabilities...$(NC)"
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image $(IMAGE_NAME):latest

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
	@echo "$(GREEN)Full cleanup complete$(NC)"

prune: ## Prune unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)Prune complete$(NC)"

# ==============================================================================
# UTILITIES
# ==============================================================================

hash: ## Generate password hash (usage: make hash PASS=yourpassword)
	@if [ -z "$(PASS)" ]; then \
		echo "$(RED)Usage: make hash PASS=yourpassword$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)SHA-256 hash for '$(PASS)':$(NC)"
	@echo -n "$(PASS)" | shasum -a 256 | cut -d' ' -f1

secret: ## Generate random secret key
	@echo "$(BLUE)Generated SECRET_KEY:$(NC)"
	@python -c "import secrets; print(secrets.token_hex(32))"

password: ## Generate random password
	@echo "$(BLUE)Generated password:$(NC)"
	@openssl rand -base64 24

validate: ## Validate docker-compose files
	@echo "$(BLUE)Validating docker-compose.yml...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) config -q && echo "$(GREEN)Valid$(NC)"
	@echo "$(BLUE)Validating docker-compose.prod.yml...$(NC)"
	@docker-compose -f $(COMPOSE_PROD_FILE) config -q && echo "$(GREEN)Valid$(NC)"

# ==============================================================================
# INFO
# ==============================================================================

info: ## Show project information
	@echo ""
	@echo "$(BLUE)FGN Savings Bond Application$(NC)"
	@echo "=============================="
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@echo "  - Nginx (reverse proxy)"
	@echo "  - Web App (user form)"
	@echo "  - Admin Dashboard"
	@echo "  - MongoDB"
	@echo ""
	@echo "$(GREEN)URLs:$(NC)"
	@echo "  - User App:  http://localhost"
	@echo "  - Admin:     http://localhost:8080"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  - README.md"
	@echo "  - docs/SECURITY.md"
	@echo "  - docs/ADMIN_GUIDE.md"
	@echo ""
