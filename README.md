# BindMacro

Prosta aplikacja Windows z GUI (Tkinter) do auto-klikania przypisanym
klawiszem lub przyciskiem myszy w zadanym interwale.

## Uruchomienie

```
pip install -r requirements.txt
python main.py
```

## Uwagi

- Aplikacja jest przeznaczona dla Windows (buduje się jako `.exe` przez PyInstaller w CI).
- Biblioteki `keyboard`/`mouse` instalują globalne hooki systemowe — jeśli inna
  aplikacja na pulpicie działa z podniesionymi uprawnieniami (jako Administrator),
  BindMacro również musi być uruchomiony jako Administrator, żeby hotkey (`.`) i
  bindowanie klawiszy/przycisków myszy działały poprawnie.
- Podczas bindowania (`[ Click to bind ]`) naciśnij `Esc`, aby anulować.
- Ustawienia (bind, opóźnienie, hold) są zapisywane do `user_settings.json`
  obok plików źródłowych/exe i wczytywane przy kolejnym uruchomieniu.

## Testy

```
pip install -r requirements.txt
pytest tests/ -q
```
