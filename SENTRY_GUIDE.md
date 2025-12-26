# Sentry Error Tracking - Przewodnik Integracji

## 📊 Przegląd

Sentry to profesjonalna platforma do monitorowania błędów i śledzenia wydajności aplikacji. Integracja z LifeAI zapewnia:

- 🐛 Automatyczne wychwytywanie błędów i wyjątków
- 📈 Monitoring wydajności (performance traces)
- 👤 Śledzenie kontekstu użytkownika
- 🔍 Stack traces i debugging context
- 📊 Dashboard z metrykami i alertami
- 🔔 Powiadomienia o błędach (email, Slack, etc.)

---

## 🚀 Szybki Start

### 1. Utwórz Konto Sentry

1. Przejdź do [sentry.io](https://sentry.io/)
2. Zarejestruj się (darmowy plan wystarczy do startu)
3. Utwórz nowy projekt:
   - Platform: **Python / FastAPI**
   - Project name: **lifeai-backend**
4. Skopiuj **DSN** (Data Source Name) - będzie wyglądać jak:
   ```
   https://abc123def456@o123456.ingest.sentry.io/7890123
   ```

### 2. Konfiguracja Aplikacji

Dodaj DSN do pliku `.env`:

```bash
# .env
SENTRY_DSN=https://your-dsn-here@o123456.ingest.sentry.io/7890123
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

**Uwaga:** W produkcji zmniejsz sample rates do 0.1 (10%) aby zredukować koszty.

### 3. Weryfikacja Integracji

#### Test 1: Podstawowy Test

Uruchom aplikację i sprawdź logi:

```bash
cd backend
uvicorn app.main:app --reload
```

Powinieneś zobaczyć:
```
INFO - Sentry initialized successfully - Environment: development, Traces Sample Rate: 1.0
```

#### Test 2: Test Endpoint

Testuj error tracking przez API:

```bash
# Test message capture
curl http://localhost:8000/debug/sentry-message?message=Hello+Sentry&level=info

# Test exception capture (spowoduje błąd - to normalne!)
curl http://localhost:8000/debug/sentry-test

# Test user context
curl http://localhost:8000/debug/sentry-user-context?user_id=test123&email=test@example.com
```

#### Test 3: Sprawdź Sentry Dashboard

1. Zaloguj się do [sentry.io](https://sentry.io/)
2. Przejdź do projektu **lifeai-backend**
3. Sprawdź sekcję **Issues** - powinieneś zobaczyć:
   - Test message
   - ZeroDivisionError z `/debug/sentry-test`
   - User context event

---

## 🔧 Użycie w Kodzie

### Automatyczne Wychwytywanie Błędów

Sentry automatycznie wychwytuje wszystkie nieobsłużone wyjątki:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/risky-operation")
async def risky_operation():
    # Ten błąd zostanie automatycznie wysłany do Sentry
    result = 1 / 0  # ZeroDivisionError
    return {"result": result}
```

### Ręczne Wychwytywanie Błędów

```python
from app.monitoring.sentry import capture_exception

@router.post("/process-data")
async def process_data(data: dict):
    try:
        result = complex_operation(data)
        return {"status": "success", "result": result}
    except ValueError as e:
        # Wyślij błąd do Sentry z dodatkowym kontekstem
        event_id = capture_exception(e, context={
            "data_size": len(data),
            "operation": "complex_operation"
        })
        logger.error(f"Processing failed - Sentry event: {event_id}")
        raise HTTPException(status_code=400, detail=str(e))
```

### Wychwytywanie Wiadomości

```python
from app.monitoring.sentry import capture_message

@router.post("/important-action")
async def important_action(user_id: str):
    # Wyślij ważną informację do Sentry
    event_id = capture_message(
        f"User {user_id} performed important action",
        level="warning",
        context={"user_id": user_id, "timestamp": datetime.now()}
    )
    return {"status": "logged", "event_id": event_id}
```

### Śledzenie Kontekstu Użytkownika

```python
from app.monitoring.sentry import set_user_context, clear_user_context

# W middleware lub dependency
def get_current_user() -> User:
    user = authenticate_user()

    # Ustaw kontekst użytkownika dla wszystkich kolejnych eventów
    set_user_context(
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )

    return user

# Po wylogowaniu
@router.post("/logout")
async def logout():
    clear_user_context()
    return {"status": "logged out"}
```

### Breadcrumbs (Ślad Zdarzeń)

```python
from app.monitoring.sentry import add_breadcrumb

@router.post("/complex-workflow")
async def complex_workflow(data: dict):
    add_breadcrumb("Started workflow", category="workflow", data={"step": 1})

    step1_result = process_step1(data)
    add_breadcrumb("Step 1 completed", category="workflow", data={"result": step1_result})

    step2_result = process_step2(step1_result)
    add_breadcrumb("Step 2 completed", category="workflow", data={"result": step2_result})

    # Jeśli wystąpi błąd, Sentry pokaże cały trail breadcrumbs
    final_result = finalize(step2_result)

    return {"result": final_result}
```

---

## 🎯 Best Practices

### 1. Filtrowanie Danych Wrażliwych

Dane wrażliwe są automatycznie filtrowane w `before_send_filter`:

```python
# Automatycznie filtrowane pola:
- password
- token
- api_key
- secret
```

Możesz dodać więcej w `backend/app/monitoring/sentry.py`:

```python
def before_send_filter(event, hint):
    if 'request' in event and 'data' in event['request']:
        for key in ['password', 'token', 'api_key', 'ssn', 'credit_card']:
            if key in event['request']['data']:
                event['request']['data'][key] = '[FILTERED]'
    return event
```

### 2. Environment-Specific Configuration

**Development:**
```env
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0  # Track 100% transactions
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

**Staging:**
```env
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.5  # Track 50% transactions
SENTRY_PROFILES_SAMPLE_RATE=0.5
```

**Production:**
```env
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Track 10% transactions (cost-effective)
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

### 3. Ignorowanie Znanych Błędów

W `before_send_filter` możesz ignorować określone błędy:

```python
# Don't send HTTP 404 errors
if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
    return None

# Don't send keyboard interrupts
if isinstance(exc_value, (KeyboardInterrupt, SystemExit)):
    return None
```

### 4. Custom Tags

Dodawaj custom tags do eventów:

```python
import sentry_sdk

sentry_sdk.set_tag("agent_type", "health")
sentry_sdk.set_tag("conversation_id", conversation_id)
sentry_sdk.set_tag("feature", "voice_input")
```

---

## 📊 Monitoring Wydajności

### Performance Traces

Sentry automatycznie śledzi:
- **API endpoint latency** - czas odpowiedzi dla każdego endpointu
- **Database queries** - czas wykonania zapytań SQL
- **Redis operations** - czas operacji cache
- **External API calls** - czas wywołań OpenAI, Pinecone, etc.

### Custom Transactions

```python
import sentry_sdk

async def complex_ai_operation():
    with sentry_sdk.start_transaction(op="ai.processing", name="generate_response"):
        # LLM call
        with sentry_sdk.start_span(op="llm", description="OpenAI GPT-4"):
            response = await call_llm(messages)

        # Vector search
        with sentry_sdk.start_span(op="db", description="Vector search"):
            memories = await search_memories(query)

        return response
```

---

## 🔔 Alerty i Powiadomienia

### Konfiguracja Alertów w Sentry

1. Przejdź do **Alerts** w dashboardzie Sentry
2. Kliknij **Create Alert**
3. Wybierz typ:
   - **Issues:** Alert when new error appears
   - **Metric:** Alert on performance degradation
   - **Crash Free Rate:** Alert when error rate exceeds threshold

### Przykładowe Alerty

**Alert 1: New Error Type**
```
When: A new issue is first seen
Then: Send email to dev@example.com
```

**Alert 2: High Error Rate**
```
When: Error rate > 1% in 5 minutes
Then: Send Slack notification to #alerts
```

**Alert 3: Slow Endpoint**
```
When: P95 latency > 2s for /chat/message
Then: Create PagerDuty incident
```

### Integracje

Sentry obsługuje integracje z:
- ✅ Slack
- ✅ Email
- ✅ PagerDuty
- ✅ Jira
- ✅ GitHub Issues
- ✅ Discord
- ✅ Microsoft Teams

Konfiguracja: **Settings → Integrations**

---

## 🐛 Debugging z Sentry

### Analiza Błędu

Każdy event w Sentry zawiera:

1. **Exception Details**
   - Type: `ZeroDivisionError`
   - Message: `division by zero`
   - Stack trace z numerami linii

2. **Request Context**
   - URL: `/chat/message`
   - Method: `POST`
   - Headers
   - Body (z filtrowanymi hasłami)

3. **User Context**
   - User ID
   - Email
   - IP address (jeśli `send_default_pii=True`)

4. **Breadcrumbs**
   - Trail zdarzeń przed błędem
   - Database queries
   - HTTP requests
   - Logs (INFO, WARNING)

5. **Environment**
   - Python version
   - OS
   - Server info
   - Installed packages

### Source Maps

Sentry pokazuje dokładne linie kodu gdzie wystąpił błąd:

```python
File "/app/backend/app/agents/health/agent.py", line 42, in process
    result = calculate_bmi(height, weight)
File "/app/backend/app/agents/health/utils.py", line 15, in calculate_bmi
    return weight / (height ** 2)  # <- ERROR HERE
ZeroDivisionError: division by zero
```

---

## 💡 Przykłady Użycia

### Przykład 1: LLM Error Handling

```python
from app.monitoring.sentry import capture_exception, add_breadcrumb

async def generate_response(messages: list):
    add_breadcrumb("Starting LLM call", category="llm", data={"messages": len(messages)})

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        add_breadcrumb("LLM call successful", category="llm")
        return response.choices[0].message.content

    except openai.RateLimitError as e:
        capture_exception(e, context={
            "model": "gpt-4",
            "messages_count": len(messages),
            "error_type": "rate_limit"
        })
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    except openai.APIError as e:
        capture_exception(e, context={
            "model": "gpt-4",
            "error_type": "api_error"
        })
        raise HTTPException(status_code=500, detail="OpenAI API error")
```

### Przykład 2: Database Operations

```python
from app.monitoring.sentry import add_breadcrumb

async def save_conversation(user_id: str, messages: list):
    add_breadcrumb("Saving conversation", category="db", data={
        "user_id": user_id,
        "message_count": len(messages)
    })

    try:
        conversation = Conversation(user_id=user_id, messages=messages)
        db.add(conversation)
        await db.commit()

        add_breadcrumb("Conversation saved", category="db", data={
            "conversation_id": str(conversation.id)
        })

        return conversation
    except Exception as e:
        capture_exception(e, context={
            "user_id": user_id,
            "operation": "save_conversation"
        })
        raise
```

### Przykład 3: Background Tasks

```python
from celery import Task
from app.monitoring.sentry import capture_exception

class SentryTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        capture_exception(exc, context={
            "task_id": task_id,
            "task_name": self.name,
            "args": args,
            "kwargs": kwargs
        })

@celery_app.task(base=SentryTask)
def generate_weekly_report(user_id: str):
    # Task logic
    pass
```

---

## 📈 Metryki i Dashboard

### Kluczowe Metryki

W dashboardzie Sentry monitoruj:

1. **Error Rate** - % requestów z błędami
2. **Crash Free Rate** - % sesji bez błędów (target: >99%)
3. **Response Time** - P50, P75, P95, P99
4. **Throughput** - Requests per minute
5. **User Impact** - Liczba użytkowników dotkniętych błędami

### Custom Dashboards

Utwórz custom dashboard w Sentry:
- **Agents Performance:** Latency per agent type
- **LLM Errors:** OpenAI API failures
- **Database Performance:** Query times
- **Cache Hit Rate:** Redis performance

---

## 🔒 Bezpieczeństwo

### Dane Wrażliwe

**NIGDY** nie wysyłaj do Sentry:
- ❌ Hasła użytkowników
- ❌ API keys / tokens
- ❌ Numery kart kredytowych
- ❌ Dane osobowe (PESEL, SSN)

**Automatycznie filtrowane:**
- ✅ Password fields
- ✅ Token fields
- ✅ API key fields

### GDPR Compliance

Sentry jest zgodny z GDPR:
- Data residency: EU (wybierz EU region)
- Data retention: 90 dni (konfigurowalny)
- Right to erasure: API do usuwania danych użytkownika
- Privacy settings: `send_default_pii=False`

---

## 💰 Koszty

### Darmowy Plan (Free)
- ✅ 5,000 errors/month
- ✅ 10,000 performance transactions/month
- ✅ 1 user
- ✅ 30-day retention
- ✅ Wystarczające dla development

### Developer Plan ($26/month)
- ✅ 50,000 errors/month
- ✅ 100,000 performance transactions/month
- ✅ 5 users
- ✅ 90-day retention

### Team Plan ($80/month)
- ✅ 250,000 errors/month
- ✅ 500,000 performance transactions/month
- ✅ Unlimited users
- ✅ 90-day retention
- ✅ Advanced integrations

**Rekomendacja:** Start z Free, upgrade gdy przekroczysz limity.

---

## 🆘 Troubleshooting

### Sentry Nie Działa

**Problem:** `Sentry DSN not configured, skipping initialization`

**Rozwiązanie:**
```bash
# Sprawdź .env
echo $SENTRY_DSN

# Jeśli puste, dodaj:
echo "SENTRY_DSN=your-dsn-here" >> .env

# Restart aplikacji
```

**Problem:** Wydarzenia nie pojawiają się w Sentry

**Rozwiązanie:**
1. Sprawdź DSN - czy jest poprawny?
2. Sprawdź environment - czy pasuje do projektu?
3. Sprawdź firewall - czy aplikacja może łączyć się z sentry.io?
4. Test endpoint: `curl http://localhost:8000/debug/sentry-test`

**Problem:** Zbyt dużo eventów / przekroczony limit

**Rozwiązanie:**
```env
# Zmniejsz sample rates w .env
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10%
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Lub dodaj więcej filtrów w before_send_filter
```

---

## 📚 Dokumentacja

- **Sentry Docs:** https://docs.sentry.io/platforms/python/
- **FastAPI Integration:** https://docs.sentry.io/platforms/python/guides/fastapi/
- **Performance Monitoring:** https://docs.sentry.io/product/performance/
- **Best Practices:** https://docs.sentry.io/product/sentry-basics/guides/

---

## ✅ Checklist Produkcyjny

Przed wdrożeniem na produkcję:

- [ ] Sentry DSN skonfigurowany
- [ ] Environment ustawiony na "production"
- [ ] Sample rates zmniejszone (0.1 lub mniej)
- [ ] `send_default_pii=False` (GDPR compliance)
- [ ] Sensitive data filtering enabled
- [ ] Alerty skonfigurowane (email, Slack)
- [ ] Team members dodani do projektu
- [ ] Backup plan - co zrobić gdy Sentry down?
- [ ] Debug endpoints wyłączone (`/debug/*`)

---

**Status:** ✅ Gotowe do użycia
**Wersja:** 1.0
**Ostatnia aktualizacja:** 2025-12-26
