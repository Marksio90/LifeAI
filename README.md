# LifeAI - Wieloagentowa Platforma AI

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal)
![Next.js](https://img.shields.io/badge/Next.js-14+-black)

Wieloagentowa, multimodalna platforma AI wspierająca użytkowników w życiu codziennym - zdrowie, finanse, relacje, rozwój osobisty i zarządzanie zadaniami.

## 🌟 Funkcjonalności

### Wyspecjalizowani Agenci
- **🏥 Health Agent** - Fitness, dieta, wellness, zdrowy styl życia
- **💰 Finance Agent** - Budżetowanie, oszczędności, planowanie finansowe
- **❤️ Relations Agent** - Relacje, komunikacja, wsparcie emocjonalne
- **🎯 Personal Development Agent** - Kariera, edukacja, rozwój osobisty
- **📋 Task Management Agent** - Zadania, produktywność, zarządzanie czasem
- **💬 General Agent** - Ogólne rozmowy i punkt wejścia

### Architektura
- **LLM-based Intent Classification** - Inteligentne rozpoznawanie intencji użytkownika
- **Dynamic Agent Routing** - Automatyczny wybór odpowiedniego agenta
- **Multi-Agent Collaboration** - Współpraca agentów dla złożonych zapytań
- **Vector Database Memory** - Długookresowa pamięć z semantic search
- **Multimodal AI** - Obsługa głosu, obrazów i tekstu
- **Context Management** - Pamięć konwersacji i personalizacja
- **Multilingual Support** - Polski, Angielski, Niemiecki

### Nowe Funkcjonalności (v2.1)
- ✅ **Voice Input** - Speech-to-text z OpenAI Whisper (100+ języków)
- ✅ **Voice Output** - Text-to-speech z naturalnymi głosami (6 opcji)
- ✅ **Vision AI** - Analiza obrazów z GPT-4 Vision
- ✅ **Food Recognition** - Rozpoznawanie jedzenia i analiza kalorii
- ✅ **OCR** - Ekstrakcja tekstu z obrazów
- ✅ **Long-term Memory** - Vector database dla kontekstu i personalizacji
- ✅ **Semantic Search** - Wyszukiwanie istotnych wspomnień

### Funkcje Enterprise (v3.0) 🆕
- ✅ **GraphQL API** - Zaawansowane query z Strawberry
- ✅ **WebSocket Server** - Real-time streaming odpowiedzi
- ✅ **Semantic Caching** - 70-90% redukcja kosztów OpenAI!
- ✅ **Rate Limiting** - Redis sliding window, multi-tier limity
- ✅ **Kubernetes/Helm** - Production-ready deployment
- ✅ **CI/CD Pipeline** - GitHub Actions, automated testing
- ✅ **Load Testing** - k6 performance tests
- ✅ **A/B Testing** - Framework eksperymentów
- ✅ **i18n** - Multi-language support (EN/PL)
- ✅ **TTS + DALL-E** - Voice synthesis & image generation
- ✅ **PWA** - Progressive Web App z offline mode
- ✅ **Advanced Monitoring** - Prometheus + Grafana

## 🚀 Szybki Start

> **📖 PEŁNA DOKUMENTACJA:** Zobacz [INSTALLATION.md](./INSTALLATION.md) dla kompletnego przewodnika instalacji, testowania i wdrożenia produkcyjnego!

### Wymagania
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- OpenAI API key

### Instalacja (Automatyczna)

```bash
# 1. Sklonuj repozytorium
git clone <repo-url>
cd LifeAI

# 2. Uruchom automatyczną instalację
chmod +x setup.sh test.sh
./setup.sh

# 3. Gotowe! Aplikacja działa
```

**Skrypt automatycznie:**
- ✅ Sprawdzi wymagania
- ✅ Utworzy bezpieczne klucze
- ✅ Zainstaluje zależności
- ✅ Zbuduje kontenery Docker
- ✅ Uruchomi wszystkie serwisy

Aplikacja będzie dostępna pod:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **GraphQL:** http://localhost:8000/graphql

### Rozwój Lokalny (bez Dockera)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Struktura Projektu

```
LifeAI/
├── backend/                      # Backend FastAPI
│   ├── app/
│   │   ├── core/                 # Core multi-agent system
│   │   │   ├── orchestrator.py   # Main orchestrator
│   │   │   ├── router.py         # Agent router
│   │   │   ├── intent_classifier.py
│   │   │   └── agent_registry.py
│   │   ├── agents/               # Specialized agents
│   │   │   ├── base.py           # Base agent class
│   │   │   ├── general/          # General conversation agent
│   │   │   ├── finance/          # Finance agent
│   │   │   ├── health/           # Health agent
│   │   │   ├── relations/        # Relations agent
│   │   │   └── task_management/  # Task management agent
│   │   ├── api/                  # API endpoints
│   │   ├── services/             # External services
│   │   ├── models/               # Database models
│   │   └── schemas/              # Pydantic schemas
│   └── requirements.txt
├── frontend/                     # Frontend Next.js
│   ├── app/
│   ├── components/
│   └── lib/
├── docs/                         # Documentation
├── ARCHITECTURE.md               # Architecture documentation
├── PROJECT_STRUCTURE.md          # Project structure details
└── docker-compose.yml
```

## 🎙️ Multimodal API

### Voice Input (Speech-to-Text)
```bash
curl -X POST http://localhost:8000/multimodal/transcribe \
  -F "file=@audio.mp3" \
  -F "language=pl"
```

### Voice Output (Text-to-Speech)
```bash
curl -X POST http://localhost:8000/multimodal/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Witaj! Jak mogę Ci pomóc?",
    "voice": "nova",
    "high_quality": true
  }' --output speech.mp3
```

### Image Analysis
```bash
curl -X POST http://localhost:8000/multimodal/analyze-image \
  -F "file=@image.jpg" \
  -F "prompt=Co jest na tym zdjęciu?" \
  -F "analysis_type=general"
```

### Food Recognition
```bash
curl -X POST http://localhost:8000/multimodal/analyze-image \
  -F "file=@meal.jpg" \
  -F "analysis_type=food"
```

### OCR (Text Extraction)
```bash
curl -X POST http://localhost:8000/multimodal/ocr \
  -F "file=@document.jpg"
```

## 🔧 API Użycie

### Rozpocznij sesję czatu
```bash
POST /chat/start
{
  "language": "pl"  # pl, en, de
}
```

### Wyślij wiadomość
```bash
POST /chat/message
{
  "session_id": "uuid",
  "message": "Jak mogę zaoszczędzić 1000 zł miesięcznie?"
}
```

Odpowiedź:
```json
{
  "reply": "Odpowiedź od agenta...",
  "metadata": {
    "agents_used": ["finance_agent_001"],
    "routing_type": "single_agent",
    "confidence": 0.95
  }
}
```

### Multi-Agent Query
```bash
POST /chat/message
{
  "session_id": "uuid",
  "message": "Chcę schudnąć 5kg i zaoszczędzić na siłownię"
}
```

Odpowiedź wykorzysta **Health Agent** + **Finance Agent**:
```json
{
  "reply": "Zintegrowana odpowiedź z obu agentów...",
  "metadata": {
    "agents_used": ["health_agent_001", "finance_agent_001"],
    "routing_type": "multi_agent"
  }
}
```

## 🎯 Przykłady Użycia

### Health Agent
```
User: "Chcę zacząć biegać, jak się do tego przygotować?"
System: [Health Agent] "Świetny pomysł! Oto plan..."
```

### Finance Agent
```
User: "Jak planować budżet domowy?"
System: [Finance Agent] "Oto sprawdzona metoda 50/30/20..."
```

### Relations Agent
```
User: "Jak rozwiązać konflikt z partnerem?"
System: [Relations Agent] "Komunikacja jest kluczowa..."
```

### Multi-Agent Collaboration
```
User: "Chcę zacząć biegać maratony i potrzebuję budżetu na sprzęt"
System: [Health + Finance Agents] "Oto zintegrowany plan..."
```

## 📊 Statystyki Systemu

```bash
GET /chat/stats
```

Zwraca:
```json
{
  "active_sessions": 5,
  "registered_agents": 6,
  "active_agents": 6
}
```

## 🏗️ Architektura

### Przepływ Zapytania

```
User Message
    ↓
API Gateway (/chat/message)
    ↓
Orchestrator
    ↓
Intent Classifier (LLM)
    ↓
Agent Router
    ↓
Agent Registry → Find Capable Agents
    ↓
[Single Agent] OR [Multi-Agent Collaboration]
    ↓
Response Aggregation (if multi-agent)
    ↓
Return to User
```

### Główne Komponenty

1. **Orchestrator** - Zarządza sesjami i cyklem życia konwersacji
2. **Intent Classifier** - Klasyfikuje intencję użytkownika (LLM)
3. **Agent Router** - Wybiera i koordynuje agentów
4. **Agent Registry** - Rejestr wszystkich dostępnych agentów
5. **Specialized Agents** - Wyspecjalizowani agenci dla różnych dziedzin

## 🔐 Bezpieczeństwo

- **API Authentication** (W przygotowaniu)
- **Rate Limiting** (W przygotowaniu)
- **Data Encryption** (W przygotowaniu)
- **GDPR Compliance** (W przygotowaniu)

## 🛣️ Roadmap

### Phase 1: Core System ✅
- [x] Multi-agent architecture
- [x] LLM-based routing
- [x] 5 specialized agents
- [x] API endpoints

### Phase 2: Advanced Features ✅
- [x] Vector database for memory
- [x] Long-term memory with semantic search
- [x] Advanced context management
- [x] Preference learning system
- [x] Dynamic prompt templates

### Phase 3: Multimodal ✅
- [x] Speech-to-Text (Whisper)
- [x] Text-to-Speech (OpenAI TTS)
- [x] Image analysis (GPT-4 Vision)
- [x] DALL-E image generation
- [x] Document processing (OCR)

### Phase 4: Enterprise ✅
- [x] Kubernetes deployment (Helm charts)
- [x] Monitoring & logging (Prometheus + Grafana)
- [x] CI/CD pipeline (GitHub Actions)
- [x] WebSocket real-time streaming
- [x] GraphQL API
- [x] Semantic caching (70-90% cost reduction!)
- [x] Rate limiting (Redis sliding window)
- [x] A/B testing framework
- [x] PWA with offline support

### Phase 5: Production Optimizations (Planowane)
- [ ] Mobile apps (React Native)
- [ ] Admin dashboard
- [ ] Analytics platform
- [ ] Multi-tenant support

## 📚 Dokumentacja

- **[📖 INSTALLATION.md](./INSTALLATION.md)** - **Kompletny przewodnik instalacji i testowania** ⭐
- [Architecture Documentation](./ARCHITECTURE.md) - Szczegółowa architektura systemu
- [Project Structure](./PROJECT_STRUCTURE.md) - Struktura katalogów
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger)
- [GraphQL Playground](http://localhost:8000/graphql) - GraphQL IDE

## 🧪 Testowanie

```bash
# Uruchom pełny test suite
./test.sh

# Lub wybrane testy:
./test.sh --unit          # Backend + Frontend unit tests
./test.sh --integration   # API integration tests
./test.sh --e2e          # End-to-end Playwright tests
./test.sh --load         # k6 load/performance tests
```

**Test Coverage:**
- Backend: `backend/htmlcov/index.html`
- Frontend: `frontend/coverage/index.html`
- E2E Reports: `frontend/playwright-report/index.html`

## 🤝 Kontrybucje

W przygotowaniu - obecnie w fazie rozwoju.

## 📄 Licencja

W przygotowaniu.

## 📧 Kontakt

W przygotowaniu.

---

**Wersja:** 3.0.0 🎉
**Status:** Production Ready
**Ostatnia aktualizacja:** 2025-12-25
