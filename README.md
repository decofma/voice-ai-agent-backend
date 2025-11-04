# Backend: AI Voice Agent API (FastAPI)


![AI Voice Agent](https://iili.io/KQXCzLF.png) 


This directory contains the Python/FastAPI backend server for the AI Voice Agent project.

Its three primary responsibilities are:
1.  **Agent Management:** Exposes `POST /api/v1/agents` to first create a "Retell LLM" (the brain, containing the system prompt) and then create an "Agent" (the voice) linked to that brain.
2.  **Call Triggering:** Exposes `POST /api/v1/calls/trigger` to register a *Web Call* with Retell and return the credentials (`call_id`, `sampleRate`) required by the V1 frontend SDK.
3.  **Post-Processing:** Exposes `POST /api/v1/calls/retell-webhook` to receive the final transcript from Retell, send it to the Gemini API for structured data extraction, and store the result.

## Tech Stack

* **Framework:** FastAPI
* **AI (Conversation):** Retell AI (V2 API)
* **AI (Post-processing):** Google Gemini (via `google-genai`)
* **Database:** Python Dictionary (In-memory, replaces Supabase due to time constraints).
* **Server:** Uvicorn

## 1. Setup

### Prerequisites
* Python 3.10+
* A public tunneling service (Ngrok, Serveo, or Cloudflared)

### Installation

1.  **Clone the repository and navigate to the `backend/` folder:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate 
    
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the environment file:**
    Create a file named `.env` in the `backend/` folder and populate it with your API keys:
    ```env
    # Retell API Key from your dashboard
    RETELL_API_KEY=key_...

    # Google Gemini API Key (for Post-Processing)
    GEMINI_API_KEY=AIzaSy...

    # A Retell Phone Number (Required by the service for validation, even if not used for web calls)
    RETELL_NUMBER=+1... 

    # Public URL from your tunnel (See Execution Step 2)
    BACKEND_URL=[https://your-tunnel-url.com](https://your-tunnel-url.com)
    ```

## 2. Execution

The backend and the tunnel must be running simultaneously.

### Terminal 1: Start the Public Tunnel

Retell AI needs to send Webhooks to your local server. You must expose your port 8000.

**Recommended (Cloudflare Tunnel):**
```bash
cloudflared tunnel --url http://localhost:8000
```

**Alternative (Serveo):**
```bash
ssh -R 80:localhost:8000 serveo.net
```
*(Note: `localtunnel` is not recommended, as its password page blocks Retell's WebSockets).*

**After starting the tunnel, copy the `https://...` URL it provides and paste it into your `.env` file (`BACKEND_URL`).**

### Terminal 2: Start the FastAPI Server

1.  Activate the virtual environment (if not already active):
    ```bash
    .\venv\Scripts\activate
    ```

2.  Start the Uvicorn server:
    ```bash
    uvicorn app.api.main:app --reload
    ```

The server is now running on `http://127.0.0.1:8000` and is publicly accessible via your tunnel for the frontend and Retell webhooks.
