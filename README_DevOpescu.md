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

## Main API Endpoints

```text
GET    /health
POST   /users/{username}/conversations
GET    /users/{username}/conversations
GET    /users/{username}/conversations/{conversation_id}
POST   /users/{username}/conversations/{conversation_id}/messages
DELETE /users/{username}/conversations/{conversation_id}
GET    /users/{username}/conversations/{conversation_id}/export
POST   /users/{username}/conversations/import
```

---

## Project Structure

```text
.
├── agent.py
├── api.py
├── api_dependencies.py
├── api_schemas.py
├── api_services.py
├── config.py
├── conversation_context.py
├── conversation_exporter.py
├── conversation_importer.py
├── conversation_manager.py
├── database.py
├── document_chunker.py
├── embedding_generator.py
├── embeddings_client.py
├── knowledge_base.py
├── llm_client.py
├── main.py
├── session_manager.py
├── utils.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── devopescu.db
│   └── embeddings.json
│
├── exports/
│
├── knowledge/
│   ├── facts/
│   │   ├── infrastructure.md
│   │   └── registry.json
│   │
│   ├── procedures/
│   │   ├── docker_troubleshooting.md
│   │   ├── service_troubleshooting.md
│   │   └── registry.json
│   │
│   └── prompts/
│       ├── 01_identity.md
│       ├── 02_rules.md
│       └── 03_language.md
│
├── routers/
│   ├── __init__.py
│   ├── conversations.py
│   ├── health.py
│   └── transfer.py
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── tools/
    ├── tool.py
    └── tools.py
```

---

## Configuration

The main configuration values are stored in `config.py`.

They include:

- LLM model name
- API endpoint
- embedding model
- embedding endpoint
- chunk size
- semantic search result limit
- minimum similarity score
- context token limit
- token prices
- database path
- embeddings path
- exports path

---

## Notes

- Documents marked with `always_load: true` are included directly in the system prompt.
- Documents marked with `always_load: false` are retrieved through semantic search.
- The assistant may use both internal documentation and general model knowledge.
- RAG context is injected temporarily and is not permanently added to the conversation history.
- Input tokens increase as the conversation history grows.
- Cost values are estimates and may differ from the provider's final billing.
- Destructive commands should require confirmation before execution.

---

## Limitations

- Ollama must be running for semantic search and embedding generation.
- The project currently uses SQLite and is primarily intended for local or educational use.
- Token counting is estimated locally.
- Advanced authentication and authorization are not implemented.
- Destructive system tools are intentionally restricted.
- The web interface is minimal and does not use a frontend framework.

---


## License

This project is intended for educational and portfolio use.
