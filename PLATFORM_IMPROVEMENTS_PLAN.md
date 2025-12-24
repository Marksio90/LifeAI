# 🚀 KOMPLETNY PLAN ULEPSZEŃ PLATFORMY LIFEAI

> **Data audytu:** 2024-12-24
> **Wersja platformy:** 2.1.0
> **Status:** Plan rewolucyjnych ulepszeń

---

## 📋 SPIS TREŚCI

1. [Podsumowanie Wykonawcze](#podsumowanie-wykonawcze)
2. [Ulepszenia Wizualne (UI/UX)](#ulepszenia-wizualne-uiux)
3. [Ulepszenia Technologiczne](#ulepszenia-technologiczne)
4. [Ulepszenia Algorytmiczne i AI](#ulepszenia-algorytmiczne-i-ai)
5. [Nowe Funkcje](#nowe-funkcje)
6. [Plan Wdrożenia](#plan-wdrożenia)
7. [Metryki Sukcesu](#metryki-sukcesu)

---

## 🎯 PODSUMOWANIE WYKONAWCZE

### Stan Obecny
LifeAI to zaawansowana platforma AI z 6 specjalizowanymi agentami, wspierająca multimodalne interakcje (tekst, głos, obraz). Platforma ma solidne fundamenty, ale wymaga ulepszeń w 4 kluczowych obszarach:

- ✅ **Mocne strony:** Dobra architektura wieloagentowa, kompletne API, multimodalne wsparcie
- ⚠️ **Krytyczne błędy:** 2 synchroniczne wywołania w async context (blokujące)
- 📊 **Braki funkcjonalne:** Brak analityki, export konwersacji, zaawansowanej personalizacji
- 🎨 **UX do poprawy:** Podstawowy interfejs, brak onboardingu, limitowane wizualizacje

### Wizja Ulepszeń
Transformacja LifeAI w **najinteligentniejszą platformę AI** z:
- 🧠 Zaawansowaną pamięcią kontekstową i uczeniem się użytkownika
- 🎨 Nowoczesnym, intuicyjnym interfejsem z animacjami i visualizacjami
- ⚡ Wydajnością klasy enterprise (cache, optymalizacje)
- 🔐 Bezpieczeństwem zgodnym z GDPR i standardami enterprise
- 🌟 Unikalnymi funkcjami niedostępnymi w konkurencji

---

## 🎨 ULEPSZENIA WIZUALNE (UI/UX)

### 1. REDESIGN INTERFEJSU CZATU

#### 1.1 Modern Message Bubbles
**Aktualny stan:** Proste bąbelki z jednolitym kolorem
**Ulepszenie:**
```tsx
// Gradient backgrounds z glassmorphism
- User messages: Gradient primary-600 → primary-700 z subtle shadow
- Assistant messages: Frosted glass effect (backdrop-blur-xl)
- Hover effects: Subtle scale + glow
- Typing animation: Elegant wave effect zamiast trzech kropek
```

**Wizualizacja:**
```
┌─────────────────────────────────────┐
│  🧑 Ty                              │
│  ╭─────────────────────────────╮   │
│  │ Jak mogę schudnąć 5kg?      │   │ ← Gradient + shadow
│  ╰─────────────────────────────╯   │
│                                     │
│              🤖 LifeAI              │
│  ╭─────────────────────────────╮   │
│  │ 📊 Analizuję Twoje cele...  │   │ ← Frosted glass
│  │                              │   │
│  │ Oto spersonalizowany plan:  │   │
│  ╰─────────────────────────────╯   │
└─────────────────────────────────────┘
```

**Implementacja:**
- `components/MessageBubble.tsx` - nowy komponent
- Tailwind gradient utilities
- Framer Motion dla animacji

#### 1.2 Rich Message Types

**Nowe typy wiadomości:**

1. **Chart Messages** - Wykresy inline
```tsx
<MessageChart type="line" data={healthProgress} />
```

2. **Card Messages** - Karty informacyjne
```tsx
<MessageCard
  title="Twój Plan Fitness"
  items={[
    { icon: "💪", label: "Trening", value: "3x tydzień" },
    { icon: "🥗", label: "Kalorie", value: "1800 kcal" }
  ]}
/>
```

3. **Interactive Messages** - Przyciski akcji
```tsx
<MessageActions>
  <Button>✅ Zaakceptuj plan</Button>
  <Button>✏️ Dostosuj</Button>
</MessageActions>
```

4. **Timeline Messages** - Kamienie milowe
```tsx
<MessageTimeline events={[
  { date: "Tydzień 1", achievement: "Zrzuciłeś 1kg!" },
  { date: "Tydzień 2", achievement: "Cel osiągnięty!" }
]} />
```

**Przykład:**
```
Assistant: Oto Twój plan finansowy:

┌───────────────────────────────────┐
│ 💰 Plan Oszczędnościowy          │
├───────────────────────────────────┤
│ 📊 Miesięczny budżet              │
│    2000 zł przychód               │
│    -500 zł oszczędności (25%)     │
│    -1500 zł wydatki               │
│                                   │
│ [📈 Zobacz wykres] [💾 Zapisz]    │
└───────────────────────────────────┘
```

#### 1.3 Advanced Input Area

**Obecny stan:** Pojedyncze pole tekstowe + 3 przyciski
**Ulepszenie:**

```tsx
// Nowy komponent InputToolbar
<InputToolbar>
  {/* Smart suggestions */}
  <SuggestionChips>
    💪 "Jak schudnąć?"
    💰 "Pomóż z budżetem"
    ❤️ "Poprawa relacji"
  </SuggestionChips>

  {/* Multi-line textarea z auto-resize */}
  <SmartTextarea
    placeholder="Opisz co Cię nurtuje..."
    autoResize
    maxHeight={200}
  />

  {/* Expanded toolbar */}
  <Toolbar>
    <IconButton icon={<Camera />} tooltip="Zdjęcie" />
    <IconButton icon={<Mic />} tooltip="Głos" />
    <IconButton icon={<Paperclip />} tooltip="Załącznik" />
    <IconButton icon={<Emoji />} tooltip="Emoji" />
    <Divider />
    <IconButton icon={<Brain />} tooltip="Wybierz agenta" />
    <SendButton />
  </Toolbar>
</InputToolbar>
```

**Funkcje:**
- ✨ Auto-suggest na podstawie historii
- 📎 Upload dokumentów (PDF, CSV)
- 😊 Emoji picker
- 🎙️ Live waveform podczas nagrywania
- 🧠 Manual agent selection

#### 1.4 Sidebar z Kontekstem

**Nowa funkcja:** Rozwijany sidebar z informacjami kontekstowymi

```
┌──────────────┬────────────────────────┐
│ CHAT         │ SIDEBAR                │
│              │                        │
│ Messages     │ 📊 Aktualna sesja      │
│ ...          │ ├─ Agent: Health       │
│              │ ├─ Czas: 15 min        │
│              │ └─ Wiadomości: 12      │
│              │                        │
│              │ 🎯 Twoje cele          │
│              │ □ Schudnąć 5kg         │
│              │ ✓ Zaoszczędzić 2000zł  │
│              │                        │
│              │ 📈 Statystyki          │
│              │ Rozmowy: 47            │
│              │ Czas: 8.5h             │
│              │                        │
│              │ [📋 Historia]          │
│              │ [⚙️ Ustawienia]        │
└──────────────┴────────────────────────┘
```

### 2. DASHBOARD I ANALYTICS

#### 2.1 Personal Dashboard

**Nowa strona:** `/dashboard`

```tsx
export default function DashboardPage() {
  return (
    <Dashboard>
      {/* Hero stats */}
      <StatsGrid>
        <StatCard
          icon="💬"
          label="Rozmowy"
          value="47"
          trend="+12% vs ostatni tydzień"
        />
        <StatCard
          icon="⏱️"
          label="Czas aktywności"
          value="8.5h"
          trend="+2.3h"
        />
        <StatCard
          icon="🎯"
          label="Cele osiągnięte"
          value="5/8"
          trend="62%"
        />
        <StatCard
          icon="🔥"
          label="Seria dni"
          value="12"
          trend="Rekord!"
        />
      </StatsGrid>

      {/* Activity chart */}
      <Section title="Aktywność">
        <LineChart
          data={activityData}
          xAxis="data"
          yAxis="wiadomości"
          gradient
        />
      </Section>

      {/* Agent usage */}
      <Section title="Najczęściej używane agenty">
        <DonutChart
          data={[
            { agent: "Health", percent: 35 },
            { agent: "Finance", percent: 28 },
            { agent: "Relations", percent: 22 },
            { agent: "Tasks", percent: 15 }
          ]}
        />
      </Section>

      {/* Recent insights */}
      <Section title="Ostatnie spostrzeżenia">
        <InsightCards>
          <Insight
            icon="💪"
            title="Świetny postęp w fitness!"
            description="Twój plan treningowy działa - 3 kg zrzucone w 2 tygodnie"
          />
          <Insight
            icon="💰"
            title="Oszczędności rosną"
            description="Zaoszczędziłeś 450 zł więcej niż planowałeś"
          />
        </InsightCards>
      </Section>
    </Dashboard>
  );
}
```

#### 2.2 Conversation Analytics

**Rozszerzenie:** `/timeline` → `/conversations`

**Nowe funkcje:**
- 🔍 Zaawansowane filtrowanie (agent, data, tags, długość)
- 📊 Wykresy wykorzystania w czasie
- 🏷️ Auto-tagging konwersacji (AI-generated)
- ⭐ Ocena konwersacji (1-5 gwiazdek)
- 📥 Export (PDF, JSON, Markdown)
- 🔗 Udostępnianie (link z tokenem)

**Przykład widoku:**
```
┌─────────────────────────────────────────────┐
│ 💬 Moje Rozmowy                             │
├─────────────────────────────────────────────┤
│ Filters: [Agent ▼] [Data ▼] [Tags ▼]      │
├─────────────────────────────────────────────┤
│                                             │
│ ┌─────────────────────────────────────────┐│
│ │ 💪 Plan treningowy na luty             ││
│ │ Health Agent • 23 gru • 42 wiadomości  ││
│ │ Tags: #fitness #diet #weight-loss       ││
│ │ ⭐⭐⭐⭐⭐                                 ││
│ │ [👁️ Zobacz] [📥 Export] [🔗 Udostępnij]││
│ └─────────────────────────────────────────┘│
│                                             │
│ ┌─────────────────────────────────────────┐│
│ │ 💰 Budżet domowy                        ││
│ │ Finance Agent • 20 gru • 28 wiadomości ││
│ │ Tags: #budget #savings #expenses        ││
│ │ ⭐⭐⭐⭐                                  ││
│ │ [👁️ Zobacz] [📥 Export] [🔗 Udostępnij]││
│ └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### 3. ONBOARDING I FIRST-TIME EXPERIENCE

#### 3.1 Interactive Onboarding

**Nowa sekwencja:** Po pierwszym logowaniu

```tsx
// Step-by-step wizard
<OnboardingWizard steps={[
  {
    title: "Witaj w LifeAI! 👋",
    description: "Poznaj swoich inteligentnych asystentów",
    component: <AgentsIntro />
  },
  {
    title: "Wybierz swoje cele 🎯",
    description: "Na czym chcesz się skupić?",
    component: <GoalSelector options={[
      { icon: "💪", label: "Zdrowie i fitness", agent: "health" },
      { icon: "💰", label: "Finanse osobiste", agent: "finance" },
      { icon: "❤️", label: "Relacje", agent: "relations" },
      { icon: "🚀", label: "Rozwój kariery", agent: "personal_dev" }
    ]} />
  },
  {
    title: "Spersonalizuj doświadczenie ✨",
    description: "Dostosuj platformę do swoich potrzeb",
    component: <PreferencesSetup fields={[
      { key: "language", label: "Język", default: "pl" },
      { key: "voice", label: "Głos TTS", options: voices },
      { key: "theme", label: "Motyw", options: ["light", "dark", "auto"] },
      { key: "notifications", label: "Powiadomienia", type: "toggle" }
    ]} />
  },
  {
    title: "Wszystko gotowe! 🎉",
    description: "Rozpocznij swoją pierwszą rozmowę",
    component: <QuickStartSuggestions />
  }
]} />
```

#### 3.2 Contextual Tooltips

**Implementacja:** React Joyride lub custom tooltips

```tsx
// Tooltips dla pierwszych użyć
<Tooltip
  id="voice-recorder-intro"
  showOnce
  position="top"
>
  Kliknij tutaj, aby nagrać wiadomość głosową! 🎙️
</Tooltip>
```

**Miejsca tooltipów:**
- Nagrywanie głosu (pierwszy raz)
- Upload obrazu (pierwszy raz)
- Agent selector (jeśli używa multiagent)
- Export konwersacji

### 4. THEME SYSTEM & CUSTOMIZATION

#### 4.1 Advanced Theme Engine

**Obecnie:** Tylko dark/light mode
**Ulepszenie:** Pełna personalizacja

```tsx
// Theme presets
const themes = {
  ocean: {
    primary: "blue-500",
    background: "blue-50",
    accent: "teal-400"
  },
  sunset: {
    primary: "orange-500",
    background: "rose-50",
    accent: "amber-400"
  },
  forest: {
    primary: "green-600",
    background: "emerald-50",
    accent: "lime-400"
  },
  custom: {
    // User-defined colors
  }
};

// Theme customizer UI
<ThemeCustomizer>
  <ColorPicker label="Kolor główny" value={primary} />
  <ColorPicker label="Tło" value={background} />
  <ColorPicker label="Akcent" value={accent} />
  <PresetGallery presets={themes} />
</ThemeCustomizer>
```

#### 4.2 Accessibility Enhancements

**Nowe funkcje:**
- 🔤 Skalowanie czcionki (small, medium, large, xl)
- 🎨 High contrast mode
- ⌨️ Pełna obsługa klawiatury (shortcuts)
- 📢 Screen reader optimization (ARIA labels)
- 🔊 Sound effects toggle

**Keyboard Shortcuts:**
```
Cmd/Ctrl + Enter  → Wyślij wiadomość
Cmd/Ctrl + K      → Focus search
Cmd/Ctrl + /      → Pokaż shortcuts
Cmd/Ctrl + N      → Nowa rozmowa
Cmd/Ctrl + ,      → Ustawienia
```

### 5. MOBILE-FIRST RESPONSIVE DESIGN

#### 5.1 Mobile Optimizations

**Problemy obecne:**
- Desktop-first design
- Brak gesture support
- Toolbar zajmuje za dużo miejsca

**Ulepszenia:**

```tsx
// Mobile-optimized chat
<MobileChatView>
  {/* Swipe gestures */}
  <SwipeableMessage
    onSwipeLeft={() => deleteMessage()}
    onSwipeRight={() => replyToMessage()}
  />

  {/* Collapsible toolbar */}
  <FloatingActionButton
    onClick={toggleToolbar}
    icon={<Plus />}
  />

  {/* Bottom sheet dla opcji */}
  <BottomSheet>
    <Option icon={<Camera />}>Zdjęcie</Option>
    <Option icon={<Mic />}>Głos</Option>
    <Option icon={<File />}>Plik</Option>
  </BottomSheet>

  {/* Minimal header */}
  <MobileHeader compact />
</MobileChatView>
```

#### 5.2 Progressive Web App (PWA)

**Implementacja:**
- 📱 Installable app (Add to Home Screen)
- 🔔 Push notifications
- 📡 Offline mode (service workers)
- 🚀 Fast loading (pre-caching)

```ts
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
});

module.exports = withPWA({
  // ... config
});
```

### 6. ANIMATIONS & MICRO-INTERACTIONS

#### 6.1 Framer Motion Integration

**Animacje:**

```tsx
import { motion } from 'framer-motion';

// Message appear animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  <MessageBubble />
</motion.div>

// Agent thinking animation
<motion.div
  animate={{
    scale: [1, 1.1, 1],
    rotate: [0, 5, -5, 0]
  }}
  transition={{
    duration: 2,
    repeat: Infinity
  }}
>
  🤖
</motion.div>

// Sidebar slide-in
<motion.aside
  initial={{ x: -300 }}
  animate={{ x: 0 }}
  exit={{ x: -300 }}
  transition={{ type: "spring" }}
>
  <Sidebar />
</motion.aside>
```

#### 6.2 Loading States

**Zamiast prostego spinnera:**

```tsx
// Skeleton screens
<MessageSkeleton />

// Progress indicators
<LinearProgress value={uploadProgress} />

// Contextual loading
{isLoadingIntent && <Badge>Rozpoznaję intencję...</Badge>}
{isLoadingAgent && <Badge>Konsultuję z {agentName}...</Badge>}
{isGenerating && <Badge>Generuję odpowiedź...</Badge>}
```

### 7. VOICE & MULTIMODAL UX

#### 7.1 Enhanced Voice Recorder

**Ulepszenia:**

```tsx
<VoiceRecorderPro>
  {/* Real-time waveform */}
  <Waveform
    audioStream={stream}
    color="primary"
    animated
  />

  {/* Voice activity detection */}
  <VADIndicator
    threshold={0.3}
    onSpeechStart={() => console.log("Mówisz...")}
    onSilence={() => console.log("Cisza")}
  />

  {/* Real-time transcription preview */}
  <LiveTranscription text={partialTranscript} />

  {/* Auto-stop on silence */}
  <AutoStopConfig
    silenceDuration={2000} // 2s ciszy
    enabled={autoStop}
  />
</VoiceRecorderPro>
```

#### 7.2 Image Analysis Enhancement

**Obecny:** Prosta analiza
**Nowy:** Interaktywny widok

```tsx
<ImageAnalysisView image={uploadedImage}>
  {/* Image preview z annotations */}
  <AnnotatedImage
    src={image}
    annotations={detectedObjects}
    interactive
  />

  {/* Tabbed results */}
  <Tabs>
    <Tab label="Opis">
      {analysis.description}
    </Tab>
    <Tab label="Wykryte obiekty">
      <ObjectList items={detectedObjects} />
    </Tab>
    <Tab label="Tekst (OCR)">
      <ExtractedText text={ocrResult} copyable />
    </Tab>
    <Tab label="Podobne obrazy">
      <SimilarImages images={similarResults} />
    </Tab>
  </Tabs>

  {/* Action buttons */}
  <ActionBar>
    <Button>🔍 Szczegółowa analiza</Button>
    <Button>🍎 Rozpoznaj jedzenie</Button>
    <Button>📄 Wyciągnij tekst</Button>
  </ActionBar>
</ImageAnalysisView>
```

---

## ⚙️ ULEPSZENIA TECHNOLOGICZNE

### 1. KRYTYCZNE NAPRAWY (PRIORITY 0)

#### 1.1 Fix Async/Await Bugs

**Błąd #1:** `/backend/app/core/router.py:205`
```python
# PRZED (BŁĄD)
aggregated = call_llm(messages)

# PO (POPRAWKA)
aggregated = await call_llm(messages)
```

**Błąd #2:** `/backend/app/services/multimodal/vision.py:217`
```python
# PRZED (BŁĄD)
comparison = call_llm([{"role": "user", "content": comparison_prompt}])

# PO (POPRAWKA)
comparison = await call_llm([{"role": "user", "content": comparison_prompt}])
```

**Impact:** KRYTYCZNY - Blokuje event loop, powoduje timeouts

#### 1.2 Fix LLM Client

**Problem:** Synchronous OpenAI calls w async functions

```python
# /backend/app/services/llm_client.py

# PRZED
def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    **kwargs
) -> str:
    response = client.chat.completions.create(...)  # SYNC!
    return response.choices[0].message.content

# PO - Async version
async def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    **kwargs
) -> str:
    response = await aclient.chat.completions.acreate(  # ASYNC!
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs
    )
    return response.choices[0].message.content

# Utrzymaj sync version dla compatibility
def call_llm_sync(...):
    # Existing code
```

**Wymaga:** `from openai import AsyncOpenAI`

### 2. PERFORMANCE OPTIMIZATIONS

#### 2.1 Response Caching Layer

**Problem:** Każde zapytanie = kosztowne wywołania LLM
**Rozwiązanie:** Redis-based caching

```python
# /backend/app/cache/response_cache.py

from typing import Optional
import hashlib
import json

class ResponseCache:
    def __init__(self, redis_client, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def _generate_key(self, user_id: str, message: str, context_hash: str) -> str:
        """Generate cache key based on user, message, and context."""
        content = f"{user_id}:{message}:{context_hash}"
        return f"cache:response:{hashlib.sha256(content.encode()).hexdigest()}"

    async def get(self, user_id: str, message: str, context: dict) -> Optional[str]:
        """Get cached response if exists."""
        context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(user_id, message, context_hash)

        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set(self, user_id: str, message: str, context: dict, response: str):
        """Cache response."""
        context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(user_id, message, context_hash)

        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(response)
        )

# Usage in orchestrator
async def process_message(self, message: str):
    # Try cache first
    cached_response = await self.cache.get(user_id, message, context)
    if cached_response:
        return cached_response

    # Generate new response
    response = await self._generate_response(message)

    # Cache it
    await self.cache.set(user_id, message, context, response)
    return response
```

**Impact:** 50-80% reduction w LLM calls dla powtarzających się pytań

#### 2.2 Vector Database Implementation

**Problem:** In-memory vector store (brak persistence)
**Rozwiązanie:** Pinecone lub Qdrant

```python
# /backend/app/memory/vector_store.py

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict

class PineconeVectorStore(VectorStoreInterface):
    def __init__(self, api_key: str, environment: str):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = "lifeai-memories"

        # Create index if not exists
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embeddings
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=environment)
            )

        self.index = self.pc.Index(self.index_name)

    async def add(self, document: VectorDocument):
        """Add document with embedding."""
        self.index.upsert(vectors=[{
            "id": document.id,
            "values": document.embedding,
            "metadata": {
                "user_id": document.user_id,
                "content": document.content,
                "timestamp": document.timestamp.isoformat(),
                **document.metadata
            }
        }])

    async def search(
        self,
        query_embedding: List[float],
        filter_dict: Dict,
        top_k: int = 5
    ) -> List[VectorDocument]:
        """Semantic search."""
        results = self.index.query(
            vector=query_embedding,
            filter=filter_dict,
            top_k=top_k,
            include_metadata=True
        )

        return [
            VectorDocument(
                id=match.id,
                embedding=match.values,
                content=match.metadata["content"],
                user_id=match.metadata["user_id"],
                # ... parse metadata
            )
            for match in results.matches
        ]
```

**Benefits:**
- ✅ Persistent storage
- ✅ Fast semantic search (<100ms)
- ✅ Scalable do milionów vectorów
- ✅ Managed service (no ops)

#### 2.3 Database Query Optimization

**Problemy:**
- N+1 queries w relationships
- Brak indexes na często używanych polach
- Brak query caching

**Rozwiązania:**

```python
# /backend/app/models/user.py

from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"

    # ... existing fields

    # Add indexes
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_username', 'username'),
        Index('ix_users_created_at', 'created_at'),
    )

