# 🚀 Setup Guide - LifeAI Platform

## Wymagania wstępne

- Docker & Docker Compose
- Git
- Konto OpenAI z API key

## 1. Klonowanie repozytorium

```bash
git clone https://github.com/Marksio90/LifeAI.git
cd LifeAI
```

## 2. Konfiguracja zmiennych środowiskowych

### 2.1 Stwórz plik `.env`

```bash
cp .env.example .env
```

### 2.2 Edytuj plik `.env`

Otwórz plik `.env` i wypełnij wymagane wartości:

#### 🔴 WYMAGANE (musisz zmienić):

```env
# OpenAI API Key - pobierz z https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-twoj-prawdziwy-klucz-api

# Secret key dla JWT - wygeneruj silny klucz:
# openssl rand -hex 32
SECRET_KEY=wygeneruj-silny-losowy-klucz-64-znaki

# Hasło do PostgreSQL - zmień na silne hasło:
POSTGRES_PASSWORD=silne-haslo-do-bazy-danych

# Zaktualizuj DATABASE_URL z nowym hasłem:
DATABASE_URL=postgresql://lifeai:silne-haslo-do-bazy-danych@postgres:5432/lifeai
```

#### 🟡 OPCJONALNE (możesz zostawić domyślne):

```env
# Środowisko
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
POSTGRES_USER=lifeai
POSTGRES_DB=lifeai

# Redis
REDIS_URL=redis://redis:6379/0

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://frontend:3000

# Vector Database
VECTOR_DB_TYPE=in-memory
```

## 3. Uruchomienie platformy

### 3.1 Zbuduj i uruchom kontenery

```bash
docker compose up -d --build
```

### 3.2 Sprawdź status

```bash
docker compose ps
```

Wszystkie serwisy powinny mieć status `Up (healthy)`:
- `lifeai-postgres` - Baza danych
- `lifeai-redis` - Cache
- `lifeai-backend` - API (FastAPI)
- `lifeai-frontend` - UI (Next.js)

### 3.3 Sprawdź logi

```bash
# Wszystkie serwisy
docker compose logs -f

# Tylko backend
docker compose logs -f backend

# Tylko frontend
docker compose logs -f frontend
```

## 4. Dostęp do aplikacji

- **Frontend (UI)**: http://localhost:3000
- **Backend (API)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 5. Pierwsze uruchomienie

1. Otwórz przeglądarkę: http://localhost:3000
2. Kliknij **Zarejestruj się**
3. Wypełnij formularz:
   - Email
   - Hasło (min. 8 znaków, max 72 bajty)
   - Imię i nazwisko (opcjonalne)
4. Zaloguj się
5. Rozpocznij rozmowę z LifeAI!

## 6. Zatrzymanie i restart

### Zatrzymaj platformę
```bash
docker compose down
```

### Restart (bez rebuildu)
```bash
docker compose restart
```

### Restart z usunięciem danych
```bash
docker compose down -v  # UWAGA: usuwa wszystkie dane!
docker compose up -d --build
```

## 🔧 Rozwiązywanie problemów

### Problem: "OPENAI_API_KEY is required"

**Rozwiązanie**: Upewnij się, że plik `.env` istnieje i zawiera prawidłowy klucz:
```bash
cat .env | grep OPENAI_API_KEY
```

### Problem: Backend nie startuje

**Rozwiązanie**: Sprawdź logi backendu:
```bash
docker compose logs backend
```

Częste przyczyny:
- Błędny DATABASE_URL
- Błędny OPENAI_API_KEY
- PostgreSQL nie jest jeszcze gotowy (poczekaj 30s)

### Problem: Frontend pokazuje "Connection refused"

**Rozwiązanie**: 
1. Sprawdź czy backend działa: http://localhost:8000/health/live
2. Wyczyść cache Next.js:
   ```bash
   docker compose exec frontend rm -rf /app/.next
   docker compose restart frontend
   ```

### Problem: Błąd z hasłem przy rejestracji

**Rozwiązanie**: Hasło musi mieć:
- Minimum 8 znaków
- Maximum 72 bajty (UTF-8)

### Problem: Timeline nie pokazuje rozmów (Windows)

**Rozwiązanie**: 
1. Wyczyść cache przeglądarki (Ctrl+Shift+R)
2. Zrestartuj frontend:
   ```bash
   docker compose restart frontend
   ```
3. Zobacz TIMELINE_DEBUG.md dla szczegółów

## 📝 Dodatkowe informacje

### Windows - problem z line endings

Jeśli widzisz błąd `exec /app/entrypoint.sh: no such file or directory`:
1. Zobacz WINDOWS_SETUP.md
2. Upewnij się że Git używa LF (nie CRLF)

### Wersje produkcyjne

Dla środowiska produkcyjnego:
1. Zmień `ENVIRONMENT=production`
2. Wyłącz `DEBUG=false`
3. Zmień wszystkie hasła i klucze na silne, losowe wartości
4. Użyj HTTPS (reverse proxy: nginx, Traefik)
5. Skonfiguruj backupy bazy danych
6. Rozważ użycie Pinecone dla vector DB

### Koszty API OpenAI

LifeAI używa:
- **gpt-4o-mini** - główny model (~$0.15/1M tokens input, ~$0.60/1M tokens output)
- **text-embedding-3-small** - embeddings (~$0.02/1M tokens)
- **whisper-1** - transkrypcja audio (~$0.006/min)
- **tts-1** - synteza mowy (~$15.00/1M znaków)

Średni koszt rozmowy: **$0.01-0.05** (zależnie od długości)

### Limity rate

Domyślnie brak limitów. W produkcji dodaj rate limiting (zobacz TODO w roadmap).

## 🆘 Wsparcie

- Issues: https://github.com/Marksio90/LifeAI/issues
- Dokumentacja: README.md, TIMELINE_DEBUG.md, WINDOWS_SETUP.md
