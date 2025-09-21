# Streamlit UI for Agent Query (Ocean Professional)

This directory also contains a Streamlit application (`streamlit_app.py`) that provides a clean, professional UI to:
- Select an available agent (if the backend supports agent listing).
- Enter a query for the LLM.
- Submit the query and view responses with references.
- Browse recent interaction history.

The UI follows the "Ocean Professional" classic theme.

## Prerequisites

- Python 3.9+ recommended
- Backend FastAPI service running and accessible. Set the URL via environment variable:
  - FRONTEND_BACKEND_BASE_URL (see `.env.example`)

## Setup

Create a virtual environment and install dependencies:

```bash
cd aws-bedrock-agent-query-platform-88993-89003/frontend_streamlit_interface
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Optionally, copy `.env.example` to `.env` and set the backend URL.

## Running

```bash
export FRONTEND_BACKEND_BASE_URL=http://localhost:8000  # or set in your environment
streamlit run streamlit_app.py --server.port=8501
```

Open http://localhost:8501 in your browser.

## Notes

- The app attempts to discover endpoints via `openapi.json` and supports common fallbacks:
  - Agent list: `GET /agents`, `GET /api/agents`
  - Query: `POST /query`, `POST /api/query`, `POST /agents/{agent_id}/query`
  - History: `GET /history`, `GET /api/history`, `GET /agents/{agent_id}/history`
- If your backend uses different routes, adjust the candidates in `streamlit_app.py` accordingly.

## Styling

Theme and styling are applied via:
- `.streamlit/config.toml`
- Inline CSS in `streamlit_app.py`

This keeps a classic, clean, business-oriented look aligned with the Ocean Professional palette.
"""
