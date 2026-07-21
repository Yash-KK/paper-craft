# PaperCraft

PaperCraft is an AI-powered platform that helps teachers create high-quality, well-structured question papers in minutes. Its goal is to use an intelligent multi-agent workflow to automate syllabus analysis, assessment planning, question generation, validation, and formatting—turning a time-consuming process into a guided, reliable experience.

> PaperCraft is currently under active development. The foundation for chapter-aware AI assistance is complete; automated blueprint and question-paper generation are the next major milestones.

## About the Product

Teachers can organize work into notebooks, select the relevant class, subject, and chapters, and chat with an AI assistant grounded in the selected textbook content. PaperCraft is being designed to support the complete question-paper lifecycle:

1. Understand the syllabus and selected chapters.
2. Generate an assessment blueprint with marks, difficulty, and topic coverage.
3. Produce the first version of a question paper.
4. Validate its quality, balance, and syllabus alignment.
5. Refine future versions through chat while retaining the first version as context.
6. Export a clean, classroom-ready document.

## Current Capabilities

- Google sign-in with JWT-based API authentication
- Teacher profiles and protected application routes
- Notebook creation, listing, and deletion
- Class, subject, and chapter selection from a managed catalog
- Chapter availability controls
- Persistent notebook-specific chat history
- AI chat grounded in the notebook's selected chapters
- Hybrid dense and sparse retrieval with metadata-based chapter filtering
- Streaming AI responses over Server-Sent Events (SSE)
- Optional live web search for current information
- Markdown, tables, and mathematical notation rendering
- Textbook ingestion for text, image descriptions, and tables
- Responsive dashboard with light and dark themes
- Database migrations, backend tests, type checking, linting, and CI builds

The currently modeled academic catalog supports Mathematics for Classes 9 and 10 and is intended to expand over time.

## Roadmap

### 1. Generate Assessment Blueprints

- Collect paper requirements such as total marks, duration, sections, and question types
- Distribute marks across chapters, learning objectives, and difficulty levels
- Define the number and type of questions for each section
- Validate syllabus coverage and blueprint totals before generation

### 2. Generate the First Question Paper (V1)

- Use the approved blueprint and retrieved textbook context
- Generate syllabus-aligned questions with clear marks and instructions
- Detect duplication, ambiguity, factual issues, and invalid mark totals
- Format the result into a consistent, printable question paper
- Prepare the paper for DOCX/PDF export

### 3. Generate Subsequent Versions Through Chat

- Treat V1 as persistent context for future revisions
- Accept natural-language requests such as:
  - “Make Section B more application-oriented.”
  - “Replace Question 7 with a harder geometry problem.”
  - “Create another version with the same blueprint.”
- Preserve constraints while regenerating only the requested parts
- Maintain version history and make versions easy to compare

### Future Enhancements

- Dedicated agents for planning, generation, validation, and formatting
- Answer keys, marking schemes, and worked solutions
- More classes, subjects, boards, and custom syllabus uploads
- Collaborative review and sharing
- Reusable templates and school branding
- Question banks and analytics for coverage and difficulty

## Tech Stack

### Frontend

- React 19 and TypeScript
- Vite
- Tailwind CSS 4
- shadcn/ui and Base UI
- TanStack Query
- React Router
- React Markdown, GFM, and MathJax
- Server-Sent Events for streamed chat responses

### Backend and AI

- Python 3.12+
- FastAPI and Pydantic
- LangChain and LangGraph
- OpenAI-compatible chat and embedding APIs
- Qdrant hybrid vector search
- FastEmbed sparse embeddings
- Tavily web search
- Document ingestion with metadata-aware text, image, and table chunks
- `python-docx` for document export workflows

### Data and Infrastructure

- PostgreSQL
- SQLAlchemy with asyncpg
- Alembic migrations
- Google OAuth
- JWT authentication
- Pytest and mypy
- GitHub Actions CI

## Architecture

```text
Teacher
   │
   ▼
React + TypeScript frontend
   │  REST API + SSE
   ▼
FastAPI backend
   ├── Authentication and user profiles
   ├── Notebook and chapter management
   ├── Persistent chat sessions
   └── AI agent
         ├── Chapter-scoped retrieval
         │     └── Qdrant hybrid vector store
         └── Optional Tavily web search

PostgreSQL stores users, notebooks, chapter metadata, and chat history.
```

## Repository Structure

```text
paper-craft/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Configuration and security
│   │   ├── db/           # SQLAlchemy models and sessions
│   │   ├── repositories/ # Data-access layer
│   │   └── services/     # Chat, ingestion, and vector search
│   ├── alembic/          # Database migrations
│   ├── data/             # Source textbooks
│   ├── extracted_data/   # Parsed textbook content
│   ├── notebooks/        # Extraction and export experiments
│   └── tests/
├── front-end/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── features/
│       ├── hooks/
│       ├── lib/
│       └── pages/
└── .github/workflows/    # CI configuration
```

## Getting Started

### Prerequisites

- Node.js 22+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL
- Qdrant
- Google OAuth credentials
- An OpenAI-compatible model and embedding provider
- A Tavily API key if web search is required

### 1. Configure the Backend

Create `backend/.env`:

```env
AIC_MODEL=your-chat-model
AIC_DENSE_EMBEDDING_MODEL=your-embedding-model
AIC_API_KEY=your-api-key
AIC_BASE_URL=https://your-provider.example/v1

QDRANT_URL=http://localhost:6333
COLLECTION_NAME=paper-craft
SPARSE_EMBEDDING_MODEL=Qdrant/bm25
EXTRACTED_DATA_DIR=extracted_data
NCERT_BOOK_CONFIG={}

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
ALLOW_INSECURE_HTTP=true

ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/paper_craft
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/paper_craft

SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
FRONTEND_URL=http://localhost:5173

# Optional
TAVILY_API_KEY=your-tavily-api-key
```

Install dependencies, migrate the database, and start the API:

```bash
cd backend
uv sync --all-groups
uv run alembic upgrade head
uv run fastapi dev
```

The backend runs at `http://localhost:8000`; API documentation is available at `http://localhost:8000/docs`.

### 2. Configure the Frontend

Create `front-end/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Install dependencies and start the app:

```bash
cd front-end
npm install
npm run dev
```

Open `http://localhost:5173`.

## Quality Checks

```bash
# Frontend
cd front-end
npm run lint
npm run typecheck
npm run build

# Backend
cd backend
uv run mypy .
uv run pytest tests -v
```

## Project Status

PaperCraft has a working full-stack foundation for authenticated, notebook-based, chapter-aware AI conversations. Blueprint generation, V1 question-paper generation, and context-aware paper versioning are planned and not yet implemented.