# /backend/app/models/conversation.py

class Conversation(Base):
    __tablename__ = "conversations"

    # ... existing fields

    __table_args__ = (
        Index('ix_conversations_user_id', 'user_id'),
        Index('ix_conversations_created_at', 'created_at'),
        Index('ix_conversations_session_id', 'session_id'),
        # Composite index dla common query
        Index('ix_conv_user_created', 'user_id', 'created_at'),
    )

# Eager loading dla relationships
from sqlalchemy.orm import selectinload

async def get_user_conversations(user_id: str, limit: int = 50):
    """Get conversations with eager loading."""
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .options(selectinload(Conversation.feedbacks))  # Avoid N+1
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return result.scalars().all()
```

#### 2.4 Connection Pooling

**Problem:** Brak connection pool configuration
**Rozwiązanie:** Proper pool settings

```python
# /backend/app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    # Connection pool settings
    pool_size=20,              # Max connections in pool
    max_overflow=10,           # Extra connections if pool full
    pool_timeout=30,           # Timeout waiting for connection
    pool_recycle=3600,         # Recycle connections after 1h
    pool_pre_ping=True,        # Test connection before using
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### 3. SCALABILITY IMPROVEMENTS

#### 3.1 Rate Limiting Enhancement

**Problem:** Basic rate limiting
**Rozwiązanie:** Tiered limits + token bucket

