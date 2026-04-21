# RogueTibia: Boss & Progresja v3.0 ⚔️🐍

Dynamiczna gra typu **Roguelike** stworzona w Pythonie z wykorzystaniem biblioteki **Pygame**. Projekt łączy klasyczną mechanikę poruszania się po siatce (grid-based) z systemem RPG, progresją trudności oraz epickimi starciami z bossami.

## 🌟 Kluczowe Funkcje
* **System Klas Bohaterów:** Wybór koloru determinuje klasę (Wojownik vs Zwiadowca), co wpływa na statystyki HP, Ataku i Uników (DEX).
* **Proceduralna Generacja Poziomów:** Każdy poziom jest generowany losowo, dbając o to, by start i wyjście zawsze były dostępne.
* **Zaawansowana Mechanika Walki:** * System uników oparty na statystyce DEX.
    * Skalowanie siły potworów wraz z "Poziomem Świata".
    * Efekt *Screen Shake* przy otrzymywaniu obrażeń zwiększający imersję.
* **System Progresji:** Zdobywanie punktów doświadczenia (EXP), awansowanie na kolejne poziomy (Level Up) i zwiększanie statystyk.
* **Starcia z Bossami:** Co 5 poziomów gracz musi zmierzyć się z potężniejszym przeciwnikiem o unikalnych statystykach.
* **Rozbudowane UI:** Czytelne paski HP i EXP, statystyki postaci oraz dynamiczny log zdarzeń informujący o przebiegu walki.

## 🛠️ Technologia
* **Język:** Python 3.x
* **Biblioteka:** Pygame 2.x
* **Paradygmat:** Programowanie obiektowe (OOP) – cała logika gry zamknięta w czystej strukturze klas.

## 🎮 Jak grać?
1. **Wybór postaci:** Po uruchomieniu wybierz kolor klawiszami `1-4`.
2. **Poruszanie się:** Używaj strzałek klawiatury.
3. **Walka:** Podejdź do czerwonego (potwór) lub fioletowego (boss) kwadratu, aby wyprowadzić atak.
4. **Cel:** Dotrzyj do zielonego wyjścia w rogu mapy, aby przejść do kolejnego świata.
5. **Śmierć:** Jeśli stracisz całe HP, naciśnij `R`, aby zresetować grę i spróbować pobić swój rekord (Score).

## 🔧 Instalacja i Uruchomienie
1. Sklonuj repozytorium.
2. Zainstaluj bibliotekę Pygame:
   ```bash
   pip install pygame
   
Uruchom grę:

Bash/Terminal:
python main.py