.PHONY: help build up down restart logs shell clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image
	docker-compose build

up: ## Start the bot in detached mode
	docker-compose up -d

down: ## Stop the bot
	docker-compose down

restart: ## Restart the bot
	docker-compose restart

logs: ## Show bot logs (follow mode)
	docker-compose logs -f crypto-bot

logs-tail: ## Show last 100 lines of logs
	docker-compose logs --tail=100 crypto-bot

shell: ## Open a shell in the running container
	docker-compose exec crypto-bot /bin/bash

ps: ## Show running containers
	docker-compose ps

stop: ## Stop the bot without removing containers
	docker-compose stop

start: ## Start the bot (if stopped)
	docker-compose start

clean: ## Remove all containers, images, and volumes
	docker-compose down -v --rmi all

rebuild: ## Rebuild and restart the bot
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

status: ## Check the status of the bot
	@docker-compose ps
	@echo ""
	@docker-compose logs --tail=20 crypto-bot