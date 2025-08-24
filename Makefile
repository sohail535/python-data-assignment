.PHONY: api site test spark

api:
	uvicorn services.mock_api.app:app --reload --port 8000

site:
	cd services/mock_site && python -m http.server 8081

test:
	pytest -q
