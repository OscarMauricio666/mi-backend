# Mi Backend API

REST API built with FastAPI, MongoDB Atlas, and multiple external service integrations.

## Features

- **Claude AI** - Chat with Anthropic's Claude
- **Crypto** - Bitcoin and cryptocurrency prices (CoinGecko)
- **News** - Top headlines and articles (NewsAPI)
- **Sports** - Football matches and standings (API-Football)
- **MongoDB Atlas** - Cloud database with Beanie ODM

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT                                         │
│                        (Web App / Mobile / Postman)                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MI BACKEND API                                      │
│                            FastAPI (Python 3.9+)                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                              main.py                                     │    │
│  │  - Lifespan (startup/shutdown)                                          │    │
│  │  - CORS Middleware                                                       │    │
│  │  - Route Registration                                                    │    │
│  │  - Swagger/ReDoc Documentation                                           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
         ┌─────────────┬───────────────┼───────────────┬─────────────┐
         │             │               │               │             │
         ▼             ▼               ▼               ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   /claude   │ │   /crypto   │ │   /news     │ │   /sports   │ │   /health   │
│   Routes    │ │   Routes    │ │   Routes    │ │   Routes    │ │   Routes    │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Claude    │ │   Crypto    │ │    News     │ │   Sports    │
│   Service   │ │   Service   │ │   Service   │ │   Service   │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Anthropic  │ │  CoinGecko  │ │   NewsAPI   │ │API-Football │
│     API     │ │     API     │ │             │ │             │
└─────────────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
                       │               │               │
                       └───────────────┴───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │        MongoDB Atlas          │
                       │         (Beanie ODM)          │
                       │  ┌─────────────────────────┐  │
                       │  │     Collections:        │  │
                       │  │  - crypto_prices        │  │
                       │  │  - news_articles        │  │
                       │  │  - football_matches     │  │
                       │  │  - football_teams       │  │
                       │  └─────────────────────────┘  │
                       └───────────────────────────────┘
```

## Request Flow

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              REQUEST FLOW                                       │
└────────────────────────────────────────────────────────────────────────────────┘

  1. REQUEST                    2. VALIDATION                 3. SERVICE
  ─────────────────────────────────────────────────────────────────────────────

     Client                        FastAPI                      Service
        │                             │                            │
        │  POST /api/v1/crypto/fetch  │                            │
        │────────────────────────────►│                            │
        │                             │                            │
        │                             │  Pydantic Validation       │
        │                             │─────────────────────┐      │
        │                             │◄────────────────────┘      │
        │                             │                            │
        │                             │  CryptoService.fetch()     │
        │                             │───────────────────────────►│
        │                             │                            │


  4. EXTERNAL API               5. DATABASE                   6. RESPONSE
  ─────────────────────────────────────────────────────────────────────────────

     Service                      MongoDB                       Client
        │                            │                             │
        │  GET coingecko.com/api     │                             │
        │───────────────────►        │                             │
        │◄───────────────────        │                             │
        │   JSON Response            │                             │
        │                            │                             │
        │  Beanie insert()           │                             │
        │───────────────────────────►│                             │
        │◄───────────────────────────│                             │
        │   Document stored          │                             │
        │                            │                             │
        │                         JSON Response                    │
        │─────────────────────────────────────────────────────────►│
        │                                                          │
```

## Project Structure

```
mi-backend/
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── config.py           # Settings with pydantic-settings
    ├── database.py         # MongoDB + Beanie initialization
    ├── main.py             # FastAPI application
    │
    ├── documents/          # Beanie ODM Documents
    │   ├── __init__.py
    │   ├── crypto.py       # CryptoPrice
    │   ├── news.py         # NewsArticle
    │   └── sports.py       # FootballMatch, FootballTeam
    │
    ├── models/             # Pydantic Schemas
    │   ├── __init__.py
    │   └── claude.py       # ChatRequest, ChatResponse
    │
    ├── routes/             # API Endpoints
    │   ├── __init__.py
    │   ├── claude.py
    │   ├── crypto.py
    │   ├── news.py
    │   └── sports.py
    │
    └── services/           # Business Logic
        ├── __init__.py
        ├── claude_service.py
        ├── crypto_service.py
        ├── news_service.py
        └── sports_service.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check + MongoDB status |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

### Claude AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/claude/chat` | Chat with Claude |
| GET | `/api/v1/claude/health` | Claude API status |

### Crypto
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/crypto/prices` | Get prices from CoinGecko |
| POST | `/api/v1/crypto/fetch` | Fetch & store in MongoDB |
| GET | `/api/v1/crypto/history/{coin_id}` | Get stored price history |

### News
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/news/headlines` | Get headlines from NewsAPI |
| POST | `/api/v1/news/fetch` | Fetch & store in MongoDB |
| GET | `/api/v1/news/stored` | Get stored articles |

### Sports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sports/football/live` | Live matches |
| GET | `/api/v1/sports/football/matches` | Matches by date |
| GET | `/api/v1/sports/football/standings` | League standings |
| POST | `/api/v1/sports/football/fetch` | Fetch & store in MongoDB |
| GET | `/api/v1/sports/football/stored` | Get stored matches |

## Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- API Keys (optional for some features)

### Setup

1. Clone the repository
```bash
git clone https://github.com/OscarMauricio666/mi-backend.git
cd mi-backend
```

2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the server
```bash
uvicorn src.main:app --reload
```

6. Open http://localhost:8000/docs

## Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URL` | MongoDB Atlas connection string | Yes |
| `DATABASE_NAME` | Database name | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | For Claude |
| `NEWSAPI_KEY` | NewsAPI key | For News |
| `FOOTBALL_API_KEY` | API-Football key | For Sports |

## External APIs

| Service | API | Free Tier |
|---------|-----|-----------|
| Crypto | [CoinGecko](https://www.coingecko.com/en/api) | Unlimited (no key) |
| News | [NewsAPI](https://newsapi.org/) | 100 req/day |
| Sports | [API-Football](https://www.api-football.com/) | 100 req/day |
| AI | [Anthropic](https://console.anthropic.com/) | Pay per use |

## Tech Stack

- **FastAPI** - Web framework
- **Beanie** - MongoDB ODM
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client
- **Uvicorn** - ASGI server

## License

MIT
