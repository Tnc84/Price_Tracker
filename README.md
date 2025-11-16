# 🛒 Romanian Price Tracker

A comprehensive price comparison application for Romanian retailers with a simple web interface to find the best prices across multiple retailers.

## 🏗️ Architecture

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Web UI (HTML/CSS/JavaScript) - served by FastAPI
- **Mobile**: Kotlin + Jetpack Compose (Android) - *In development*
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery

## 🏪 Supported Romanian Retailers

- **eMAG** - https://www.emag.ro ✅ (Active)
- **Altex** - https://www.altex.ro ⏸️ (Temporarily disabled)
- **Carrefour** - https://www.carrefour.ro ⏸️ (Temporarily disabled)
- **Kaufland** - https://www.kaufland.ro ⏸️ (Temporarily disabled)
- **Selgros** - https://www.selgros.ro ⏸️ (Temporarily disabled)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ for local development

### Start with Docker (Recommended)
```bash
# Start all services (backend, database, redis)
docker-compose up -d

# Access the web UI at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Run Locally (Development)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Access the web UI at http://localhost:8000
```

### Using the Web Interface
1. Open http://localhost:8000 in your browser
2. Enter a product name (e.g., "cafea lavazza", "mancare caini")
3. Click "Search Now"
4. View the top 3 best prices with direct links to purchase

## 📁 Project Structure

```
Promotion_Search/
├── backend/              # Python FastAPI Backend
│   ├── app/
│   │   ├── static/       # Web UI (HTML, CSS, JavaScript)
│   │   ├── scrapers/     # Web scrapers for retailers
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   └── models/       # Database models
│   └── requirements.txt
├── mobile/               # Kotlin Android App (in development)
└── docker-compose.yml    # Docker configuration
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/promotion_search
REDIS_URL=redis://localhost:6379/0
```

## 📱 Features

### Current Features
- 🌐 **Web UI**: Simple, modern search interface
- 🔍 **Product Search**: Search across Romanian retailers (eMAG active)
- 💰 **Price Comparison**: Get top 3 best prices instantly
- 🔗 **Direct Links**: Click to buy directly from retailer
- 📊 **Real-time Results**: Live scraping for current prices

### Planned Features
- 📊 Price history and trends
- 🔔 Price drop alerts
- 🎯 Target price notifications
- 🏪 Multi-retailer support (Altex, Carrefour, Kaufland, Selgros)
- 📱 Mobile app (Android)

## 🤝 Contributing

Contributions are welcome! Please read the contribution guidelines.

## 📄 License

MIT License

