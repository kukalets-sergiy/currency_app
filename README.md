# Currency App

Currency exchange monitoring application. Periodically fetches exchange rates from Monobank API and stores them in database.

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/kukalets-sergiy/currency_app.git
cd currency_app
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup .env
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. With Docker (recommended)
```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5. Without Docker
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # Terminal 1
celery -A core worker -l info  # Terminal 2
celery -A core beat -l info  # Terminal 3
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/currency/currencies/` | List all currencies with rates |
| GET | `/api/v1/currency/available/` | Available currencies to add |
| POST | `/api/v1/currency/currencies/add/` | Add currency to monitoring |
| GET | `/api/v1/currency/currencies/<code>/history/` | Currency history for period |
| PATCH | `/api/v1/currency/currencies/<code>/toggle/` | Enable/disable monitoring |
| GET | `/api/v1/currency/export/csv/` | Export rates to CSV |

## Documentation

- **Swagger UI:** http://localhost:8000/docs/
- **Admin Panel:** http://localhost:8000/admin/

## Tech Stack

- Python 3.12+
- Django 5.0
- Django Rest Framework
- Celery + Redis
- PostgreSQL
- drf-yasg (Swagger)

## Management Command

```bash
python manage.py export_currency_rates
```

## Features

- ✅ Periodic currency rate updates (every 1 minute)
- ✅ REST API with Swagger documentation
- ✅ Currency history tracking
- ✅ CSV export functionality
- ✅ Enable/disable currency monitoring
- ✅ PostgreSQL database with indexes
- ✅ Celery background tasks

## License

MIT