```python
# /backend/app/middleware/advanced_rate_limit.py

from enum import Enum

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

RATE_LIMITS = {
    UserTier.FREE: {
        "chat": (30, 60),      # 30 req/min
        "multimodal": (10, 60), # 10 req/min
        "daily_messages": 100
    },
    UserTier.PREMIUM: {
        "chat": (120, 60),      # 120 req/min
        "multimodal": (60, 60), # 60 req/min
        "daily_messages": 1000
    },
    UserTier.ENTERPRISE: {
        "chat": (500, 60),
        "multimodal": (200, 60),
        "daily_messages": 10000
    }
}

class TieredRateLimiter:
    async def check_limit(self, user_id: str, endpoint: str) -> bool:
        """Check rate limit based on user tier."""
        user_tier = await self._get_user_tier(user_id)
        limits = RATE_LIMITS[user_tier]

        # Check endpoint-specific limit
        if endpoint in limits:
            limit, window = limits[endpoint]
            # Token bucket algorithm
            # ...

        # Check daily limit
        daily_count = await self._get_daily_count(user_id)
        if daily_count >= limits["daily_messages"]:
            raise HTTPException(429, "Daily limit exceeded")

        return True
```

#### 3.2 Background Task Queue

**Problem:** Long-running tasks blokują response
**Rozwiązanie:** Celery lub RQ dla async tasks

