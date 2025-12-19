# 🪟 Windows Quick Start Guide

## Dla Użytkowników Windows

### Metoda 1: PowerShell Script (Zalecana) ⭐

```powershell
# W PowerShell (jako Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Następnie uruchom:
.\test-local.ps1
```

### Metoda 2: Docker Compose (Najprostsza) 🐳

```powershell
# 1. Upewnij się że Docker Desktop działa

# 2. Uruchom wszystko w Docker
docker-compose up -d

# 3. Sprawdź logi
docker-compose logs -f

# 4. Otwórz browser
start http://localhost:3000
start http://localhost:8000/docs
```

### Metoda 3: Git Bash (Jeśli masz Git)

```bash
# W Git Bash:
./test-local.sh
```

---

## Krok po Kroku (Dla Początkujących)

### 1. Zainstaluj Wymagane Narzędzia

**Docker Desktop:**
- Pobierz: https://www.docker.com/products/docker-desktop/
- Zainstaluj i uruchom
- Sprawdź: `docker --version`

**Python 3.11+:**
- Pobierz: https://www.python.org/downloads/
- ✅ Zaznacz "Add Python to PATH" podczas instalacji
- Sprawdź: `python --version`

**Node.js 18+:**
- Pobierz: https://nodejs.org/
- Zainstaluj LTS version
- Sprawdź: `node --version`

---

### 2. Przygotuj Projekt

```powershell
# Otwórz PowerShell w folderze projektu
cd C:\Users\Marksio\Documents\GitHub\LifeAI

# Sprawdź czy masz wszystkie pliki
dir
```

---

### 3. Skonfiguruj Environment Variables

```powershell
# Skopiuj plik .env
copy backend\.env.example backend\.env

# Edytuj w Notepad
notepad backend\.env
```

**W pliku backend\.env, zmień:**
```
OPENAI_API_KEY=sk-your-real-openai-api-key-here
```

Zapisz i zamknij Notepad.

---

### 4. Uruchom Docker Desktop

1. Otwórz Docker Desktop
2. Poczekaj aż się uruchomi (ikona wieloryba w tray)
3. Sprawdź czy działa: `docker ps`

---

### 5. Uruchom Testy

**Opcja A: Automatyczny Script**

```powershell
# Pozwól na uruchomienie scriptów (jednorazowo)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Uruchom testy
.\test-local.ps1
```

**Opcja B: Manualne Komendy**

```powershell
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head

# 3. Run tests
pytest -v

# 4. Start backend (w nowym oknie PowerShell)
uvicorn app.main:app --reload --port 8000

# 5. Frontend setup (w kolejnym oknie PowerShell)
cd ..\frontend
npm install

# 6. Start frontend
npm run dev
```

---

### 6. Otwórz w Przeglądarce

```powershell
# Frontend
start http://localhost:3000

# API Documentation
start http://localhost:8000/docs

# Health Check
start http://localhost:8000/health/
```

---

## Troubleshooting Windows

### Problem: "execution of scripts is disabled"

**Rozwiązanie:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Python not found"

**Rozwiązanie:**
1. Sprawdź czy Python jest zainstalowany: `python --version`
2. Jeśli nie, pobierz z https://www.python.org/downloads/
3. ✅ Zaznacz "Add Python to PATH"
4. Restart PowerShell

### Problem: "Docker daemon not running"

**Rozwiązanie:**
1. Otwórz Docker Desktop
2. Poczekaj aż ikona wieloryba w tray będzie zielona
3. Spróbuj: `docker ps`

### Problem: "Port 8000 already in use"

**Rozwiązanie:**
```powershell
# Znajdź proces
netstat -ano | findstr :8000

# Zabij proces (użyj PID z poprzedniej komendy)
taskkill /PID <PID> /F
```

### Problem: "npm ERR!"

**Rozwiązanie:**
```powershell
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

### Problem: "Database connection failed"

**Rozwiązanie:**
```powershell
# Restart PostgreSQL
docker-compose restart postgres

# Sprawdź logi
docker-compose logs postgres

# Sprawdź czy działa
docker-compose ps
```

---

## Szybkie Komendy Windows

### Start/Stop Services

```powershell
# Start wszystkiego
docker-compose up -d

# Stop wszystkiego
docker-compose down

# Restart konkretnego service
docker-compose restart postgres
docker-compose restart redis

# Zobacz logi
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Sprawdź Status

```powershell
# Docker containers
docker ps

# Backend status
curl http://localhost:8000/health/

# Database
docker exec -it lifeai-postgres psql -U lifeai
```

### Czyszczenie

```powershell
# Zatrzymaj wszystko
docker-compose down

# Usuń volumes (⚠️ usuwa dane!)
docker-compose down -v

# Wyczyść Python cache
cd backend
rm -r __pycache__
rm -r .pytest_cache

# Wyczyść Node modules
cd ..\frontend
rm -r node_modules
rm package-lock.json
```

---

## Visual Studio Code (Opcjonalnie)

Jeśli używasz VS Code:

1. **Zainstaluj Extensions:**
   - Python
   - Pylance
   - ESLint
   - Prettier
   - Docker

2. **Otwórz projekt:**
   ```powershell
   code .
   ```

3. **Terminal w VS Code:**
   - `Ctrl + ~` otwiera terminal
   - Możesz użyć PowerShell lub Git Bash

---

## Następne Kroki

Po pomyślnym uruchomieniu:

1. **Przetestuj features:**
   - Otwórz http://localhost:3000
   - Zarejestruj się
   - Wyślij wiadomość
   - Przetestuj voice/image

2. **Zobacz dokumentację:**
   - QUICK_TEST.md - Quick start guide
   - TESTING.md - Manual testing checklist
   - PRODUCTION.md - Production deployment

3. **Deploy to production:**
   - Zobacz PRODUCTION.md
   - Skonfiguruj Pinecone
   - Deploy na cloud

---

## Pomoc

Jeśli nadal masz problemy:

1. **Sprawdź Docker Desktop** - musi być uruchomiony
2. **Sprawdź .env file** - OPENAI_API_KEY musi być prawdziwy
3. **Sprawdź logi** - `docker-compose logs`
4. **Restart wszystkiego:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

---

## Skróty Klawiszowe

- `Ctrl + C` - Zatrzymaj aktualny proces
- `Ctrl + ~` - Otwórz terminal (VS Code)
- `Tab` - Auto-complete w PowerShell
- `↑` / `↓` - Historia komend

---

**Gotowy do testowania? Uruchom `.\test-local.ps1` i zobacz magię!** ✨
