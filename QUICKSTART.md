# 🚀 Quick Start Guide - LifeAI Multi-Agent Platform

Ten przewodnik pomoże Ci szybko uruchomić platformę LifeAI.

## Przygotowanie

### 1. Wymagania
Upewnij się, że masz zainstalowane:
- Docker & Docker Compose
- Git

### 2. Sklonuj repozytorium
```bash
git clone <repo-url>
cd LifeAI
```

### 3. Skonfiguruj OpenAI API Key

**WAŻNE:** Musisz mieć klucz API OpenAI

Edytuj `backend/.env`:
```bash
nano backend/.env
```

Zamień `sk-placeholder-key` na swój prawdziwy klucz OpenAI:
```
OPENAI_API_KEY=sk-twoj-prawdziwy-klucz-tutaj
```

## Uruchomienie

### Opcja 1: Docker Compose (Zalecane)

```bash
docker-compose up --build
```

Poczekaj aż wszystkie serwisy się uruchomią (może potrwać 1-2 minuty przy pierwszym uruchomieniu).

### Dostęp do aplikacji

Po uruchomieniu:
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

## Test Systemu

### 1. Sprawdź Health Check

```bash
curl http://localhost:8000/health
```

Oczekiwana odpowiedź:
```json
{
  "status": "ok",
  "version": "2.0.0"
}
```

### 2. Rozpocznij sesję czatu

```bash
curl -X POST http://localhost:8000/chat/start \
  -H "Content-Type: application/json" \
  -d '{"language": "pl"}'
```

Otrzymasz `session_id`.

### 3. Wyślij wiadomość (Finance Agent)

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TUTAJ_TWOJ_SESSION_ID",
    "message": "Jak mogę zaoszczędzić 1000 zł miesięcznie?"
  }'
```

### 4. Wyślij wiadomość (Health Agent)

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TUTAJ_TWOJ_SESSION_ID",
    "message": "Chcę zacząć biegać, jak się przygotować?"
  }'
```

### 5. Multi-Agent Query

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TUTAJ_TWOJ_SESSION_ID",
    "message": "Chcę schudnąć 5kg i zaoszczędzić na siłownię"
  }'
```

To zapytanie uruchomi współpracę **Health Agent** + **Finance Agent**!

### 6. Sprawdź statystyki

```bash
curl http://localhost:8000/chat/stats
```

## Interaktywna Dokumentacja API

Najłatwiejszy sposób na testowanie API:

1. Otwórz: http://localhost:8000/docs
2. Kliknij "Try it out" na dowolnym endpoincie
3. Wypełnij parametry
4. Kliknij "Execute"

## Przykładowe Zapytania dla Różnych Agentów

### General Agent
```
"Cześć, jak się masz?"
"Co potrafisz?"
```

### Finance Agent
```
"Jak zaplanować budżet domowy?"
"Jak oszczędzać na wakacje?"
"Pomóż mi zrozumieć kredyt hipoteczny"
```

### Health Agent
```
"Jak zacząć treningi siłowe?"
"Jaką dietę polecasz przy odchudzaniu?"
"Jak poprawić kondycję?"
```

### Relations Agent
```
"Jak poprawić komunikację z partnerem?"
"Jak radzić sobie ze stresem?"
"Jak rozwiązać konflikt w pracy?"
```

### Task Management Agent
```
"Pomóż mi zaplanować dzień"
"Jak być bardziej produktywnym?"
"Jak priorytyzować zadania?"
```

### Multi-Agent (używa wielu agentów)
```
"Chcę zacząć jogę i potrzebuję budżetu na zajęcia"
→ Health + Finance Agents

"Planuję zmianę kariery i martwię się o finanse"
→ Personal Development + Finance Agents

"Chcę poprawić relację i zarządzać czasem lepiej"
→ Relations + Task Management Agents
```

## Logowanie i Debugging

### Sprawdź logi backendu
```bash
docker-compose logs -f backend
```

Zobaczysz:
- Inicjalizację agentów
- Klasyfikację intencji
- Routing zapytań
- Odpowiedzi agentów

### Sprawdź logi wszystkich serwisów
```bash
docker-compose logs -f
```

## Zatrzymanie Aplikacji

```bash
docker-compose down
```

Aby również usunąć volumes (bazę danych):
```bash
docker-compose down -v
```

## Rozwiązywanie Problemów

### Problem: "Module not found"
```bash
docker-compose down
docker-compose up --build
```

### Problem: "Connection refused" do bazy danych
Poczekaj ~30 sekund aż PostgreSQL się uruchomi, następnie:
```bash
docker-compose restart backend
```

### Problem: Błędy OpenAI API
Sprawdź czy klucz API jest poprawny w `backend/.env`:
```bash
cat backend/.env | grep OPENAI_API_KEY
```

### Problem: Port 8000 zajęty
Zmień port w `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Zmienione z 8000:8000
```

## Dalsze Kroki

1. **Przeczytaj dokumentację**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Eksploruj API**: http://localhost:8000/docs
3. **Zobacz strukturę**: [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## Pomoc

Jeśli masz problemy:
1. Sprawdź logi: `docker-compose logs -f backend`
2. Sprawdź dokumentację: [README.md](./README.md)
3. Sprawdź health check: http://localhost:8000/health

---

**Miłego korzystania z LifeAI!** 🎉
