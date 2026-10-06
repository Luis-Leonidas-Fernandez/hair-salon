.PHONY: build-frontend run dev test lint format

build-frontend:
	cd frontend && npm run build

run: build-frontend
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev:
	npx --yes concurrently -n "api,web" -c "blue,green" ". .venv/bin/activate && uvicorn app.main:app --reload --port 8000" "cd frontend && npm run dev"

test:
	. .venv/bin/activate && pytest -v

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format .