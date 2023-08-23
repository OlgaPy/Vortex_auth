.PHONY: build bash migrations migrate
build:
	docker-compose build --no-cache

bash:
	docker-compose exec kapibara-auth bash

migrate:
	docker-compose run kapibara-auth alembic upgrade head
