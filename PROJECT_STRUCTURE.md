# LifeAI - Struktura Projektu

## Docelowa Struktura Katalogów

```
LifeAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app entry point
│   │   ├── config.py                        # Configuration management
│   │   │
│   │   ├── api/                             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                      # Chat endpoints (existing)
│   │   │   ├── timeline.py                  # Timeline endpoints (existing)
│   │   │   ├── auth.py                      # Authentication endpoints (NEW)
│   │   │   ├── agents.py                    # Agent management endpoints (NEW)
│   │   │   ├── multimodal.py                # Voice/Image upload endpoints (NEW)
│   │   │   └── user.py                      # User profile endpoints (NEW)
│   │   │
│   │   ├── core/                            # Core business logic (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py              # Agent Orchestrator
│   │   │   ├── router.py                    # Agent Router (LLM-based)
│   │   │   ├── intent_classifier.py         # Intent classification
│   │   │   ├── agent_registry.py            # Agent Registry
│   │   │   └── multi_agent_coordinator.py   # Multi-agent collaboration
│   │   │
│   │   ├── agents/                          # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # BaseAgent abstract class (NEW)
│   │   │   ├── chaos_agent.py               # Chaos Agent (existing)
│   │   │   ├── prompt.py                    # Agent prompts (existing)
│   │   │   │
│   │   │   ├── health/                      # Health Agent (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompts.py
│   │   │   │   └── tools.py
│   │   │   │
│   │   │   ├── finance/                     # Finance Agent (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompts.py
│   │   │   │   └── tools.py
│   │   │   │
│   │   │   ├── relations/                   # Relations Agent (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompts.py
│   │   │   │   └── tools.py
│   │   │   │
│   │   │   ├── personal_development/        # Personal Development Agent (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompts.py
│   │   │   │   └── tools.py
│   │   │   │
│   │   │   └── task_management/             # Task Management Agent (NEW)
│   │   │       ├── __init__.py
│   │   │       ├── agent.py
│   │   │       ├── prompts.py
│   │   │       └── tools.py
│   │   │
│   │   ├── memory/                          # Memory & Context System
│   │   │   ├── __init__.py
│   │   │   ├── summarizer.py                # Conversation summarizer (existing)
│   │   │   ├── context_manager.py           # Context management (NEW)
│   │   │   ├── vector_store.py              # Vector DB interface (NEW)
│   │   │   ├── embeddings.py                # Embedding generation (NEW)
│   │   │   └── retrieval.py                 # Semantic search (NEW)
│   │   │
│   │   ├── services/                        # External services
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py                # LLM client (existing)
│   │   │   ├── conversation.py              # Conversation service (existing)
│   │   │   ├── timeline_store.py            # Timeline storage (existing)
│   │   │   │
│   │   │   ├── multimodal/                  # Multimodal services (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asr.py                   # Speech-to-Text
│   │   │   │   ├── tts.py                   # Text-to-Speech
│   │   │   │   ├── vision.py                # Image analysis
│   │   │   │   └── document.py              # Document processing
│   │   │   │
│   │   │   ├── external/                    # External API integrations (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── open_banking.py          # Banking APIs
│   │   │   │   ├── health_api.py            # Health data APIs
│   │   │   │   └── calendar.py              # Calendar integrations
│   │   │   │
│   │   │   └── i18n/                        # Internationalization (NEW)
│   │   │       ├── __init__.py
│   │   │       ├── translator.py
│   │   │       └── locales/
│   │   │           ├── pl.json
│   │   │           ├── en.json
│   │   │           └── de.json
│   │   │
│   │   ├── models/                          # Database models
│   │   │   ├── __init__.py
│   │   │   ├── timeline.py                  # Timeline model (existing)
│   │   │   ├── user.py                      # User model (NEW)
│   │   │   ├── session.py                   # Session model (NEW)
│   │   │   ├── conversation.py              # Conversation model (NEW)
│   │   │   ├── agent_interaction.py         # Agent interaction logs (NEW)
│   │   │   └── feedback.py                  # User feedback (NEW)
│   │   │
│   │   ├── schemas/                         # Pydantic schemas (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── agent.py
│   │   │   ├── user.py
│   │   │   ├── multimodal.py
│   │   │   └── common.py
│   │   │
│   │   ├── db/                              # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── session.py                   # DB session (existing)
│   │   │   ├── base.py                      # Base model (existing)
│   │   │   └── migrations/                  # Alembic migrations (NEW)
│   │   │       └── versions/
│   │   │
│   │   ├── security/                        # Security & Auth (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                      # Authentication
│   │   │   ├── encryption.py                # Encryption utilities
│   │   │   ├── jwt.py                       # JWT handling
│   │   │   └── permissions.py               # Authorization
│   │   │
│   │   ├── utils/                           # Utilities (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   ├── metrics.py
│   │   │   └── helpers.py
│   │   │
│   │   └── tests/                           # Tests (NEW)
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_agents/
│   │       ├── test_api/
│   │       ├── test_core/
│   │       └── test_services/
│   │
│   ├── alembic.ini                          # Alembic config (NEW)
│   ├── requirements.txt                     # Dependencies (existing)
│   ├── requirements-dev.txt                 # Dev dependencies (NEW)
│   ├── Dockerfile                           # Docker config (existing)
│   ├── init.sql                             # DB init script (existing)
│   └── .env.example                         # Environment variables example (NEW)
│
├── frontend/
│   ├── app/                                 # Next.js 14 app directory
│   │   ├── page.tsx                         # Home page
│   │   ├── layout.tsx                       # Root layout
│   │   ├── chat/                            # Chat pages
│   │   ├── settings/                        # Settings pages
│   │   └── api/                             # API routes
│   │
│   ├── components/                          # React components
│   │   ├── chat/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── VoiceInput.tsx              # NEW
│   │   │   └── ImageUpload.tsx             # NEW
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/                              # shadcn/ui components
│   │
│   ├── lib/                                 # Utilities
│   │   ├── api.ts                           # API client (existing)
│   │   ├── session.ts                       # Session management (existing)
│   │   ├── audio.ts                         # Audio handling (NEW)
│   │   └── i18n.ts                          # i18n config (NEW)
│   │
│   ├── hooks/                               # React hooks (NEW)
│   │   ├── useChat.ts
│   │   ├── useVoice.ts
│   │   └── useAuth.ts
│   │
│   ├── store/                               # State management (NEW)
│   │   ├── chatStore.ts
│   │   ├── userStore.ts
│   │   └── settingsStore.ts
│   │
│   ├── styles/                              # Styles
│   │   └── globals.css
│   │
│   ├── public/                              # Static assets
│   │   ├── icons/
│   │   └── images/
│   │
│   ├── package.json                         # Dependencies (existing)
│   ├── next.config.js                       # Next.js config (existing)
│   ├── tsconfig.json                        # TypeScript config
│   ├── tailwind.config.js                   # Tailwind config
│   └── .env.local.example                   # Environment variables (NEW)
│
├── docs/                                    # Documentation (NEW)
│   ├── api/
│   │   ├── endpoints.md
│   │   └── authentication.md
│   ├── agents/
│   │   ├── creating-agents.md
│   │   └── agent-api.md
│   ├── deployment/
│   │   ├── docker.md
│   │   ├── kubernetes.md
│   │   └── production.md
│   └── development/
│       ├── setup.md
│       ├── contributing.md
│       └── testing.md
│
├── scripts/                                 # Utility scripts (NEW)
│   ├── setup.sh
│   ├── migrate.sh
│   └── seed_db.py
│
├── .github/                                 # GitHub configs (NEW)
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── test.yml
│
├── docker-compose.yml                       # Docker Compose (existing)
├── docker-compose.prod.yml                  # Production compose (NEW)
├── .gitignore                               # Git ignore (existing)
├── README.md                                # Project README (NEW)
├── ARCHITECTURE.md                          # Architecture doc (NEW)
├── PROJECT_STRUCTURE.md                     # This file (NEW)
└── LICENSE                                  # License (NEW)
```

