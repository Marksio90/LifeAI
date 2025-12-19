# 🧪 Quick Testing Guide

## Szybki Start (5 minut)

### 1. Przygotowanie

```bash
# Upewnij się, że masz OPENAI_API_KEY
# Edytuj backend/.env i dodaj swój klucz:
nano backend/.env
# OPENAI_API_KEY=sk-your-real-api-key-here
```

### 2. Uruchom Automatyczne Testy

```bash
# Uruchom kompletny test suite
./test-local.sh
```

To uruchomi:
- ✓ Sprawdzenie prerequisites (Python, Node, Docker)
- ✓ Instalację dependencies
- ✓ Start PostgreSQL i Redis
- ✓ Migracje bazy danych
- ✓ Backend tests (pytest)
- ✓ Frontend tests (jest)
- ✓ Start aplikacji
- ✓ Health checks
- ✓ API tests

### 3. Ręczne Testowanie

Po uruchomieniu `./test-local.sh`, otwórz:

**Frontend:**
```
http://localhost:3000
```

**API Documentation:**
```
http://localhost:8000/docs
```

**Health Check:**
```
curl http://localhost:8000/health/
```

### 4. Co Przetestować Ręcznie

Użyj checklisty w pliku `TESTING.md`:

```bash
# Zobacz pełną checklistę
cat TESTING.md
```

Kluczowe testy:
- [ ] Rejestracja użytkownika
- [ ] Login
- [ ] Wysłanie wiadomości tekstowej
- [ ] Nagranie głosowe (wymaga mikrofonu)
- [ ] Upload obrazu
- [ ] Text-to-speech (odtwarzanie odpowiedzi)
- [ ] Dark mode
- [ ] Timeline

### 5. Zatrzymanie Serwisów

```bash
# Zatrzymaj aplikację
kill $(cat .backend.pid)
kill $(cat .frontend.pid)

# Zatrzymaj infrastructure
docker-compose down
```

---

## Szybkie Testy API (bez UI)

### Test 1: Health Check
```bash
curl http://localhost:8000/health/
```

Oczekiwany wynik:
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "database": "connected"
}
```

### Test 2: Rejestracja
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

Oczekiwany wynik:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Test 3: Chat Session
```bash
# Start session
curl -X POST http://localhost:8000/chat/start

# Send message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Hello AI!"
  }'
```

---

## Troubleshooting

### Problem: "OPENAI_API_KEY is required"
**Rozwiązanie:** Dodaj prawdziwy klucz API w `backend/.env`

### Problem: "Database connection failed"
**Rozwiązanie:**
```bash
# Sprawdź czy PostgreSQL działa
docker-compose ps postgres

# Restart jeśli trzeba
docker-compose restart postgres
```

### Problem: "Port 8000 already in use"
**Rozwiązanie:**
```bash
# Znajdź proces
lsof -i :8000

# Zabij proces
kill -9 <PID>
```

### Problem: "npm install failed"
**Rozwiązanie:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Logi i Debugging

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# PostgreSQL logs
docker-compose logs -f postgres

# Redis logs
docker-compose logs -f redis

# Wszystkie logi
docker-compose logs -f
```

---

## Następne Kroki

Po pomyślnych testach lokalnych:

1. **Commit changes**
   ```bash
   git add .
   git commit -m "Testing complete - ready for production"
   ```

2. **Deploy to staging**
   ```bash
   # Użyj docker-compose.prod.yml
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Deploy to production**
   - Zobacz `PRODUCTION.md` dla pełnych instrukcji
   - Skonfiguruj Pinecone
   - Setup AWS Secrets Manager (opcjonalnie)
   - Deploy na Kubernetes

---

## Pomoc

Jeśli coś nie działa:
1. Sprawdź logi (`logs/` directory)
2. Verify .env configuration
3. Ensure all services are running (`docker-compose ps`)
4. Check API documentation (`http://localhost:8000/docs`)
5. Zobacz `DEPLOYMENT.md` i `PRODUCTION.md` dla więcej info
