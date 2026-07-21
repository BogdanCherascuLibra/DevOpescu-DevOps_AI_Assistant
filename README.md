# DevOpescu

DevOpescu is an AI-powered DevOps assistant designed to help with Linux administration, Docker troubleshooting, service diagnosis, networking, CI/CD, and general infrastructure-related questions.

The project combines a conversational AI agent with a local knowledge base, semantic search, retrieval-augmented generation (RAG), conversation persistence, a REST API, and a minimal web interface.

---

## Features

- DevOps-focused AI assistant
- Custom identity, behavior rules, and language handling
- Conversation context management
- Dynamic system prompt generation
- Knowledge base organized into:
  - prompts
  - facts
  - procedures
- Registry-based knowledge loading
- Paragraph-based document chunking
- Local embedding generation with Ollama
- Semantic search using cosine similarity
- Retrieval-based context injection
- General model knowledge fallback
- Token usage tracking
- Estimated API cost calculation
- Context compression for long conversations
- Robust error handling
- Fallback strategy when RAG or external services are unavailable
- SQLite persistence
- Session management
- Multiple conversations per user
- Conversation export and import using JSON
- FastAPI HTTP backend
- REST API endpoints
- Swagger documentation
- Minimal web interface
- Conversation deletion
- Per-conversation usage analytics

---

## Requirements

- Python 3.10 or newer
- Ollama
- An API key for the configured LLM provider
- Git
- A modern web browser

Recommended environment:

- Linux
- Ubuntu 24.04
- WSL
- macOS

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/BogdanCherascuLibra/DevOpescu-DevOps_AI_Assistant.git
cd DevOpescu-DevOps_AI_Assistant
```

### 2. Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

Linux/macOS:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Open `.env` and add your API key:

```env
API_KEY=your_api_key_here
```

Do not commit `.env` to GitHub.

---

## Ollama Setup

The project uses Ollama for local embeddings.

Install the embedding model:

```bash
ollama pull bge-m3
```

Start Ollama:

```bash
ollama serve
```

Generate the embeddings file:

```bash
python embedding_generator.py
```

Embeddings are regenerated when the knowledge base changes.

---

## Run the Application

Start the FastAPI server:

```bash
uvicorn api:app --reload
```

Open the web interface:

```text
http://127.0.0.1:8000
```

Open the Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Check the service status:

```text
http://127.0.0.1:8000/health
```

---

## Usage Examples

### Docker troubleshooting

User:

```text
A Docker container does not start. How can I diagnose it?
```

DevOpescu may recommend:

```bash
docker ps -a
docker logs --tail 100 CONTAINER_NAME
docker inspect CONTAINER_NAME
docker stats --no-stream CONTAINER_NAME
```

The assistant explains each command and avoids claiming that the problem is fixed without seeing the command output.

### Linux service troubleshooting

User:

```text
My nginx service is not working.
```

Possible diagnostic steps:

```bash
systemctl status nginx
journalctl -u nginx --since "30 minutes ago"
ss -lntup
df -h
free -h
```

### Multiple conversations

A user can create separate conversations such as:

```text
Docker startup issue
Nginx service debugging
GitHub Actions failure
Network connectivity problem
```

Each conversation stores its own history and usage information.

### Export a conversation

Use the web interface or the REST endpoint:

```http
GET /users/{username}/conversations/{conversation_id}/export
```

### Import a conversation

```http
POST /users/{username}/conversations/import
```

The uploaded file must be a valid JSON conversation export.

---

## License

This project is intended for educational and portfolio use.