## Kluczowe Zmiany

### Backend
1. **Nowa struktura `core/`** - centralny system orchestracji agentów
2. **Rozbudowa `agents/`** - podkatalogi dla każdego wyspecjalizowanego agenta
3. **Nowy `memory/`** - zaawansowany system pamięci z vector DB
4. **Nowy `services/multimodal/`** - obsługa głosu i obrazów
5. **Nowy `security/`** - authentication i encryption
6. **Nowy `schemas/`** - Pydantic schemas dla walidacji
7. **Nowy `tests/`** - kompleksowe testy

### Frontend
1. **Komponenty multimodalne** - VoiceInput, ImageUpload
2. **State management** - Zustand stores
3. **React hooks** - custom hooks dla funkcjonalności
4. **i18n** - internacjonalizacja

### Infrastruktura
1. **Dokumentacja** - katalog `docs/`
2. **CI/CD** - GitHub Actions workflows
3. **Scripts** - utility scripts dla deployment

## Migracja z Obecnej Struktury

### Zachowane Pliki
- ✅ `backend/app/main.py`
- ✅ `backend/app/api/chat.py`
- ✅ `backend/app/api/timeline.py`
- ✅ `backend/app/agents/chaos_agent.py`
- ✅ `backend/app/agents/prompt.py`
- ✅ `backend/app/services/llm_client.py`
- ✅ `backend/app/services/conversation.py`
- ✅ `backend/app/memory/summarizer.py`
- ✅ `backend/app/models/timeline.py`

### Do Refaktoryzacji
- 🔄 `backend/app/services/conversation.py` - integracja z nowym orchestratorem
- 🔄 `backend/app/agents/chaos_agent.py` - adaptacja do BaseAgent

### Nowe Pliki
- ➕ Wszystkie pliki w `core/`
- ➕ Nowi agenci (health, finance, etc.)
- ➕ Multimodal services
- ➕ Security layer
- ➕ Tests

---

**Next Steps**: Implementacja poszczególnych komponentów zgodnie z roadmapą
