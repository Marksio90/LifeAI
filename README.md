# 🧠 LifeAI Platform

**Advanced AI-Powered Life Guidance & Prediction System**

LifeAI is a comprehensive multi-agent AI platform that provides personalized guidance across all aspects of life: health, finance, psychology, relationships, and personal development. Using state-of-the-art AI technology, it creates a digital twin of the user, predicts life scenarios, and offers actionable insights.

---

## 🎯 Vision

Create the ultimate AI life companion that:
- **Understands** you deeply through continuous learning
- **Predicts** life scenarios and outcomes
- **Guides** you with evidence-based, personalized advice
- **Evolves** with you through feedback and adaptation
- **Respects** your privacy with end-to-end encryption

---

## 🏗️ Architecture

LifeAI is built using a **6-layer architecture**, each with specific responsibilities:

### **Layer 0: Foundation (Core System)**

#### 0.1. Core Orchestrator
The heart of the system. Receives user input, recognizes intent, routes to appropriate agents, and merges responses.

**Key Components:**
- `CoreOrchestrator`: Main controller
- `IntentRecognizer`: Uses LLM to classify user intent
- `ResponseMerger`: Synthesizes multi-agent responses

**Location:** `src/core/orchestrator.py`

#### 0.2. Identity & Context Engine
Builds and maintains user identity, values, goals, and life context.

**Key Components:**
- `IdentityEngine`: User profile management
- `LifeOntology`: Structured life representation
- Graph database integration (Neo4j)

**Location:** `src/core/identity_engine.py`

---

### **Layer 1: Multimodal Input** (Planned)

Will support:
- Text (chat, journaling)
- Voice (speech-to-text, emotion analysis)
- Image (vision, OCR, emotion recognition)
- Biosensors (health data, HRV, sleep)

**Location:** `src/input/`

---

### **Layer 2: Multi-Agent AI** ✅

Specialized AI agents, each expert in their domain:

#### Health Agent
- Physical health, symptoms, wellness
- Fitness, exercise, training
- Nutrition, diet, sleep
- **Location:** `src/agents/health/health_agent.py`

#### Finance Agent
- Budgeting, expense management
- Investment strategies
- Financial planning, risk assessment
- **Location:** `src/agents/finance/finance_agent.py`

#### Psychology Agent
- Emotional awareness and regulation
- CBT/ACT principles
- Stress management
- Crisis detection
- **Location:** `src/agents/psychology/psychology_agent.py`

#### Additional Agents (Planned)
- Relationships Agent
- Personal Development Agent
- Meta Supervisor Agent

**Base Framework:** `src/agents/base.py`

---

### **Layer 3: Prediction & Simulation** (Planned)

The game-changing layer:

- **Life Simulation Engine**: Simulates future scenarios using RL
- **Digital Twin Engine**: Creates and evolves user's digital twin
- **Confidence & Uncertainty Layer**: Measures prediction certainty

**Location:** `src/prediction/`

---

### **Layer 4: Memory & Learning** ✅

Manages conversation history and learning:

**Key Components:**
- Short-term memory (Redis): Current conversation
- Long-term memory (PostgreSQL): User history
- Vector database (Pinecone/Qdrant): Semantic search
- Learning loop: Feedback-based improvement

**Location:** `src/memory/memory_system.py`

---

### **Layer 5: Security & Privacy** (Planned)

Ensures data protection:
- End-to-end encryption
- GDPR/RODO compliance
- Zero-knowledge architecture
- User data control

**Location:** `src/security/`

---

### **Layer 6: Product & Business** (Planned)

User-facing interfaces and monetization:
- Web app (Next.js)
- Mobile apps (iOS/Android)
- Subscription model
- API/SDK for developers

**Location:** `frontend/`

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Neo4j (optional, for advanced features)
- OpenAI API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/LifeAI.git
cd LifeAI
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

4. **Start services:**
```bash
# Start PostgreSQL
sudo service postgresql start

# Start Redis
sudo service redis-server start

# Optional: Start Neo4j
sudo service neo4j start
```

5. **Run the application:**
```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## 📡 API Usage

### Create a Session

```bash
curl -X POST "http://localhost:8000/session/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "user_id": "user123",
  "created_at": "2025-12-19T10:00:00"
}
```

### Send a Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "abc-123-def",
    "message": "I feel stressed about work and it affects my sleep"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "response": "I understand work stress can significantly impact sleep quality...",
  "confidence": 0.85,
  "intent": "multi_domain",
  "agents_used": ["psychology", "health"],
  "timestamp": "2025-12-19T10:01:00"
}
```

### Submit Feedback

```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def",
    "message_index": 1,
    "helpful": true,
    "rating": 5,
    "comment": "Very helpful advice!"
  }'
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_orchestrator.py
```

