# 🛒 Romanian Price Tracker

A comprehensive price comparison application for Romanian retailers including eMAG, Altex, Carrefour, Kaufland, Selgros, and more.

## 🏗️ Architecture

- **Backend**: Python 3.11 + FastAPI
- **Mobile**: Kotlin + Jetpack Compose (Android)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery

## 🏪 Supported Romanian Retailers

- **eMAG** - https://www.emag.ro
- **Altex** - https://www.altex.ro
- **Carrefour** - https://www.carrefour.ro
- **Kaufland** - https://www.kaufland.ro
- **Selgros** - https://www.selgros.ro
- **Auchan** - https://www.auchan.ro
- **Flanco** - https://www.flanco.ro
- **Dedeman** - https://www.dedeman.ro

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Android Studio (for mobile development)

### Start Backend
```bash
# Start all services
docker-compose up -d

# Or run locally
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
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

- 🔍 Search products across multiple retailers
- 💰 Real-time price comparison
- 📊 Price history and trends
- 🔔 Price drop alerts
- 🎯 Target price notifications
- 🏪 Multi-retailer support

## 🤝 Contributing

Contributions are welcome! Please read the contribution guidelines.

## 📄 License

MIT License

