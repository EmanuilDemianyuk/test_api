# Test_API

FastAPI backend for the shop API.

## System requirements

### Required components

- Docker and Docker Compose
- FastAPI (runs inside the container)
- MySQL 8.0
- phpMyAdmin (for visual database inspection)

### Optional

- Apache2 — **not required** for the current stack. Only needed if you want to expose the API through Apache as an external proxy.
- Python 3.12 — required only for local runs without Docker.

## Postman collection

The repository includes a ready-to-use request collection:

- `docs/postman/ShopAPI.postman_collection.json`

### How to import

1. Open Postman.
2. Click `Import`.
3. Select `docs/postman/ShopAPI.postman_collection.json`.
4. Make sure the `base_url` variable is set to `http://localhost:8000`.

### Seeded demo workflow

The application seeds a realistic demo catalog on startup by default (`AUTO_SEED_TEST_DATA=true`).

After importing the collection:

1. Run `GET /category` to populate `category_id` from the seeded categories when it is still empty.
2. Run `GET /product` to populate `product_id` from the seeded demo products.
3. Use `GET /product/{{product_id}}` to inspect a seeded demo item.
4. Use `POST /product` with the current `category_id` variable to create a new product linked to seeded demo data.

If you want to disable the seeded catalog, set `AUTO_SEED_TEST_DATA=false` in your `.env`.

### Base URL

- `http://localhost:8000`

## Start the server

### Option 1: Docker Compose

From the project root:

```bash
docker compose up --build
```

The API will be available at:

- http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Option 2: Local run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run tests

### Docker Compose

```bash
docker exec fastapi_app python -m pytest
```

### Local run

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

## Useful commands

### Rebuild Docker containers

```bash
docker compose up --build
```

### Stop containers

```bash
docker compose down
```

### Run a specific test file

```bash
docker exec fastapi_app python -m pytest tests/test_category_tree_usage.py -q -s
```

## Environment

The app uses `.env` for configuration. Make sure it exists in `backend/.env` before starting the containers.

## Database

- MySQL is started by Docker Compose
- phpMyAdmin is available at http://localhost:8080

## API endpoints for testing

### Categories

- `GET /category` — get a paginated list of categories
- `GET /category/{category_id}` — get a category by ID
- `POST /category` — create a category
- `PATCH /category/{category_id}` — update a category
- `DELETE /category/{category_id}` — delete a category

### Products

- `POST /product` — create a product
- `GET /product/{product_id}` — get a product by ID

### Health

- `GET /` — check API availability
