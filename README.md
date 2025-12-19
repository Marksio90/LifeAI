# LifeAI - Wieloagentowa Platforma AI

![Version](https://img.shields.io/badge/version-2.0.0-blue)
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
- **Context Management** - Pamięć konwersacji i personalizacja
- **Multilingual Support** - Polski, Angielski, Niemiecki

## 🚀 Szybki Start

### Wymagania
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- OpenAI API key

### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone <repo-url>
cd LifeAI
```

2. **Skonfiguruj zmienne środowiskowe**
```bash
# Backend
cd backend
cp .env.example .env
# Edytuj .env i dodaj OPENAI_API_KEY
```

3. **Uruchom z Docker Compose**
```bash
docker-compose up --build
```

Aplikacja będzie dostępna pod:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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

### Phase 2: Advanced Features (W trakcie)
- [ ] Vector database for memory
- [ ] User authentication
- [ ] Advanced context management
- [ ] Feedback learning system

### Phase 3: Multimodal (Planowane)
- [ ] Speech-to-Text (Whisper)
- [ ] Text-to-Speech (OpenAI TTS)
- [ ] Image analysis (GPT-4 Vision)
- [ ] Document processing

### Phase 4: Production (Planowane)
- [ ] Kubernetes deployment
- [ ] Monitoring & logging
- [ ] CI/CD pipeline
- [ ] Mobile apps

## 📚 Dokumentacja

- [Architecture Documentation](./ARCHITECTURE.md) - Szczegółowa architektura systemu
- [Project Structure](./PROJECT_STRUCTURE.md) - Struktura katalogów
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger)

## 🧪 Testowanie

```bash
cd backend
pytest
```

## 🤝 Kontrybucje

W przygotowaniu - obecnie w fazie rozwoju.

## 📄 Licencja

W przygotowaniu.

## 📧 Kontakt

W przygotowaniu.

---

**Wersja:** 2.0.0
**Status:** Development
**Ostatnia aktualizacja:** 2025-12-19
