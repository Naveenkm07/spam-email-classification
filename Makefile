COMPOSE = docker compose

.PHONY: build up test stop

# Build Docker images for all services
build:
	$(COMPOSE) build

# Start app, database, and admin UI
up:
	$(COMPOSE) up --build

# Run pytest inside the app container with coverage
test:
	$(COMPOSE) run --rm app pytest

# Stop and remove containers, networks, but keep volumes (DB data, models)
stop:
	$(COMPOSE) down
