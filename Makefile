.PHONY: build up down logs clean test run-pipeline api site db-migrate db-downgrade db-revision db-history db-current

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf data/bronze/* data/silver/* data/gold/*

run-pipeline:
	docker-compose up -d postgres mock_api mock_website
	docker-compose run --rm pipeline

# Database migration commands
db-migrate:
	docker-compose run --rm migrations python scripts/manage_db.py upgrade

db-downgrade:
	docker-compose run --rm migrations python scripts/manage_db.py downgrade

db-revision:
	docker-compose run --rm migrations python scripts/manage_db.py revision --message "$(message)"

db-history:
	docker-compose run --rm migrations python scripts/manage_db.py history

db-current:
	docker-compose run --rm migrations python scripts/manage_db.py current

# Development commands for running services locally
api:
	uvicorn services.mock_api.app:app --reload --port 8000

site:
	cd services/mock_site && python -m http.server 8081

test:
	pytest -q