```python
# /backend/app/tasks/worker.py

from celery import Celery

celery_app = Celery(
    "lifeai_tasks",
    broker="redis://redis:6379/1",
    backend="redis://redis:6379/2"
)

@celery_app.task
def generate_conversation_summary(conversation_id: str):
    """Background task: Generate summary after conversation ends."""
    conversation = db.get(Conversation, conversation_id)

    # Use LLM to summarize
    summary_prompt = f"Summarize this conversation in 2-3 sentences:\n\n"
    for msg in conversation.messages:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"

    summary = call_llm_sync([{"role": "user", "content": summary_prompt}])

    # Update conversation
    conversation.summary = summary
    db.commit()

@celery_app.task
def extract_topics(conversation_id: str):
    """Extract main topics from conversation."""
    # ...

@celery_app.task
def generate_insights(user_id: str):
    """Weekly insights generation."""
    # ...

# Usage in API
@router.post("/chat/end")
async def end_chat(session_id: str):
    # End session immediately
    conversation = await orchestrator.end_session(session_id)

    # Queue background tasks
    generate_conversation_summary.delay(conversation.id)
    extract_topics.delay(conversation.id)

    return {"status": "ended"}
```

#### 3.3 Horizontal Scaling Preparation

**Dodaj health checks:**

```python
# /backend/app/api/health.py

from fastapi import APIRouter, status
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}

@router.get("/health/detailed")
async def detailed_health():
    """Detailed health with dependencies."""
    checks = {
        "api": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "openai": await check_openai()
    }

    all_healthy = all(v == "healthy" for v in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks
    }

async def check_database():
    try:
        await db.execute("SELECT 1")
        return "healthy"
    except:
        return "unhealthy"
```

