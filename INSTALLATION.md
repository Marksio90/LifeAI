# 🚀 LifeAI - Kompletny Przewodnik Instalacji i Testowania

> **Najnowocześniejsza platforma AI z zaawansowanymi funkcjami enterprise**

## 📋 Spis Treści

1. [Wymagania Wstępne](#-wymagania-wstępne)
2. [Szybki Start (5 minut)](#-szybki-start)
3. [Szczegółowa Instalacja](#-szczegółowa-instalacja)
4. [Testowanie Wszystkich Funkcji](#-testowanie-wszystkich-funkcji)
5. [Wdrożenie Produkcyjne](#-wdrożenie-produkcyjne)
6. [Rozwiązywanie Problemów](#-rozwiązywanie-problemów)
7. [Zaawansowane Funkcje](#-zaawansowane-funkcje)

---

## 📦 Wymagania Wstępne

### Minimalne Wymagania

| Komponent | Wersja Minimalna | Zalecana |
|-----------|------------------|----------|
| **Docker** | 20.10+ | 24.0+ |
| **Docker Compose** | 2.0+ | 2.20+ |
| **Node.js** | 18.0+ | 20.0+ |
| **Python** | 3.10+ | 3.11+ |
| **npm** | 8.0+ | 10.0+ |
| **RAM** | 4GB | 8GB+ |
| **Dysk** | 10GB | 20GB+ |

### Instalacja Narzędzi

<details>
<summary><b>🐧 Linux (Ubuntu/Debian)</b></summary>

```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Python
sudo apt-get install python3.11 python3-pip
```

</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# Homebrew (jeśli nie masz)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Docker Desktop
brew install --cask docker

# Node.js
brew install node@20

# Python
brew install python@3.11
```

</details>

<details>
<summary><b>🪟 Windows (WSL2)</b></summary>

```powershell
# Zainstaluj WSL2
wsl --install

# W WSL2 terminal:
# Postępuj zgodnie z instrukcjami Linux
```

</details>

### Wymagane Klucze API

| Serwis | Opis | Link |
|--------|------|------|
| **OpenAI API** | ⚠️ **WYMAGANE** - AI, TTS, DALL-E | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Pinecone** | Opcjonalne - Vector DB (produkcja) | [pinecone.io](https://www.pinecone.io/) |

---

## ⚡ Szybki Start

### 1. Sklonuj Repozytorium

```bash
git clone https://github.com/yourusername/LifeAI.git
cd LifeAI
```

### 2. Uruchom Automatyczną Instalację

```bash
# Nadaj uprawnienia
chmod +x setup.sh test.sh

# Uruchom instalację
./setup.sh
```

**Skrypt automatycznie:**
- ✅ Sprawdzi wymagania
- ✅ Utworzy plik `.env` z bezpiecznymi kluczami
- ✅ Zainstaluje wszystkie zależności
- ✅ Zbuduje kontenery Docker
- ✅ Uruchomi wszystkie serwisy
- ✅ Zainicjalizuje bazę danych

### 3. Ustaw Klucz OpenAI

Podczas instalacji zostaniesz poproszony o klucz OpenAI, lub ustaw go ręcznie:

```bash
nano .env
# Zmień: OPENAI_API_KEY=sk-your-key-here
```

### 4. Sprawdź Status

```bash
docker-compose ps
```

Wszystkie kontenery powinny być `healthy`:
- ✅ `lifeai-backend` (port 8000)
- ✅ `lifeai-frontend` (port 3000)
- ✅ `lifeai-postgres` (port 5432)
- ✅ `lifeai-redis` (port 6379)

### 5. Otwórz Aplikację

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **GraphQL:** http://localhost:8000/graphql

🎉 **Gotowe! Aplikacja działa!**

---

## 🔧 Szczegółowa Instalacja

### Krok 1: Konfiguracja Środowiska

#### Ręczna Konfiguracja `.env`

Jeśli wolisz ręczną konfigurację:

```bash
cp .env.example .env
```

Edytuj `.env`:

```bash
# =========================
# 🔐 BEZPIECZEŃSTWO (WYMAGANE!)
# =========================

# Wygeneruj silny klucz:
# openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# =========================
# 🤖 OPENAI (WYMAGANE!)
# =========================
OPENAI_API_KEY=sk-your-openai-api-key-here

# =========================
# 🗄️ BAZA DANYCH
# =========================
POSTGRES_USER=lifeai
POSTGRES_PASSWORD=your-strong-password-min-16-chars
POSTGRES_DB=lifeai

# WAŻNE: Hasło musi być takie samo w obu miejscach!
DATABASE_URL=postgresql://lifeai:your-strong-password-min-16-chars@postgres:5432/lifeai

# =========================
# 📦 REDIS
# =========================
REDIS_URL=redis://redis:6379/0

# =========================
# 🌐 ŚRODOWISKO
# =========================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# =========================
# 🔗 CORS
# =========================
ALLOWED_ORIGINS=http://localhost:3000,http://frontend:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# =========================
# 🧠 VECTOR DATABASE
# =========================
# Opcje: in-memory (dev) lub pinecone (prod)
VECTOR_DB_TYPE=in-memory

# Dla Pinecone (opcjonalne):
# PINECONE_API_KEY=your-key
# PINECONE_ENVIRONMENT=your-env
# PINECONE_INDEX_NAME=lifeai-memory
```

### Krok 2: Budowa i Uruchomienie

#### Budowa Kontenerów

```bash
# Zbuduj wszystkie obrazy
docker-compose build

# Lub z wymuszonym rebuildem
docker-compose build --no-cache
```

#### Uruchomienie Serwisów

```bash
# Uruchom w tle
docker-compose up -d

# Lub z logami na żywo
docker-compose up

# Sprawdź logi konkretnego serwisu
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Krok 3: Inicjalizacja Bazy Danych

```bash
# Migracje Alembic (jeśli skonfigurowane)
docker-compose exec backend alembic upgrade head

# Sprawdź status migracji
docker-compose exec backend alembic current

# Utwórz nową migrację (development)
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Krok 4: Weryfikacja Instalacji

```bash
# Uruchom pełny test suite
./test.sh

# Lub wybrane testy:
./test.sh --unit          # Tylko testy jednostkowe
./test.sh --integration   # Tylko testy integracyjne
./test.sh --e2e          # Tylko testy E2E
./test.sh --load         # Tylko testy obciążeniowe
```

---

## 🧪 Testowanie Wszystkich Funkcji

### 1. API Endpoints

#### Health Check

```bash
# Podstawowy health check
curl http://localhost:8000/health/live

# Szczegółowy health check
curl http://localhost:8000/health/ready | jq .
```

Oczekiwany wynik:
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "redis": true,
    "openai": true
  },
  "timestamp": "2025-12-25T10:00:00Z"
}
```

#### REST API

```bash
# Rejestracja użytkownika
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Zapisz token z odpowiedzi
TOKEN="your-access-token-here"

# Rozpocznij sesję czatu
curl -X POST http://localhost:8000/api/chat/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Wyślij wiadomość
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-id-from-previous-response",
    "message": "Jak mogę poprawić swoje zdrowie?",
    "modality": "text"
  }'
```

### 2. GraphQL API

Otwórz GraphQL Playground: http://localhost:8000/graphql

**Przykładowe query:**

```graphql
# Pobierz rozmowy
query GetConversations {
  conversations(limit: 10) {
    id
    agentType
    startTime
    messageCount
    lastMessage {
      role
      content
      timestamp
    }
  }
}

# Pobierz analitykę
query GetAnalytics {
  analytics {
    totalConversations
    totalMessages
    averageRating
    agentDistribution {
      agentType
      count
      percentage
    }
  }
}
```

**Przykładowa mutacja:**

```graphql
mutation SendMessage($input: MessageInput!) {
  sendMessage(input: $input) {
    id
    content
    timestamp
    agentType
  }
}
```

**Variables:**
```json
{
  "input": {
    "conversationId": "conv-123",
    "content": "Pomóż mi zaplanować budżet",
    "agentType": "FINANCE"
  }
}
```

### 3. WebSocket (Real-time Streaming)

**Testowanie z `wscat`:**

```bash
# Zainstaluj wscat
npm install -g wscat

# Połącz się z WebSocket
wscat -c ws://localhost:8000/ws?token=your-jwt-token

# Wyślij wiadomość (w sesji wscat)
{"type": "message", "content": "Witaj!", "agent_type": "general"}

# Otrzymasz streaming response token po tokenie!
```

**Testowanie z JavaScript:**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_TOKEN');

ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Test message',
    agent_type: 'health'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### 4. Semantic Caching

**Testowanie cache hit rate:**

```bash
# Pierwsze zapytanie (cache MISS)
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"session_id": "test", "message": "Jak zaoszczędzić pieniądze?"}'

# Podobne zapytanie (cache HIT - 70-90% szybsze!)
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"session_id": "test", "message": "Jak oszczędzać finanse?"}'

# Sprawdź metryki cache
curl http://localhost:8000/metrics | grep cache_hit_rate
```

### 5. Rate Limiting

**Testowanie limitów:**

```bash
# Sprawdź nagłówki rate limit
curl -I http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN"

# Nagłówki:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 1640000000

# Test przekroczenia limitu (wyślij 101 requestów szybko)
for i in {1..105}; do
  curl -X GET http://localhost:8000/api/analytics/dashboard \
    -H "Authorization: Bearer $TOKEN"
done

# Oczekiwany status po przekroczeniu: 429 Too Many Requests
```

### 6. Text-to-Speech (TTS)

```bash
# Generuj mowę z tekstu
curl -X POST http://localhost:8000/api/multimodal/tts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Witaj w LifeAI! Jak mogę Ci pomóc?",
    "voice": "nova",
    "model": "tts-1-hd"
  }' \
  --output speech.mp3

# Odtwórz audio
mpv speech.mp3  # lub vlc, ffplay, itp.
```

**Dostępne głosy:**
- `alloy` - Neutralny i zbalansowany
- `echo` - Męski, czysty
- `fable` - Brytyjski akcent
- `onyx` - Głęboki męski
- `nova` - Żeński, energetyczny ⭐
- `shimmer` - Żeński, miękki

### 7. DALL-E Image Generation

```bash
# Generuj obraz
curl -X POST http://localhost:8000/api/multimodal/image \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A serene meditation space with plants and natural light",
    "size": "1024x1024",
    "quality": "hd",
    "style": "natural"
  }' | jq .

# Otrzymasz URL do wygenerowanego obrazu
```

### 8. A/B Testing

```bash
# Sprawdź przypisaną wersję dla użytkownika
curl -X GET "http://localhost:8000/api/ab-test/variant?experiment=ai_response_style&user_id=user123" \
  -H "Authorization: Bearer $TOKEN"

# Odpowiedź:
# {"variant": "casual", "config": {"style": "casual", "temperature": 0.9}}

# Zapisz event dla eksperymentu
curl -X POST http://localhost:8000/api/ab-test/event \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "experiment": "ai_response_style",
    "user_id": "user123",
    "variant": "casual",
    "event_type": "conversion",
    "value": 5
  }'
```

### 9. Internationalization (i18n)

```bash
# Frontend automatycznie wykrywa język z przeglądarki

# Ręczna zmiana języka:
# 1. Otwórz http://localhost:3000
# 2. Przejdź do Settings
# 3. Wybierz: Polski lub English

# Dostępne języki:
# - en (English)
# - pl (Polski)
```

### 10. PWA (Progressive Web App)

**Testowanie offline mode:**

1. Otwórz http://localhost:3000 w Chrome
2. Otwórz DevTools (F12)
3. Przejdź do Application > Service Workers
4. Zaznacz "Offline"
5. Odśwież stronę
6. ✅ Aplikacja działa offline!

**Instalacja jako aplikacja:**

1. Kliknij ikonę "Zainstaluj" w pasku adresu
2. Aplikacja otworzy się jako standalone app
3. Działa jak natywna aplikacja!

### 11. Long-Term Memory

```bash
# Wysyłaj wiadomości, aby system uczył się preferencji
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "session_id": "test",
    "message": "Jestem wegetarianinem i ćwiczę 3 razy w tygodniu"
  }'

# System automatycznie zapisze te fakty w pamięci długoterminowej

# Sprawdź zapisane wspomnienia
curl -X GET http://localhost:8000/api/memory/retrieve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "dieta",
    "user_id": "your-user-id"
  }'

# Odpowiedź zawiera relewanatne wspomnienia:
# [
#   {
#     "type": "preference",
#     "content": "User is vegetarian",
#     "importance": 9,
#     "timestamp": "..."
#   }
# ]
```

### 12. Load Testing (k6)

```bash
# Zainstaluj k6
brew install k6  # macOS
# lub
sudo apt install k6  # Linux

# Uruchom test obciążeniowy
k6 run tests/load/chat-api-load-test.js

# Test symuluje:
# - 50 → 100 → 200 użytkowników
# - Rzeczywiste scenariusze użytkowania
# - Chat, analitykę, health checks

# Metryki:
# ✓ http_req_duration........: avg=250ms p(95)=450ms
# ✓ http_req_failed..........: 0.12%
# ✓ chat_response_time.......: avg=1.2s p(95)=1.8s
```

---

## 🚀 Wdrożenie Produkcyjne

### Kubernetes + Helm

#### 1. Przygotowanie

```bash
# Zainstaluj Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Dodaj secrets
kubectl create secret generic lifeai-secrets \
  --from-literal=secret-key=$(openssl rand -hex 32) \
  --from-literal=openai-api-key=sk-your-key \
  --from-literal=postgres-password=$(openssl rand -base64 24)
```

#### 2. Instalacja

```bash
# Instaluj z Helm
helm install lifeai ./helm/lifeai \
  --namespace lifeai \
  --create-namespace \
  --values helm/lifeai/values.yaml

# Sprawdź status
helm status lifeai -n lifeai

# Sprawdź pods
kubectl get pods -n lifeai
```

#### 3. Aktualizacja

```bash
# Aktualizuj deployment
helm upgrade lifeai ./helm/lifeai \
  --namespace lifeai \
  --values helm/lifeai/values-prod.yaml

# Rollback (jeśli potrzeba)
helm rollback lifeai -n lifeai
```

#### 4. Skalowanie

```bash
# Ręczne skalowanie
kubectl scale deployment lifeai-backend --replicas=5 -n lifeai

# Auto-scaling (HPA już skonfigurowane w values.yaml)
kubectl get hpa -n lifeai

# Skaluje automatycznie 3-10 replik przy 70% CPU
```

#### 5. Monitoring

```bash
# Port-forward Grafana
kubectl port-forward svc/grafana 3001:80 -n lifeai

# Otwórz: http://localhost:3001
# Login: admin / (sprawdź secret)

# Dashboardy:
# - LifeAI Overview
# - API Performance
# - Database Metrics
# - Redis Cache Stats
```

### CI/CD Pipeline

**GitHub Actions już skonfigurowane!**

Pipeline automatycznie:
1. ✅ Uruchamia testy (unit + integration)
2. ✅ Skanuje bezpieczeństwo (Trivy + Snyk)
3. ✅ Buduje obrazy Docker
4. ✅ Pushuje do registry
5. ✅ Deployuje na Kubernetes
6. ✅ Uruchamia E2E testy
7. ✅ Uruchamia testy obciążeniowe
8. ✅ Rollback przy błędzie

**Workflow:** `.github/workflows/ci-cd.yaml`

```bash
# Push uruchamia pipeline
git push origin main

# Sprawdź status
# GitHub > Actions > Latest workflow run
```

### Zmienne Środowiskowe (Produkcja)

```bash
# Produkcyjny .env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Użyj zewnętrznych serwisów
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/lifeai
REDIS_URL=redis://prod-redis.example.com:6379/0

# Vector DB - Pinecone dla produkcji
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your-prod-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=lifeai-prod

# Zwiększ limity
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
```

---

## 🐛 Rozwiązywanie Problemów

### Problem: Backend nie startuje

```bash
# Sprawdź logi
docker-compose logs backend

# Typowe przyczyny:
# 1. Brak klucza OpenAI
grep OPENAI_API_KEY .env

# 2. Błąd połączenia z bazą
docker-compose exec backend python -c "from app.db.session import engine; engine.connect()"

# 3. Port zajęty
lsof -i :8000
# Zabij proces lub zmień port w docker-compose.yml
```

### Problem: Frontend nie łączy się z backendem

```bash
# Sprawdź CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -I http://localhost:8000/api/chat/start

# Dodaj origin do .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Restart backend
docker-compose restart backend
```

### Problem: PostgreSQL Out of Memory

```bash
# Zwiększ shared_buffers w docker-compose.yml
services:
  postgres:
    command: postgres -c shared_buffers=256MB -c max_connections=200

# Restart
docker-compose restart postgres
```

### Problem: Redis Connection Errors

```bash
# Sprawdź status
docker-compose exec redis redis-cli ping

# Wyczyść cache
docker-compose exec redis redis-cli FLUSHALL

# Sprawdź memory
docker-compose exec redis redis-cli INFO memory
```

### Problem: Wolne API Responses

```bash
# 1. Sprawdź cache hit rate
curl http://localhost:8000/metrics | grep cache

# 2. Enable query logging (development only!)
# W docker-compose.yml dla postgres:
command: postgres -c log_statement=all

# 3. Sprawdź slow queries
docker-compose exec postgres psql -U lifeai -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 4. Zwiększ connection pool
# W .env:
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=60
```

### Problem: OpenAI Rate Limits

```bash
# Włącz semantic caching (redukcja 70-90%!)
# Już włączone domyślnie w backend/app/cache/semantic_cache.py

# Sprawdź usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Rozważ upgrade planu: https://platform.openai.com/account/billing
```

### Problem: WebSocket Disconnects

```bash
# Zwiększ timeouty w nginx/ingress
# nginx.conf:
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;

# Kubernetes Ingress:
annotations:
  nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

### Czyszczenie i Reset

```bash
# Zatrzymaj wszystko
docker-compose down

# Usuń wszystkie dane (OSTROŻNIE!)
docker-compose down -v

# Pełny rebuild
docker-compose build --no-cache
docker-compose up -d

# Reset bazy danych
docker-compose exec postgres psql -U lifeai -c "DROP DATABASE lifeai; CREATE DATABASE lifeai;"
docker-compose exec backend alembic upgrade head
```

---

## 🎯 Zaawansowane Funkcje

### 1. Custom Agent Creation

```python
# backend/app/agents/custom_agent.py

from app.agents.base import BaseAgent
from app.core.agent_types import AgentRole

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.CUSTOM,
            system_prompt="You are a custom specialized agent..."
        )

    async def process_message(self, message: str, context: dict):
        # Custom logic
        response = await self.generate_response(message, context)
        return response

# Zarejestruj w app/agents/__init__.py
```

### 2. Custom Prompt Templates

```python
# backend/app/ai/prompt_templates.py

# Dodaj nowy template
CUSTOM_TEMPLATE = """
You are {role_name}.
User preferences: {preferences}
Recent context: {context}
Current time: {current_time}

Respond to: {user_message}
"""

# Użyj w agencie
template_engine.register_template("custom", CUSTOM_TEMPLATE)
```

### 3. Webhook Integration

```python
# backend/app/webhooks/handlers.py

from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook/conversation-end")
async def on_conversation_end(request: Request):
    data = await request.json()

    # Wyślij do zewnętrznego systemu
    await send_to_crm(data)
    await send_to_analytics(data)

    return {"status": "processed"}

# Zarejestruj w main.py
```

### 4. Custom Vector Store

```python
# backend/app/vector_store/custom_store.py

from app.vector_store.base import BaseVectorStore

class CustomVectorStore(BaseVectorStore):
    async def store_embedding(self, vector, metadata):
        # Implementacja dla Weaviate, Qdrant, etc.
        pass

    async def search_similar(self, query_vector, top_k=5):
        # Similarity search
        pass

# Konfiguruj w .env
VECTOR_DB_TYPE=custom
```

### 5. Multi-Tenant Support

```python
# backend/app/middleware/tenant.py

from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Wyciągnij tenant ID z nagłówka lub subdomeny
        tenant_id = request.headers.get("X-Tenant-ID")

        # Ustaw w context
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response

# Dodaj w main.py
app.add_middleware(TenantMiddleware)
```

---

## 📊 Monitoring i Metryki

### Prometheus Metrics

```bash
# Endpoint z metrykami
curl http://localhost:8000/metrics

# Kluczowe metryki:
# - http_requests_total
# - http_request_duration_seconds
# - cache_hit_rate
# - openai_api_calls_total
# - active_websocket_connections
# - database_connection_pool_size
```

### Grafana Dashboards

**Domyślne dashboardy:**
1. API Overview
2. Database Performance
3. Cache Analytics
4. AI/ML Metrics
5. User Activity

**Import custom dashboard:**

```bash
# Skopiuj JSON do Grafana UI
# Dashboard ID: 1860 (Node Exporter)
# Dashboard ID: 3662 (Prometheus)
```

### Logging

```bash
# Structured JSON logs
docker-compose logs backend | jq .

# Filter by level
docker-compose logs backend | jq 'select(.level=="ERROR")'

# Filter by request_id
docker-compose logs backend | jq 'select(.request_id=="req-123")'

# Realtime monitoring
docker-compose logs -f backend | jq -r '.timestamp + " " + .level + " " + .message'
```

---

## 🔐 Bezpieczeństwo

### Security Checklist

- [ ] ✅ SECRET_KEY jest losowy (min 32 bajty)
- [ ] ✅ Hasła do bazy danych są silne (min 16 znaków)
- [ ] ✅ .env NIE jest w git (w .gitignore)
- [ ] ✅ HTTPS w produkcji
- [ ] ✅ Rate limiting włączony
- [ ] ✅ CORS poprawnie skonfigurowany
- [ ] ✅ SQL Injection protection (SQLAlchemy ORM)
- [ ] ✅ XSS protection (React auto-escaping)
- [ ] ✅ CSRF protection dla formularzy
- [ ] ✅ JWT token expiration (24h)
- [ ] ✅ Dependency scanning (npm audit, safety)

### Regularne Audyty

```bash
# Python dependencies
pip3 install safety
safety check

# npm dependencies
npm audit

# Docker images
docker scan lifeai-backend:latest

# Secrets scanning
pip3 install gitleaks
gitleaks detect --source . --verbose
```

---

## 📚 Dodatkowe Zasoby

### Dokumentacja

- **API Documentation:** http://localhost:8000/docs (Swagger)
- **GraphQL Playground:** http://localhost:8000/graphql
- **Code Documentation:** Wygeneruj z `pydoc` / `jsdoc`

### Narzędzia Deweloperskie

```bash
# Backend REPL
docker-compose exec backend python

# Database console
docker-compose exec postgres psql -U lifeai

# Redis console
docker-compose exec redis redis-cli

# Frontend hot reload już włączony
```

### Przydatne Komendy

```bash
# Szybki restart po zmianach
docker-compose restart backend frontend

# Rebuild tylko jednego serwisu
docker-compose build backend
docker-compose up -d backend

# Sprawdź zużycie zasobów
docker stats

# Backup bazy danych
docker-compose exec postgres pg_dump -U lifeai lifeai > backup.sql

# Restore bazy danych
docker-compose exec -T postgres psql -U lifeai lifeai < backup.sql
```

---

## 🎓 Szkolenia i Przykłady

### Przykładowe Scenariusze

<details>
<summary><b>Scenariusz 1: Health Coach Conversation</b></summary>

```bash
# Rozpocznij sesję
curl -X POST http://localhost:8000/api/chat/start \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"agent_type": "health"}'

# Wiadomości:
# 1. "Chcę schudnąć 5kg w 2 miesiące"
# 2. "Jakie ćwiczenia polecasz?"
# 3. "Jak powinienem się odżywiać?"

# System:
# - Zapamiętuje cel (5kg w 2 miesiące)
# - Personalizuje rekomendacje
# - Generuje plan treningowy
```

</details>

<details>
<summary><b>Scenariusz 2: Financial Planning</b></summary>

```bash
# Agent finansowy
curl -X POST http://localhost:8000/api/chat/start \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"agent_type": "finance"}'

# Wiadomości:
# 1. "Mam 5000 zł miesięcznie, jak zaplanować budżet?"
# 2. "Chcę zaoszczędzić na mieszkanie"

# System:
# - Analizuje przychody
# - Tworzy budżet 50/30/20
# - Sugeruje strategie oszczędności
# - Wizualizuje w dashboard (wykresy!)
```

</details>

---

## 🤝 Wsparcie

### Zgłaszanie Problemów

1. Sprawdź [FAQ](#-rozwiązywanie-problemów)
2. Przeszukaj [GitHub Issues](https://github.com/yourusername/LifeAI/issues)
3. Utwórz nowy issue z:
   - Opisem problemu
   - Krokami do reprodukcji
   - Logami (`docker-compose logs`)
   - Informacjami o środowisku

### Community

- **Discord:** [Join Server](https://discord.gg/lifeai)
- **Forum:** [discuss.lifeai.com](https://discuss.lifeai.com)
- **Email:** support@lifeai.com

---

## 📄 Licencja

MIT License - patrz [LICENSE](LICENSE)

---

**🎉 Gratulacje! Masz teraz w pełni funkcjonalną, zaawansowaną platformę AI! 🎉**

Made with ❤️ by LifeAI Team
