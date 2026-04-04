# Resume-to-Jobs Matching Platform

A production-grade web application that matches resumes to job listings using AI. Upload your resume, and the system will automatically extract skills, search job boards, and rank opportunities by relevance.

## Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 20+** (for frontend)
- **Docker** (optional, for containerized deployment)
- **OpenAI API Key** (or compatible LLM endpoint)

## Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd Resume-to-Jobs

# Start with Docker Compose
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

- **Resume Parsing**: Upload PDF/DOCX files or paste text; LLM extracts structured data
- **Job Scraping**: Multi-source scraping (Indeed, RemoteOK, LinkedIn) with anti-blocking
- **AI Matching**: Two-stage matching - heuristic filtering + LLM scoring
- **Real-time Results**: Matched jobs ranked by relevance with detailed explanations

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings management
- **LangChain** - LLM orchestration and chains
- **httpx + BeautifulSoup** - Async web scraping

### Frontend
- **React** - UI component library
- **Vite** - Build tool
- **Axios** - HTTP client

## Project Structure

```
Resume-to-Jobs/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Configuration & prompts
│   ├── requirements.txt        # Python dependencies
│   ├── environment.yml         # Conda environment (references requirements.txt)
│   ├── schemas/
│   │   ├── resume.py           # Resume data models
│   │   ├── job.py              # Job listing models
│   │   └── match.py            # Match score models
│   ├── services/
│   │   ├── resume_parser.py    # Resume upload & parsing
│   │   ├── job_service.py      # Job scraping & filtering
│   │   ├── matcher.py          # Resume-to-job matching
│   │   └── cache.py            # In-memory caching
│   ├── scrapers/
│   │   ├── common.py           # Shared scraper utilities
│   │   ├── indeed.py           # Indeed.com scraper
│   │   ├── linkedin.py         # LinkedIn.com scraper
│   │   └── remoteok.py         # RemoteOK.com scraper
│   ├── chains/
│   │   ├── resume_chain.py     # Resume extraction chain
│   │   └── job_match_chain.py  # Job matching chain
│   └── utils/
│       ├── file_loader.py      # PDF/DOCX parsing
│       └── text_utils.py       # Text processing helpers
│
├── frontend/                   # React Frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js              # API client
│       └── components/
│           ├── Upload.jsx      # Resume upload UI
│           └── JobList.jsx     # Job results UI
│
├── Dockerfile                  # Multi-stage Docker build (backend + frontend)
├── docker-compose.yml          # Multi-container Docker config
├── .gitignore                  # Git ignore rules (unified)
├── .dockerignore               # Docker ignore rules (unified)
└── README.md                   # This file
```

## Setup & Installation

### Option 1: Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Using Conda
conda env create -f environment.yml
conda activate resume-matcher

# Or using pip
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/upload-resume` | POST | Upload resume file (PDF/DOCX) |
| `/parse-text` | POST | Parse resume from text |
| `/jobs` | GET | Search job listings |
| `/match-jobs` | POST | Match resume to jobs |
| `/resume/{id}` | GET | Get parsed resume by ID |
| `/apply?url=` | GET | Redirect to job application |
| `/stats` | GET | System statistics |

## Configuration

Set these environment variables in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
API_URL=http://localhost:8000
DEBUG=false
```

## Job Sources

- **Indeed**: Global job board with extensive listings
- **RemoteOK**: Remote-first job board
- **LinkedIn**: Professional networking with job listings

## Matching Algorithm

1. **Heuristic Pre-filter**: Calculate skills overlap percentage
2. **LLM Scoring**: Detailed analysis of resume vs job description
3. **Weighted Combine**: 30% heuristic + 70% LLM = final score

## Edge Cases Handled

- Empty/resume parsing failures
- Invalid file formats
- Expired job listings (>30 days)
- Dead apply URLs
- Duplicate job listings across sources
- Missing fields in scraped data

## Production Deployment

### Using Docker Compose

```bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Manual Docker Deployment

#### Backend
```bash
cd backend
docker build -t resume-matcher-backend .
docker run -d -p 8000:8000 --env-file .env --name resume-matcher-backend resume-matcher-backend
```

#### Frontend
```bash
cd frontend
docker build -t resume-matcher-frontend .
docker run -d -p 80:80 --name resume-matcher-frontend resume-matcher-frontend
```

## License

MIT License
