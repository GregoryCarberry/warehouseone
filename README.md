# WarehouseOne Backend (Flask + Postgres) — v2

Robust scaffold with:
- Flask 3, SQLAlchemy, Flask-Migrate (Alembic), Postgres 16
- Server-side sessions (filesystem at /tmp)
- Self-healing migrations at container start
- Permissions (many-to-many with validity)
- Products API (`GET /products` with `q`, `limit`, `offset`)
- Seed script (root user + 100 products)
- Docker Compose

## Quick Start
cp .env.example .env
docker compose up --build
docker compose exec backend python -m seed.seed_data

## Test
curl -s http://localhost:5000/health/ | jq .
curl -s -c cookies.txt -H 'Content-Type: application/json' -d '{"username":"root","password":"rootpass"}' http://localhost:5000/auth/login | jq .
curl -s http://localhost:5000/products/?limit=5 | jq .
