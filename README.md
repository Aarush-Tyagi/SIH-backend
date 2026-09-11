# SIH Backend

WeatherGPT backend for the SIH project. This is a FastAPI application that
provides weather chat, alert, subscription, and WhatsApp webhook endpoints.

## Current demo behavior

The project works without provider credentials:

- Weather falls back to deterministic mock IMD data.
- RAG starts with an empty local vector store until the seed script is run.
- Chat requires `GROQ_API_KEY`; without it, `/api/chat` returns a clear `503`.
- OpenWeather, Bhashini, and Twilio integrations are optional.

Do not commit `.env`, API keys, database files, or the local virtual
environment.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`. Interactive
documentation is available at `/docs`.

## Optional configuration

Edit `.env` to add provider credentials. `ADMIN_API_KEY` protects the local
subscription inspection endpoint. Twilio webhook signatures are validated
automatically when `TWILIO_AUTH_TOKEN` is configured.
