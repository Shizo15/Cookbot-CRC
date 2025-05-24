# 🍳🤖 CookBot - Discord Bot

CookBot to bot na Discordzie, który integruje się z zewnętrznym API `Spoonacular`, aby dostarczać użytkownikom spersonalizowane informacje dotyczące ulubionych przepisów lub inne dane z nimi związane. Dodatkowo bot umożliwia dodawanie obrazków do ulubionych oraz zarządzanie nimi poprzez reakcje. Projekt jest napisany w Pythonie i konteneryzowany w Dockerze.  

---

## Spis treści

- [Funkcjonalności](#-funkcjonalności)  
- [Struktura projektu](#-struktura-projektu)  
- [Wymagania](#-wymagania)  
- [Instalacja i uruchomienie lokalne](#-instalacja-i-uruchomienie-lokalne)  
- [Testy](#-testy)  
- [Docker](#-docker)
- [CI/CD](#-cicd---azure-pipelines)  
- [Wdrożenie](#-wdrożenie)  
- [Podsumowanie](#-podsumowanie)

---


## ✨ Funkcjonalności

- `!recipe <nazwa>` –  
🔍 Wyszukuje przepis po nazwie i wyświetla losowy pasujący wynik.  

    **Przykład:** `!recipe pasta`

- `!meal <typ posiłku> [liczba]` –  
🍽️ Wyszukuje losowe przepisy według typu posiłku (np. śniadanie, danie główne). Opcjonalnie można podać liczbę (1–5).  

    **Przykład:** `!meal breakfast 2`

    **Dostępne typy posiłków:**  
    `maincourse`, `sidedish`, `dessert`, `appetizer`, `salad`, `bread`, `breakfast`, `soup`,  
    `beverage`, `sauce`, `marinade`, `fingerfood`, `snack`, `drink`

- `!cuisine <typ kuchni> [liczba]` –  
🌍 Wyszukuje przepisy z wybranej kuchni. Opcjonalnie można podać liczbę (1–5).  

    **Przykład:** `!cuisine italian 3`

    **Dostępne kuchnie:**  
    `african`, `asian`, `american`, `british`, `cajun`, `caribbean`, `chinese`, `easterneuropean`, `european`, `french`,  
    `german`, `greek`, `indian`, `irish`, `italian`, `japanese`, `jewish`, `korean`, `latinamerican`,  
    `mediterranean`, `mexican`, `middleeastern`, `nordic`, `southern`, `spanish`, `thai`, `vietnamese`

- `!ingredients <składnik1,składnik2,...> [liczba]` –  
🧂 Wyszukuje przepisy na podstawie podanych składników.  

    **Przykład:** `!ingredients tomato,cheese 2`

- `!random [1-5]` –  
🎲 Wyświetla od 1 do 5 losowych przepisów.  

    **Przykład:** `!random 3`

- `!favorites` –  
❤️ Pokazuje listę ulubionych przepisów dodanych za pomocą reakcji „serduszko”.

- `!helpme` –  
❓ Wyświetla pomoc i listę dostępnych komend.

- ❤️ Reakcja – Dodaj lub usuń przepis z ulubionych, klikając ikonę serca pod wiadomością z przepisem.

---

## 🗂️ Struktura projektu

```bash
Cookbot/
├── src/
│   ├── main.py                  # Główny punkt wejścia aplikacji
│   ├── commands/                # Komendy bota
│   │   ├── cuisine.py
│   │   ├── helpme.py
│   │   ├── ingredients.py
│   │   ├── meal.py
│   │   ├── random.py
│   │   └── recipe.py
│   └── utils/                   # Narzędzia wspomagające (np. czyszczenie HTML)
│       ├── HTMLCleaner.py
│       └── isHTML.py
├── requirements.txt            # Lista zależności
├── requirements-dev.txt        # Zależności developerskie
├── Dockerfile                  # Konfiguracja Dockera
├── .gitignore
├── .dockerignore
├── azure-pipelines.yml         # Konfiguracja CI/CD (Azure)
└── README.md                   # Dokumentacja projektu
```

---

## 📦 Wymagania

- `Python 3.12+`  
- `discord.py` - logika bota
- `requests` - obsługa zapytań
- `dotenv` - zmienne środowiskowe
- `pytest`, `pytest-asyncio`, `ruff` - testy i linting

---

## 💻 Instalacja i uruchomienie lokalne

1. Sklonuj repozytorium:  
   ```bash
   git clone https://twoje-repozytorium.git
   cd twoje-repozytorium
   ```
2. Utwórz i aktywuj wirtualne środowisko:
    ```bash
   python3 -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```
3. Zainstaluj potrzebne biblioteki:
    ```bash
    pip install -r requirements.txt
    ```
4. Utwórz plik `.env` z wymaganymi sekretami:
    ```text
    DISCORD_TOKEN=twój_token_discord
    API_TOKEN=twój_token_api
    ```
5. Uruchom bota lokalnie:
    ```bash
    python src/main.py
    ```

## ✅ Testy
Projekt zawiera zestaw testów jednostkowych dla każdej z głównych funkcjonalności bota, zlokalizowanych w katalogu `tests/`. Testy obejmują m.in.:

- `test_cuisine.py` – testy komendy wyboru kuchni świata

- `test_helpme.py` – testy systemu pomocy

- `test_ingredients.py` – sprawdzanie poprawności działania przetwarzania składników

- `test_main.py` – testy dla punktu wejścia aplikacji

- `test_meal.py` – testowanie funkcji doboru posiłków

- `test_random.py` – testowanie losowego doboru przepisów

- `test_recipe.py` – weryfikacja pobierania i parsowania przepisów

- `test_sender.py` – testy wysyłania wiadomości lub interfejsu komunikacyjnego

Uruchom testy jednostkowe i linter:
```bash
pip install -r requirements-dev.txt
pytest tests --cov=src
ruff check src
```

## 🐳 Docker
Projekt można uruchomić w kontenerze Docker, co upraszcza instalację zależności i wdrażanie w środowiskach produkcyjnych.

#### Struktura

Plik `Dockerfile` znajduje się w folderze src/ i zawiera instrukcje budowania obrazu aplikacji.

```dockerfile
# Użycie lekkiego obrazu Pythona 3.13 jako bazy
FROM python:3.13-slim

# Informacja o autorze obrazu
LABEL authors="Shizo15"

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Skopiowanie pliku z zależnościami i instalacja pakietów
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Skopiowanie całego kodu źródłowego do kontenera
COPY . .

# Ustawienie ścieżki dla modułów Pythona
ENV PYTHONPATH=/app

# Komenda uruchamiająca bota po starcie kontenera
CMD ["python", "src/main.py"]
```
#### Budowanie obrazu
```bash
docker build --no-cache -f src/Dockerfile -t NAZWA .   
```

#### Uruchamianie kontenera
```bash
docker run --env-file .env NAZWA    
```

## 🔁 CI/CD - Azure Pipelines
Projekt posiada pipeline Azure DevOps, który:

* Uruchamia testy i linter
* Buduje obraz Docker i wypycha go do Docker Hub
* Wdraża obraz na wskazanym agencie (VM) z wyborem akcji: install, uninstall, reinstall
* Sekrety przechowywane grupie zmiennych Azure DevOps

## 🚀 Wdrożenie
* Pipeline jest uruchamiany automatycznie po pushu na gałąź main.
* Docker image jest wdrażany na wskazanym serwerze poprzez docker run z odpowiednimi zmiennymi środowiskowymi.
* Możliwa jest rozbudowa o wdrożenie do Kubernetes lub innych usług chmurowych.

## 🎉 Podsumowanie
CookBot to prosty, ale funkcjonalny bot na Discorda, który pomaga znaleźć inspiracje kulinarne i zarządzać ulubionymi przepisami w wygodny sposób. Zapraszam do korzystania, testowania i rozwijania projektu!

## 🤝 Współpraca
Jeśli masz pomysł na nowe funkcjonalności lub znalazłeś błąd — zapraszam do zgłaszania issue lub wysyłania pull requestów. Każda pomoc jest mile widziana!

