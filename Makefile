.PHONY: build run bash shell migrate test

build:
	docker-compose build --no-cache

run:
	docker-compose up

bash:
	docker-compose exec kapibara-auth bash

shell:
	docker-compose exec kapibara-auth ipython

migrate:
	docker-compose run kapibara-auth alembic upgrade head

test:
	docker-compose run kapibara-auth pytest
