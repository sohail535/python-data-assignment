# Senior Python Data Engineer

Functions are intentionally left as `pass` or `NotImplementedError`. Your task is to implement them.

## Quickstart (suggested)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# run mock API and site in two terminals
uvicorn services.mock_api.app:app --reload --port 8000
cd services/mock_site && python -m http.server 8081

# run your flow (once implemented)
PYTHONPATH=. python -m orchestration.prefect.flow
```

See **ASSIGNMENT.md** for detailed requirements.
