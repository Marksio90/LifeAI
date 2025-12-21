# Windows Setup Guide

## Problem z Line Endings

Jeśli napotkasz błąd:
```
exec /app/entrypoint.sh: no such file or directory
```

To oznacza problem z zakończeniami linii (CRLF vs LF).

## Rozwiązanie

### Opcja 1: Konfiguracja Git (Zalecana)

```bash
# Skonfiguruj Git, aby automatycznie konwertować line endings
git config --global core.autocrlf input

# Odśwież repozytorium
git rm --cached -r .
git reset --hard
```

### Opcja 2: Manualna Konwersja

Jeśli masz zainstalowane WSL lub Git Bash:

```bash
# Konwertuj entrypoint.sh do LF
sed -i 's/\r$//' backend/entrypoint.sh
chmod +x backend/entrypoint.sh
```

### Opcja 3: Użyj .gitattributes

Plik `.gitattributes` został już dodany do repozytorium i automatycznie zarządza zakończeniami linii:
- `.sh` pliki zawsze używają LF
- `.py` pliki zawsze używają LF

Po wykonaniu którejkolwiek z powyższych opcji, uruchom ponownie:

```bash
docker-compose down
docker-compose up --build
```

## Weryfikacja

Po uruchomieniu powinieneś zobaczyć:

```
lifeai-backend  | Waiting for PostgreSQL to be ready...
lifeai-backend  | PostgreSQL is up - running migrations...
lifeai-backend  | Starting application...
```

## Dodatkowe Wskazówki

1. **Używaj edytora, który wspiera LF**: VSCode, Notepad++, Sublime Text
2. **Konfiguracja VSCode**:
   - Otwórz Settings (Ctrl+,)
   - Wyszukaj "End of Line"
   - Ustaw na "\n" (LF)
3. **Git for Windows**: Podczas instalacji wybierz "Checkout as-is, commit Unix-style line endings"