**Docker healthcheck:**

```dockerfile
# /backend/Dockerfile

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 4. SECURITY ENHANCEMENTS

#### 4.1 HTTPS Enforcement

```yaml
# docker-compose.yml

services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - backend

  backend:
    # Only exposed to nginx, not outside
    expose:
      - "8000"
```

```nginx
# nginx/nginx.conf

server {
    listen 80;
    server_name lifeai.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lifeai.example.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4.2 Input Validation & Sanitization

```python
# /backend/app/validators/message_validator.py

from pydantic import BaseModel, validator, Field
from typing import Optional

class MessageInput(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    modality: Optional[str] = Field(default="text")

    @validator('content')
    def sanitize_content(cls, v):
        """Remove potentially harmful content."""
        # Strip HTML tags
        import re
        v = re.sub(r'<[^>]+>', '', v)

        # Remove excessive whitespace
        v = ' '.join(v.split())

        # Check for injection attempts
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick='
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Invalid content detected")

        return v

    @validator('modality')
    def validate_modality(cls, v):
        """Ensure modality is valid."""
        allowed = ['text', 'voice', 'image']
        if v not in allowed:
            raise ValueError(f"Modality must be one of {allowed}")
        return v

# Usage
@router.post("/chat/message")
async def send_message(message: MessageInput, session_id: str):
    # message.content is already validated and sanitized
    # ...
```

#### 4.3 GDPR Compliance

**Right to Delete:**

```python
# /backend/app/api/gdpr.py

from fastapi import APIRouter, Depends
from app.security.auth import get_current_user

router = APIRouter(prefix="/gdpr", tags=["GDPR"])

@router.delete("/delete-my-data")
async def delete_user_data(current_user: User = Depends(get_current_user)):
    """
    Delete all user data (GDPR Right to Erasure).
    This is irreversible.
    """
    user_id = current_user.id

    # Delete conversations
    await db.execute(
        delete(Conversation).where(Conversation.user_id == user_id)
    )

    # Delete vector memories
    await vector_store.delete_by_user(user_id)

    # Delete feedbacks
    await db.execute(
        delete(Feedback).where(Feedback.user_id == user_id)
    )

    # Anonymize user record (keep for audit)
    current_user.email = f"deleted_{user_id}@anonymized.local"
    current_user.username = f"deleted_{user_id}"
    current_user.full_name = "Deleted User"
    current_user.is_active = False
    current_user.preferences = {}

    await db.commit()

    return {"message": "All your data has been deleted"}

@router.get("/export-my-data")
async def export_user_data(current_user: User = Depends(get_current_user)):
    """Export all user data (GDPR Right to Data Portability)."""
    user_id = current_user.id

    # Gather all data
    conversations = await db.execute(
        select(Conversation).where(Conversation.user_id == user_id)
    )

    export_data = {
        "user": {
            "email": current_user.email,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat(),
            "preferences": current_user.preferences
        },
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "messages": conv.messages,
                "created_at": conv.created_at.isoformat()
            }
            for conv in conversations.scalars()
        ],
        "statistics": {
            "total_conversations": len(conversations.scalars().all()),
            # ... more stats
        }
    }

    return export_data
```

**Consent Tracking:**

```python
# Add to User model
class User(Base):
    # ... existing fields

    consent_analytics: bool = Column(Boolean, default=False)
    consent_marketing: bool = Column(Boolean, default=False)
    consent_timestamp: datetime = Column(DateTime, nullable=True)
```

#### 4.4 API Key Rotation

```python
# /backend/app/security/api_keys.py

from datetime import datetime, timedelta

class APIKeyRotation:
    """Rotate OpenAI API keys for security."""

    def __init__(self, keys: List[str]):
        self.keys = keys
        self.current_index = 0
        self.last_rotation = datetime.utcnow()
        self.rotation_interval = timedelta(hours=24)

    def get_current_key(self) -> str:
        """Get current API key with auto-rotation."""
        if datetime.utcnow() - self.last_rotation > self.rotation_interval:
            self.rotate()

        return self.keys[self.current_index]

    def rotate(self):
        """Rotate to next key."""
        self.current_index = (self.current_index + 1) % len(self.keys)
        self.last_rotation = datetime.utcnow()

# Usage
api_keys = APIKeyRotation([
    os.getenv("OPENAI_API_KEY_1"),
    os.getenv("OPENAI_API_KEY_2"),
    os.getenv("OPENAI_API_KEY_3")
])

client = OpenAI(api_key=api_keys.get_current_key())
```

### 5. MONITORING & OBSERVABILITY

#### 5.1 Structured Logging

```python
# /backend/app/core/logging.py

import structlog
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()

# Usage
logger.info("message_processed",
    user_id=user_id,
    session_id=session_id,
    agent=agent_type,
    latency_ms=latency,
    tokens_used=tokens
)
```

#### 5.2 Prometheus Metrics

```python
# /backend/app/middleware/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter(
    'lifeai_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'lifeai_request_latency_seconds',
    'Request latency',
    ['endpoint']
)

LLM_CALLS = Counter(
    'lifeai_llm_calls_total',
    'Total LLM API calls',
    ['model', 'agent']
)

LLM_TOKENS = Counter(
    'lifeai_llm_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: prompt/completion
)

ACTIVE_SESSIONS = Gauge(
    'lifeai_active_sessions',
    'Number of active chat sessions'
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    latency = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        endpoint=request.url.path
    ).observe(latency)

    return response

# Expose metrics endpoint
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

#### 5.3 Error Tracking (Sentry)

```python
# /backend/app/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of requests for performance monitoring
    environment=os.getenv("ENVIRONMENT", "development"),
    release=f"lifeai@{VERSION}"
)

