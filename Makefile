.PHONY: help start stop restart logs logs-backend logs-frontend logs-db test test-quick coverage seed migrate clean ps

help:
	@echo "Logs Dashboard - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "  make start       - Start all services (postgres, backend, frontend)"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Follow logs from all services"
	@echo "  make logs-backend - Follow backend logs only"
	@echo "  make logs-frontend - Follow frontend logs only"
	@echo "  make logs-db     - Follow database logs only"
	@echo "  make test        - Run all tests (backend + frontend)"
	@echo "  make test-quick  - Run tests excluding slow performance tests (fast feedback)"
	@echo "  make coverage    - Run all tests with coverage reports (HTML + terminal)"
	@echo "  make seed        - Populate database with 100k logs"
	@echo "  make migrate     - Run database migrations"
	@echo "  make clean       - Stop services and remove volumes (fresh start)"
	@echo "  make ps          - Show status of all services"
	@echo ""
	@echo "First time setup:"
	@echo "  1. cp .env.example .env"
	@echo "  2. Edit .env with your configuration"
	@echo "  3. make start"
	@echo ""

start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "  Backend API:  http://localhost:8000"
	@echo "  API Health:   http://localhost:8000/api/health"
	@echo "  API Docs:     http://localhost:8000/docs"
	@echo "  Frontend:     http://localhost:3000"
	@echo ""
	@echo "View logs with: make logs"

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

test:
	@echo "Running all tests (backend + frontend)..."
	@echo ""
	@echo "=== Backend Tests ==="
	docker-compose exec backend pytest tests/ -v
	@echo ""
	@echo "=== Frontend Tests ==="
	docker-compose exec frontend npm test -- --passWithNoTests
	@echo ""
	@echo "All tests complete!"

test-quick:
	@echo "Running quick tests (excluding slow performance tests)..."
	@echo ""
	@echo "=== Backend Quick Tests ==="
	docker-compose exec backend pytest tests/ -v -m "not slow"
	@echo ""
	@echo "=== Frontend Tests ==="
	docker-compose exec frontend npm test -- --passWithNoTests
	@echo ""
	@echo "Quick tests complete! (Performance tests skipped)"

coverage:
	@echo "Running tests with coverage reports..."
	@echo ""
	@echo "=== Backend Coverage ==="
	docker-compose exec backend pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov
	@echo ""
	@echo "=== Frontend Coverage ==="
	docker-compose exec frontend npm test -- --coverage --passWithNoTests
	@echo ""
	@echo "Coverage reports generated:"
	@echo "  Backend:  backend/htmlcov/index.html"
	@echo "  Frontend: frontend/coverage/lcov-report/index.html"
	@echo ""

seed:
	@echo "Seeding database with 100k logs (target: <60 seconds)..."
	docker-compose exec backend python scripts/seed.py

migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

clean:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v
	@echo "All services stopped and data removed."

ps:
	docker-compose ps
