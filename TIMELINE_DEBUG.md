# Debugowanie problemu z Timeline

## Problem
Frontend pokazuje "Brak zapisanych rozmów" mimo że backend zwraca rozmowy (widoczne w logach: "Retrieved 3 conversations").

## Możliwe przyczyny
1. **Cache Next.js** - Volume `/app/.next` może zawierać stare zbudowane pliki
2. **Hot reload nie działa** - Zmiany w TypeScript interface mogą wymagać pełnego rebuildu

## Kroki naprawcze

### Opcja 1: Wyczyść cache i przebuduj (ZALECANE)
```powershell
# Zatrzymaj kontenery
docker compose down

# Usuń volume z cache Next.js
docker volume rm lifeai_frontend_next 2>$null

# Przebuduj frontend od zera
docker compose build --no-cache frontend

# Uruchom ponownie
docker compose up -d
```

### Opcja 2: Restart frontendu
```powershell
# Zrestartuj tylko frontend
docker compose restart frontend

# Sprawdź logi
docker compose logs -f frontend
```

### Opcja 3: Ręczne wyczyszczenie cache w kontenerze
```powershell
# Wejdź do kontenera
docker compose exec frontend sh

# Usuń cache Next.js
rm -rf /app/.next

# Wyjdź z kontenera
exit

# Zrestartuj frontend
docker compose restart frontend
```

## Weryfikacja naprawy

### 1. Sprawdź logi backendu
```powershell
docker compose logs backend | Select-String "timeline"
```

Powinno pokazywać:
```
Retrieved 3 conversations for user ...
Returning timeline data: 3 items
First item: id=..., title=..., messages=...
```

### 2. Sprawdź konsolę przeglądarki
1. Otwórz DevTools (F12)
2. Przejdź na zakładkę Console
3. Odśwież stronę Timeline (Ctrl+Shift+R - hard refresh)
4. Szukaj logów:
   ```
   Timeline API response: [...]
   Is array? true
   Data length: 3
   ```

### 3. Sprawdź Network tab
1. DevTools → Network
2. Odśwież Timeline
3. Znajdź request `GET /timeline/`
4. Sprawdź Response - powinno być:
   ```json
   [
     {
       "id": "...",
       "session_id": "...",
       "title": "Hsje...",
       "message_count": 2,
       "created_at": "2025-12-21T15:41:17...",
       ...
     },
     ...
   ]
   ```

## Jeśli nadal nie działa

### Sprawdź, czy frontend używa nowego kodu:
```powershell
# Zobacz timestamp pliku w kontenerze
docker compose exec frontend ls -la /app/app/timeline/page.tsx

# Porównaj z lokalnym
ls -la frontend/app/timeline/page.tsx
```

### Sprawdź błędy TypeScript:
```powershell
docker compose logs frontend | Select-String "error"
```

## Zmiany, które zostały wprowadzone

### Backend (`backend/app/api/timeline.py`)
- ✅ Dodano endpoint `GET /timeline/` z automatyczną autentykacją
- ✅ Zwraca tablicę bezpośrednio (nie `{timeline: []}`)
- ✅ Dodano szczegółowe logowanie

### Frontend (`frontend/app/timeline/page.tsx`)
- ✅ Zaktualizowano `TimelineItem` interface (dodano `id`, `title`, zmieniono `timestamp` → `created_at`)
- ✅ Poprawiono parsowanie: `data` zamiast `data.timeline`
- ✅ Dodano console.log dla debugowania
- ✅ Używamy `item.id` jako key zamiast indeksu tablicy

## Kontakt z API bezpośrednio

Możesz też przetestować API bezpośrednio:

```powershell
# Zaloguj się i pobierz token (zmień email/hasło)
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body (@{email="twoj@email.com"; password="twojehaslo"} | ConvertTo-Json) -ContentType "application/json"
$token = $response.access_token

# Pobierz timeline
$headers = @{Authorization = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/timeline/" -Headers $headers | ConvertTo-Json -Depth 10
```