# Custom error context
from sentry_sdk import set_context

async def process_message(message: str, user_id: str):
    set_context("conversation", {
        "user_id": user_id,
        "message_length": len(message),
        "session_id": session_id
    })

    try:
        # ... process
    except Exception as e:
        # Sentry will automatically capture with context
        raise
```

### 6. TESTING INFRASTRUCTURE

#### 6.1 Comprehensive Test Suite

```python
# /backend/tests/test_chat.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_flow(async_client: AsyncClient, auth_headers):
    """Test complete chat flow."""

    # Start session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Send message
    response = await async_client.post(
        f"/chat/message",
        json={
            "session_id": session_id,
            "content": "Jak schudnąć 5kg?"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "reply" in response.json()

    # End session
    response = await async_client.post(
        f"/chat/end",
        params={"session_id": session_id},
        headers=auth_headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_multimodal_voice(async_client: AsyncClient, auth_headers):
    """Test voice input."""
    # ... test voice transcription
    pass

@pytest.mark.asyncio
async def test_rate_limiting(async_client: AsyncClient, auth_headers):
    """Test rate limits."""
    # Send 61 messages in 1 minute
    for i in range(61):
        response = await async_client.post(...)
        if i < 60:
            assert response.status_code == 200
        else:
            assert response.status_code == 429  # Rate limited
```

#### 6.2 Integration Tests

```python
# /backend/tests/integration/test_agents.py

@pytest.mark.integration
async def test_finance_agent():
    """Test finance agent with real LLM."""
    agent = FinanceAgent()

    context = Context(
        user_id="test_user",
        session_id="test_session",
        history=[],
        preferences={}
    )

    intent = Intent(
        intent_type=IntentType.FINANCE_QUERY,
        confidence=0.95,
        agent_types=[AgentType.FINANCE]
    )

    response = await agent.process(context, intent)

    assert response.content is not None
    assert len(response.content) > 0
    assert response.metadata["agent_type"] == "finance"
```

#### 6.3 Load Testing

```python
# /tests/load/locustfile.py

from locust import HttpUser, task, between

class LifeAIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before testing."""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Start session
        response = self.client.post("/chat/start", headers=self.headers)
        self.session_id = response.json()["session_id"]

    @task(3)
    def send_message(self):
        """Send chat message (most common action)."""
        self.client.post(
            "/chat/message",
            json={
                "session_id": self.session_id,
                "content": "Jak oszczędzać pieniądze?"
            },
            headers=self.headers
        )

    @task(1)
    def get_conversations(self):
        """Get conversation history."""
        self.client.get(
            "/chat/conversations",
            headers=self.headers
        )
```

**Run:** `locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10`

---

## 🧠 ULEPSZENIA ALGORYTMICZNE I AI

### 1. ADVANCED INTENT CLASSIFICATION

#### 1.1 Multi-Intent Detection

**Problem:** Obecny classifier zwraca 1 główną intencję
**Ulepszenie:** Wykrywanie wielu intencji w 1 wiadomości

```python
# /backend/app/core/intent_classifier.py

class EnhancedIntentClassifier:
    async def classify_multi_intent(self, message: str, context: Context) -> List[Intent]:
        """Classify multiple intents in a single message."""

        prompt = f"""Analyze this user message and identify ALL intents present.
A message may contain multiple intents.

Message: "{message}"

For each intent found, provide:
1. intent_type (health_query, finance_query, relationship_advice, etc.)
2. confidence (0.0-1.0)
3. specific_entities (extracted keywords)

Return as JSON array of intents, ordered by relevance.

Example:
[
  {{
    "intent_type": "health_query",
    "confidence": 0.9,
    "entities": {{"goal": "weight_loss", "amount": "5kg"}}
  }},
  {{
    "intent_type": "finance_query",
    "confidence": 0.85,
    "entities": {{"purpose": "gym_membership"}}
  }}
]
"""

        response = await call_llm([
            {"role": "system", "content": "You are an intent classification expert."},
            {"role": "user", "content": prompt}
        ], temperature=0.3, response_format={"type": "json_object"})

        intents_data = json.loads(response)

        return [
            Intent(
                intent_type=IntentType(intent["intent_type"]),
                confidence=intent["confidence"],
                entities=intent.get("entities", {}),
                agent_types=self._map_to_agents(intent["intent_type"])
            )
            for intent in intents_data
        ]
```

**Przykład:**
```
User: "Chcę schudnąć 5kg i zaoszczędzić na siłownię"

Intents:
[
  {
    "intent_type": "health_query",
    "confidence": 0.92,
    "entities": {"goal": "weight_loss", "amount": "5kg"},
    "agents": ["health"]
  },
  {
    "intent_type": "finance_query",
    "confidence": 0.88,
    "entities": {"purpose": "gym_membership"},
    "agents": ["finance"]
  }
]
```

#### 1.2 Context-Aware Classification

**Ulepszenie:** Użyj historii konwersacji dla lepszej klasyfikacji

```python
async def classify_with_context(
    self,
    message: str,
    context: Context
) -> Intent:
    """Classify with conversation history."""

    # Build context from last 3 messages
    conversation_context = ""
    for msg in context.history[-3:]:
        conversation_context += f"{msg.role}: {msg.content}\n"

    prompt = f"""Given this conversation context:

{conversation_context}

Current user message: "{message}"

Classify the intent considering the conversation flow.
If the message is a follow-up, maintain context continuity.

JSON response with intent_type, confidence, and entities."""

    # ... rest of classification
```

### 2. SMART AGENT ORCHESTRATION

#### 2.1 Agent Confidence Thresholds

**Problem:** Router wybiera agenta z highest confidence, nawet jeśli niska
**Ulepszenie:** Dynamic thresholds

```python
# /backend/app/core/router.py

class SmartAgentRouter:
    CONFIDENCE_THRESHOLDS = {
        "single_agent": 0.7,      # Min confidence dla 1 agenta
        "multi_agent": 0.5,       # Min dla każdego w multi-agent
        "fallback": 0.3           # Poniżej = general agent
    }

    async def route(self, intent: Intent, context: Context) -> OrchestratorResponse:
        """Smart routing with confidence thresholds."""

        # Get agent capabilities
        agent_scores = await self._score_agents(intent, context)

        # Filter by threshold
        top_agent = max(agent_scores, key=lambda x: x[1])

        if top_agent[1] >= self.CONFIDENCE_THRESHOLDS["single_agent"]:
            # High confidence - single agent
            return await self._single_agent_response(top_agent[0], intent, context)

        # Check if multi-agent makes sense
        capable_agents = [
            agent for agent, score in agent_scores
            if score >= self.CONFIDENCE_THRESHOLDS["multi_agent"]
        ]

        if len(capable_agents) >= 2:
            # Multi-agent collaboration
            return await self._multi_agent_response(capable_agents, intent, context)

        # Low confidence - use general agent
        return await self._fallback_response(intent, context)
```

#### 2.2 Agent Specialization Scoring

**Ulepszenie:** Bardziej sophisticated scoring dla agentów

```python
async def _score_agents(
    self,
    intent: Intent,
    context: Context
) -> List[Tuple[BaseAgent, float]]:
    """Score agents based on multiple factors."""

    scores = []

    for agent in self.agents:
        # Base score from can_handle
        base_score = await agent.can_handle(intent, context)

        # Boost if user has history with this agent
        history_boost = self._calculate_history_boost(agent, context)

        # Boost if recent messages were with this agent (conversation continuity)
        continuity_boost = self._calculate_continuity_boost(agent, context)

        # Penalize if agent recently failed
        failure_penalty = await self._calculate_failure_penalty(agent, context)

        final_score = (
            base_score * 0.5 +
            history_boost * 0.2 +
            continuity_boost * 0.2 -
            failure_penalty * 0.1
        )

        scores.append((agent, final_score))

    return sorted(scores, key=lambda x: x[1], reverse=True)

def _calculate_history_boost(self, agent: BaseAgent, context: Context) -> float:
    """Boost if user frequently uses this agent."""
    user_agent_usage = context.user_preferences.get("agent_usage", {})
    total_uses = sum(user_agent_usage.values())

    if total_uses == 0:
        return 0.0

    agent_uses = user_agent_usage.get(agent.agent_type.value, 0)
    return agent_uses / total_uses
```

### 3. MEMORY & PERSONALIZATION

#### 3.1 Long-Term Memory System

**Nowa funkcja:** Zapamiętywanie kluczowych faktów o użytkowniku

```python
# /backend/app/memory/long_term_memory.py

from typing import List, Dict
from datetime import datetime

class LongTermMemory:
    """Store and retrieve long-term user memories."""

    def __init__(self, vector_store, llm_client):
        self.vector_store = vector_store
        self.llm = llm_client

    async def extract_memories(self, conversation: Conversation) -> List[Memory]:
        """Extract memorable facts from conversation."""

        # Combine all messages
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation.messages
        ])

        prompt = f"""Extract important facts about the user from this conversation.
Focus on:
- Personal goals and aspirations
- Constraints and limitations
- Preferences and dislikes
- Important life events or context
- Recurring themes

Conversation:
{conversation_text}

Return JSON array of memories:
[
  {{
    "fact": "User wants to lose 5kg",
    "category": "health_goal",
    "confidence": 0.95,
    "context": "Mentioned in fitness discussion"
  }}
]
"""

        response = await self.llm.call([
            {"role": "system", "content": "You extract and categorize personal information."},
            {"role": "user", "content": prompt}
        ], response_format={"type": "json_object"})

        memories_data = json.loads(response)

        memories = []
        for mem in memories_data:
            memory = Memory(
                user_id=conversation.user_id,
                content=mem["fact"],
                category=mem["category"],
                confidence=mem["confidence"],
                context=mem["context"],
                timestamp=datetime.utcnow(),
                source_conversation_id=conversation.id
            )

            # Generate embedding
            memory.embedding = await self.llm.embed(memory.content)

            # Store in vector DB
            await self.vector_store.add(memory)

            memories.append(memory)

        return memories

    async def recall_relevant_memories(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> List[Memory]:
        """Retrieve relevant memories for current context."""

        # Generate query embedding
        query_embedding = await self.llm.embed(query)

        # Search vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            filter_dict={"user_id": user_id},
            top_k=top_k
        )

        return results
```

**Integracja z Orchestratorem:**

```python
async def process_message(self, message: str, session_id: str):
    """Process message with long-term memory."""

    # ... existing code

    # Recall relevant memories
    relevant_memories = await self.long_term_memory.recall_relevant_memories(
        query=message,
        user_id=context.user_id,
        top_k=3
    )

    # Add to context
    context.memories = relevant_memories

    # Agent can now use these memories
    response = await self.router.route(intent, context)

    return response
```

**Przykład użycia w agencie:**

```python
# Finance Agent
async def process(self, context: Context, intent: Intent):
    # Check memories
    budget_memory = next(
        (m for m in context.memories if m.category == "finance_budget"),
        None
    )

    if budget_memory:
        # Personalize response
        system_prompt += f"\n\nREMEMBER: {budget_memory.content}"

    # ... generate response
```

#### 3.2 User Preference Learning

**Nowa funkcja:** Uczenie się preferencji użytkownika

```python
# /backend/app/ml/preference_learner.py

from collections import defaultdict

class PreferenceLearner:
    """Learn user preferences from interactions."""

    async def analyze_user_behavior(self, user_id: str):
        """Analyze patterns in user conversations."""

        # Get all conversations
        conversations = await db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        patterns = {
            "preferred_agents": defaultdict(int),
            "common_topics": defaultdict(int),
            "response_length_preference": [],
            "interaction_times": [],
            "modality_preference": defaultdict(int)
        }

        for conv in conversations:
            # Agent preference
            for agent in conv.agents_used:
                patterns["preferred_agents"][agent] += 1

            # Topic extraction
            for topic in conv.main_topics:
                patterns["common_topics"][topic] += 1

            # Response length
            avg_length = sum(len(m["content"]) for m in conv.messages) / len(conv.messages)
            patterns["response_length_preference"].append(avg_length)

            # Interaction time
            patterns["interaction_times"].append(conv.created_at.hour)

            # Modality
            for msg in conv.messages:
                modality = msg.get("metadata", {}).get("modality", "text")
                patterns["modality_preference"][modality] += 1

        # Generate insights
        insights = {
            "top_agent": max(patterns["preferred_agents"].items(), key=lambda x: x[1])[0],
            "top_topics": sorted(patterns["common_topics"].items(), key=lambda x: x[1], reverse=True)[:5],
            "prefers_concise": sum(patterns["response_length_preference"]) / len(patterns["response_length_preference"]) < 200,
            "most_active_hour": max(set(patterns["interaction_times"]), key=patterns["interaction_times"].count),
            "preferred_modality": max(patterns["modality_preference"].items(), key=lambda x: x[1])[0]
        }

        # Update user preferences
        await self._update_user_preferences(user_id, insights)

        return insights
```

### 4. ADVANCED PROMPT ENGINEERING

#### 4.1 Dynamic Prompt Templates

**Problem:** Hardcoded prompty
**Ulepszenie:** Template system z personalizacją

```python
# /backend/app/prompts/template_engine.py

from jinja2 import Template

class PromptTemplateEngine:
    """Advanced prompt templating with personalization."""

    def __init__(self):
        self.templates = {
            "finance_advice": Template("""You are a personal finance assistant helping {{ user_name }}.

User Context:
{% if memories %}
What you know about {{ user_name }}:
{% for memory in memories %}
- {{ memory.content }}
{% endfor %}
{% endif %}

{% if user_preferences.prefers_concise %}
Keep your response concise and to-the-point.
{% else %}
Provide detailed explanations when relevant.
{% endif %}

User's question: {{ question }}

Provide actionable financial advice."""),

            "health_coaching": Template("""You are a health and wellness coach for {{ user_name }}.

{% if memories %}
Personal Health Context:
{% for memory in memories %}
- {{ memory.content }}
{% endfor %}
{% endif %}

Current Goal: {{ intent.entities.goal }}
{% if intent.entities.timeframe %}
Timeframe: {{ intent.entities.timeframe }}
{% endif %}

User's message: {{ message }}

Create a personalized {{ "concise" if user_preferences.prefers_concise else "comprehensive" }} health plan.""")
        }

    def render(
        self,
        template_name: str,
        user: User,
        context: Context,
        intent: Intent,
        message: str
    ) -> str:
        """Render personalized prompt."""

        template = self.templates[template_name]

        return template.render(
            user_name=user.full_name or user.username,
            memories=context.memories,
            user_preferences=user.preferences,
            intent=intent,
            message=message
        )
```

**Użycie:**

```python
# In agent
prompt = self.prompt_engine.render(
    "finance_advice",
    user=current_user,
    context=context,
    intent=intent,
    message=user_message
)

response = await call_llm([
    {"role": "system", "content": prompt}
])
```

#### 4.2 Few-Shot Learning for Agents

**Ulepszenie:** Dodaj examples do prompts dla lepszej jakości

```python
class AgentPromptBuilder:
    """Build prompts with few-shot examples."""

    FINANCE_EXAMPLES = [
        {
            "user": "Jak oszczędzać 1000 zł miesięcznie?",
            "assistant": """Oto konkretny plan oszczędności 1000 zł/miesiąc:

1. **Budżet 50/30/20**:
   - 50% na potrzeby (jedzenie, rachunki)
   - 30% na przyjemności
   - 20% na oszczędności (1000 zł)

2. **Automatyzacja**:
   - Zlecenie stałe w dniu wypłaty
   - Osobne konto oszczędnościowe

3. **Konkretne cięcia**:
   - Kawa na wynos: -200 zł
   - Lunche w pracy: -300 zł
   - Subskrypcje: -150 zł
   - Zakupy impulsywne: -350 zł

Czy chcesz szczegóły któregoś z punktów?"""
        },
        # More examples...
    ]

    def build_with_examples(self, user_message: str, agent_type: str) -> str:
        """Build prompt with relevant examples."""

        examples = self._get_examples_for_agent(agent_type)

        examples_text = "\n\n".join([
            f"Example {i+1}:\nUser: {ex['user']}\nAssistant: {ex['assistant']}"
            for i, ex in enumerate(examples)
        ])

        prompt = f"""Here are examples of high-quality responses:

{examples_text}

Now respond to this user message following the same style and quality:

User: {user_message}