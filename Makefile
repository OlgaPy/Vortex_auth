.PHONY: build bash shell migrate

build:
	docker-compose build --no-cache

bash:
	docker-compose exec kapibara-auth bash

shell:
	docker-compose exec kapibara-auth ipython

migrate:
	docker-compose run kapibara-auth alembic upgrade head
