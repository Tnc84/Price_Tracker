# 🇷🇴 Romanian Price Tracker - Backend

FastAPI backend for tracking product prices across major Romanian retailers.

## Supported Retailers

- **eMAG** - https://www.emag.ro (Romania's largest marketplace)
- **Altex** - https://www.altex.ro (Electronics & appliances)
- **Carrefour** - https://www.carrefour.ro (Supermarket)
- **Kaufland** - https://www.kaufland.ro (Supermarket)
- **Selgros** - https://www.selgros.ro (Cash & Carry)

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services
cd ..
docker-compose up -d

# Check logs
docker-compose logs -f backend

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run application
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

## API Endpoints

### Products

- `POST /api/v1/products/` - Create a new product
- `GET /api/v1/products/` - List all products
- `GET /api/v1/products/{id}` - Get product with prices
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/{id}/scrape` - Scrape prices

### Prices

- `GET /api/v1/prices/comparison/{product_id}` - Price comparison
- `GET /api/v1/prices/history/{product_id}` - Price history
- `GET /api/v1/prices/deals` - Promotional deals

### Scraper

- `GET /api/v1/scraper/retailers` - List supported retailers
- `GET /api/v1/scraper/search` - Search without saving

## Example Usage

### 1. Create a Product

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cafea Jacobs Cronat Gold 200g",
    "category": "Alimente",
    "brand": "Jacobs",
    "target_price": 25.00
  }'
```

### 2. Scrape Prices

```bash
curl -X POST "http://localhost:8000/api/v1/products/1/scrape"
```

### 3. Get Price Comparison

```bash
curl "http://localhost:8000/api/v1/prices/comparison/1"
```

Response:
```json
{
  "product_id": 1,
  "product_name": "Cafea Jacobs Cronat Gold 200g",
  "lowest_price": 24.99,
  "highest_price": 32.50,
  "average_price": 28.25,
  "price_range": 7.51,
  "savings_percentage": 23.08,
  "retailers_count": 5,
  "best_deal": {
    "retailer": "Kaufland",
    "price": 24.99,
    "url": "https://www.kaufland.ro/...",
    "is_promotional": true
  }
}
```

## Architecture

```
backend/
├── app/
│   ├── core/          # Configuration and database
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── repositories/  # Database operations
│   ├── services/      # Business logic
│   ├── scrapers/      # Web scrapers
│   └── routers/       # API endpoints
├── requirements.txt
└── Dockerfile
```

## Technologies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **aiohttp** - Async HTTP client
- **BeautifulSoup** - HTML parsing
- **Pydantic** - Data validation

## Development

### Running Tests

```bash
pytest
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Linting
flake8 app/
mypy app/
```

## Deployment

### Docker

```bash
docker build -t romanian-price-tracker .
docker run -p 8000:8000 romanian-price-tracker
```

### Production

For production deployment, use:
- Gunicorn with Uvicorn workers
- PostgreSQL with connection pooling
- Redis for caching
- Nginx as reverse proxy

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/promotion_search
REDIS_URL=redis://localhost:6379/0
DEBUG=false
REQUEST_DELAY=2.0
MAX_CONCURRENT_REQUESTS=3
```

## License

MIT License

