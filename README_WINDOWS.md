# Instrukcja budowania aplikacji na Windows

## Wymagania

1. Windows 10 lub nowszy
2. Python 3.8 lub nowszy (64-bit)
3. Git (opcjonalnie)

## Kroki instalacji

### 1. Przygotowanie środowiska

1. Pobierz i zainstaluj Python ze strony https://www.python.org/downloads/windows/
   - Podczas instalacji zaznacz opcję "Add Python to PATH"
2. Otwórz PowerShell lub Command Prompt jako administrator

3. Stwórz i aktywuj wirtualne środowisko:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Instalacja zależności

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

### 3. Budowanie aplikacji

1. Upewnij się, że plik `logo.png` znajduje się w tym samym folderze co skrypt

2. Uruchom PyInstaller z plikiem specyfikacji dla Windows:

```powershell
pyinstaller cutting_optimizer_windows.spec
```

3. Po zakończeniu procesu, w folderze `dist` znajdziesz plik wykonywalny `AMIR Cutting Optimizer.exe`

## Rozwiązywanie problemów

### Brak modułów

Jeśli podczas budowania pojawią się błędy o brakujących modułach, dodaj je do listy `hiddenimports` w pliku `cutting_optimizer_windows.spec`.

### Problemy z UPX

Jeśli pojawią się błędy związane z UPX, możesz wyłączyć kompresję UPX zmieniając `upx=True` na `upx=False` w pliku specyfikacji.

### Antywirus

Niektóre programy antywirusowe mogą blokować proces budowania. W takim przypadku może być konieczne tymczasowe wyłączenie ochrony antywirusowej.

## Dystrybucja

Po zbudowaniu aplikacji, możesz dystrybuować plik `AMIR Cutting Optimizer.exe` z folderu `dist`. Użytkownicy nie będą potrzebowali zainstalowanego Pythona ani żadnych dodatkowych bibliotek.
