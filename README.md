# Word Visual Memory 🌿

A web application that helps users memorize words through visual memory techniques. The system generates visual options (similar words, synonyms, antonyms) with corresponding images using LLM and image generation APIs.

## Features

- **Word Generation**: Enter a word and automatically generate:
  - Similar-looking word (形近词)
  - Synonym (近义词)
  - Antonym (反义词)
- **Visual Learning**: Each word gets a generated image to aid memory
- **Image Regeneration**: Refresh individual images or regenerate all
- **Local Storage**: All data saved to local SQLite database

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Local database
- **OpenAI Python SDK** - For Doubao API calls (compatible interface)

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework

## API Configuration

This application uses Doubao APIs:
- **LLM**: `doubao-seed-1-8-251228` - For generating word options and image prompts
- **Image**: `doubao-seedream-4-0-250828` - For generating visual images

## Project Structure

```
buciwa_danxuan/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── main.py            # FastAPI application
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── llm_service.py     # LLM API integration
│   │       └── image_service.py   # Image generation API
│   ├── static/
│   │   └── images/            # Generated images storage
│   ├── .env                   # Environment variables (with API key)
│   ├── .env.example           # Environment variables template
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js       # API client
│   │   ├── components/
│   │   │   ├── WordCard.vue       # List item component
│   │   │   └── WordImageCard.vue  # Detail page card
│   │   ├── views/
│   │   │   ├── ListView.vue       # Word list page
│   │   │   └── DetailView.vue     # Word detail page
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment:
   - The `.env` file is already configured with the API key
   - If needed, copy `.env.example` to `.env` and add your API key

6. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open browser at `http://localhost:3000`

## API Endpoints

### Word Sets
- `GET /api/word-sets` - List all word sets
- `GET /api/word-sets/{id}` - Get a specific word set
- `POST /api/word-sets/generate` - Generate new word set with images
- `POST /api/word-sets/{id}/regenerate` - Regenerate all words and images
- `DELETE /api/word-sets/{id}` - Delete a word set

### Words
- `POST /api/words/{word_id}/regenerate-image` - Regenerate image for a word

## Design

- **Color Scheme**: Mint Green primary with Macaron accent colors
- **Style**: Rounded corners, soft shadows, card-based layout
- **Responsive**: Mobile-first design with responsive breakpoints

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ARK_API_KEY` | Doubao API Key | Required |
| `ARK_BASE_URL` | API Base URL | `https://ark.cn-beijing.volces.com/api/v3` |
| `LLM_MODEL` | LLM Model Name | `doubao-seed-1-8-251228` |
| `IMAGE_MODEL` | Image Model Name | `doubao-seedream-4-0-250828` |
| `DATABASE_URL` | Database URL | `sqlite:///./word_memory.db` |

## License

MIT
