# 🛒 Romanian Price Tracker

A comprehensive price comparison application for Romanian retailers including eMAG, Altex, Carrefour, Kaufland, Selgros, and more.

## 🏗️ Architecture

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Web UI (HTML/CSS/JavaScript) - served by FastAPI
- **Mobile**: Kotlin + Jetpack Compose (Android)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery

## 🏪 Supported Romanian Retailers

- **eMAG** - https://www.emag.ro ✅ (Active)
- **Altex** - https://www.altex.ro ⏸️ (Temporarily disabled)
- **Carrefour** - https://www.carrefour.ro ⏸️ (Temporarily disabled)
- **Kaufland** - https://www.kaufland.ro ⏸️ (Temporarily disabled)
- **Selgros** - https://www.selgros.ro ⏸️ (Temporarily disabled)
- **Auchan** - https://www.auchan.ro (Not implemented)
- **Flanco** - https://www.flanco.ro (Not implemented)
- **Dedeman** - https://www.dedeman.ro (Not implemented)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Android Studio (for mobile development)

### Start Backend & Frontend
```bash
# Start all services (backend, database, redis)
docker-compose up -d

# Access the web UI at http://localhost:8000
# API documentation at http://localhost:8000/docs

# Or run locally
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Access the web UI at http://localhost:8000
```

### Start Mobile Development
```bash
cd mobile
# Open in Android Studio
```

## 📁 Project Structure

```
Promotion_Search/
├── backend/          # Python FastAPI Backend
├── mobile/           # Kotlin Android App
├── database/         # Database migrations
├── docs/            # Documentation
└── docker-compose.yml
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/promotion_search
REDIS_URL=redis://localhost:6379/0
```

## 📱 Features

- 🌐 **Web UI**: Simple search interface to find best prices
- 🔍 Search products across retailers (currently eMAG)
- 💰 Real-time price comparison
- 📊 Price history and trends
- 🔔 Price drop alerts
- 🎯 Target price notifications
- 🏪 Multi-retailer support (other retailers temporarily disabled)

## 🤝 Contributing

Contributions are welcome! Please read the contribution guidelines.

## 📄 License

MIT License