---

## 📊 System Statistics

Get real-time system statistics:

```bash
curl http://localhost:8000/statistics
```

**Response:**
```json
{
  "orchestrator": {
    "registered_agents": 3,
    "total_costs": 0.0523,
    "agent_costs": {
      "health": 0.0123,
      "finance": 0.0234,
      "psychology": 0.0166
    }
  },
  "memory": {
    "active_sessions": 12,
    "total_messages": 347,
    "avg_messages_per_session": 28.9
  }
}
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all configuration options:

**Required:**
- `OPENAI_API_KEY`: OpenAI API key
- `POSTGRES_PASSWORD`: PostgreSQL password
- `NEO4J_PASSWORD`: Neo4j password
- `SECRET_KEY`: JWT secret key

**Optional:**
- `ANTHROPIC_API_KEY`: For Claude models
- `ASSEMBLYAI_API_KEY`: For advanced voice processing
- `PINECONE_API_KEY`: For vector search

### Agent Configuration

Modify agent behavior in `config/settings.py`:

```python
max_agents_per_request = 5
agent_timeout_seconds = 30
confidence_threshold = 0.7
```

---

## 🎨 Project Structure

```
LifeAI/
├── config/                    # Configuration files
│   ├── settings.py           # Application settings
│   └── __init__.py
├── src/
│   ├── core/                 # Layer 0: Core System
│   │   ├── orchestrator.py   # Main orchestrator
│   │   ├── intent_recognizer.py
│   │   ├── response_merger.py
│   │   ├── identity_engine.py
│   │   └── models.py         # Data models
│   ├── agents/               # Layer 2: Multi-Agent AI
│   │   ├── base.py           # Base agent class
│   │   ├── health/
│   │   │   └── health_agent.py
│   │   ├── finance/
│   │   │   └── finance_agent.py
│   │   └── psychology/
│   │       └── psychology_agent.py
│   ├── memory/               # Layer 4: Memory System
│   │   └── memory_system.py
│   ├── input/                # Layer 1: Input processing
│   │   ├── text/
│   │   ├── voice/
│   │   └── vision/
│   ├── prediction/           # Layer 3: Prediction & Simulation
│   │   ├── simulation/
│   │   └── digital_twin/
│   ├── security/             # Layer 5: Security
│   └── api/                  # API Layer
│       └── main.py           # FastAPI application
├── tests/                    # Test suite
├── frontend/                 # Web interface (planned)
├── docs/                     # Documentation
├── data/                     # Data storage
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🛠️ Development Roadmap

### ✅ Phase 1: MVP (Completed)
- [x] Core Orchestrator
- [x] Intent Recognition
- [x] Multi-Agent Framework
- [x] Health, Finance, Psychology Agents
- [x] Memory System
- [x] Identity Engine
- [x] REST API

### 🚧 Phase 2: Enhanced Functionality (In Progress)
- [ ] Multimodal input (voice, image)
- [ ] Prediction & Simulation Engine
- [ ] Digital Twin v1
- [ ] Web interface
- [ ] Additional agents (relationships, personal development)
- [ ] Meta supervisor agent

### 🔮 Phase 3: Advanced Features (Planned)
- [ ] Life simulation scenarios
- [ ] Biofeedback integration
- [ ] Confidence & uncertainty quantification
- [ ] Mobile apps
- [ ] Blockchain for data sovereignty
- [ ] SDK for external developers

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Write docstrings for all functions and classes
- Add type hints where appropriate
- Write tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔒 Privacy & Ethics

LifeAI is designed with privacy and ethics as core principles:

- **User Control**: You own your data
- **Transparency**: We explain how decisions are made
- **No Manipulation**: Guidance, not persuasion
- **Professional Boundaries**: We recommend professional help when needed
- **Crisis Support**: Immediate escalation for crisis situations

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/LifeAI/issues)
- **Email**: support@lifeai.platform
- **Discord**: [Join our community](https://discord.gg/lifeai)

---

## 🙏 Acknowledgments

Built with:
- OpenAI GPT-4
- FastAPI
- LangChain
- PostgreSQL
- Redis
- Neo4j

Inspired by research in:
- Multi-agent systems
- Digital twins
- Reinforcement learning
- Cognitive behavioral therapy
- Financial planning
- Preventive health

---

## ⚠️ Disclaimer

LifeAI is a guidance platform and does NOT replace:
- Medical professionals for health matters
- Licensed therapists for mental health
- Financial advisors for investment decisions
- Legal counsel for legal matters

Always consult qualified professionals for important life decisions.

---

**Made with ❤️ for human flourishing**

Version: 0.1.0 (MVP)
Last Updated: 2025-12-19
