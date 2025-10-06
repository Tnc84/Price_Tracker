# 🚀 Getting Started - Romanian Price Tracker

Complete guide to set up and run the Romanian Price Tracker application.

## 📋 Prerequisites

### Backend (Python)
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Mobile (Kotlin)
- Android Studio Hedgehog or newer
- Android SDK 24+ (Android 7.0+)
- JDK 11+

## 🏃 Quick Start

### Option 1: Using Docker (Easiest)

```bash
# Clone the repository
git clone <your-repo-url>
cd Promotion_Search

# Start all services (PostgreSQL, Redis, Backend)
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f backend

# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env with your database credentials

# Start PostgreSQL and Redis
# (Install locally or use Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

#### Mobile Setup

```bash
# Open Android Studio
# File > Open > Select mobile/ folder

# Wait for Gradle sync to complete

# Update API URL in mobile/app/build.gradle.kts:
buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/v1/\"")

# Run on emulator or device
# Click Run button or Shift+F10
```

## 📱 Using the Application

### 1. Test the Backend API

```bash
# Check API health
curl http://localhost:8000/health

# Get supported retailers
curl http://localhost:8000/api/v1/scraper/retailers
```

### 2. Create Your First Product

```bash
# Create a product
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cafea Jacobs Cronat Gold 200g",
    "category": "Alimente",
    "brand": "Jacobs",
    "target_price": 25.00
  }'

# Response:
{
  "id": 1,
  "name": "Cafea Jacobs Cronat Gold 200g",
  "category": "Alimente",
  "brand": "Jacobs",
  "target_price": 25.00,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 3. Scrape Prices

```bash
# Scrape prices from all retailers
curl -X POST "http://localhost:8000/api/v1/products/1/scrape"

# Response:
{
  "message": "Price scraping completed",
  "product_id": 1,
  "prices_found": 15
}
```

### 4. Compare Prices

```bash
# Get price comparison
curl "http://localhost:8000/api/v1/prices/comparison/1"

# Response:
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
    "is_promotional": true
  }
}
```

## 🏪 Supported Romanian Retailers

- **eMAG** (www.emag.ro) - Romania's largest marketplace
- **Altex** (www.altex.ro) - Electronics & appliances
- **Carrefour** (www.carrefour.ro) - Supermarket
- **Kaufland** (www.kaufland.ro) - Supermarket
- **Selgros** (www.selgros.ro) - Cash & Carry

## 📊 API Endpoints

### Products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{id}` - Get product with prices
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/{id}/scrape` - Scrape prices

### Prices
- `GET /api/v1/prices/comparison/{id}` - Price comparison
- `GET /api/v1/prices/history/{id}` - Price history
- `GET /api/v1/prices/deals` - Promotional deals

### Scraper
- `GET /api/v1/scraper/retailers` - List retailers
- `GET /api/v1/scraper/search` - Quick search

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/promotion_search

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=false
CURRENCY=RON
LOCALE=ro_RO

# Scraping (respect websites)
REQUEST_DELAY=2.0
MAX_CONCURRENT_REQUESTS=3
```

### Mobile Configuration

In `mobile/app/build.gradle.kts`:

```kotlin
buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/v1/\"")
```

**Note**: `10.0.2.2` is the special IP for localhost from Android emulator.

For physical device, use your computer's IP:
```kotlin
buildConfigField("String", "API_BASE_URL", "\"http://192.168.1.100:8000/api/v1/\"")
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Mobile Tests
```bash
cd mobile
./gradlew test
./gradlew connectedAndroidTest
```

## 📦 Deployment

### Backend (Docker)

```bash
# Build image
docker build -t romanian-price-tracker ./backend

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  romanian-price-tracker
```

### Mobile (Google Play)

```bash
cd mobile
./gradlew bundleRelease

# Output: app/build/outputs/bundle/release/app-release.aab
# Upload to Google Play Console
```

## 🐛 Troubleshooting

### Backend Issues

**Database connection error:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U user -d promotion_search
```

**Import errors:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Mobile Issues

**Cannot connect to API:**
- Ensure backend is running: `curl http://localhost:8000/health`
- Check emulator uses `10.0.2.2` for localhost
- For physical device, use computer's local IP

**Gradle sync failed:**
- File > Invalidate Caches and Restart
- Delete `.gradle` folder and sync again

## 📚 Next Steps

1. **Add more products** - Create products you want to track
2. **Schedule scraping** - Set up periodic price updates
3. **Configure alerts** - Get notified on price drops
4. **Extend mobile app** - Add full UI implementation
5. **Deploy to production** - Use cloud hosting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- Documentation: `/docs` folder
- API Docs: http://localhost:8000/docs
- Issues: GitHub Issues

---

**Happy Price Tracking! 🇷🇴**

