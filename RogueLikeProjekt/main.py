import pygame
import random
import math

# --- Ustawienia Gry ---
GRID_SIZE = 12
TILE_SIZE = 50
# Okno jest wyższe, aby zmieścić rozbudowane UI (statystyki i logi)
WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE + 200
FPS = 60

# --- Definicje Kolorów ---
BLACK = (10, 10, 10)
DARK_GRAY = (30, 30, 30)
WALL_COLOR = (70, 70, 80)
WHITE = (220, 220, 220)
RED = (200, 30, 30)
GREEN = (50, 200, 50)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0)
PURPLE = (160, 32, 240)  # Kolor Bossa


class Game:
    def __init__(self):
        pygame.init()
        # Ustawienie trybu wideo
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RogueTibia: Boss & Progresja v3.0")
        self.clock = pygame.time.Clock()

        # Czcionki - Segoe UI wygląda nowocześniej, ale Verdana jest bezpieczniejsza
        self.font_main = pygame.font.SysFont("Verdana", 22, bold=True)
        self.font_stats = pygame.font.SysFont("Verdana", 14)
        self.font_log = pygame.font.SysFont("Verdana", 13)

        # Stan gry
        self.state = "MENU_COLOR"  # Pierwszy ekran: wybór koloru
        self.player_color = BLUE  # Domyślny, zmieni się w menu
        self.shake_amount = 0  # Intensywność trzęsienia ekranu

        # Statystyki progresji świata
        self.world_level = 1
        self.total_score = 0

        # Statystyki gracza (Inicjalizacja domyślna)
        self.player_class = "Wojownik"
        self.player_hp_max = 150
        self.player_hp = self.player_hp_max
        self.player_atk = 20
        self.player_dex = 12  # Szansa na unik (%)
        self.player_exp = 0
        self.player_exp_next = 100
        self.player_lvl = 1

        # Logi walki
        self.log = ["Witaj w RogueTibia! Wybierz kolor bohatera."]

        # Pozycja startowa (zawsze [2, 2])
        self.player_pos = [2, 2]

    def add_log(self, text):
        self.log.append(text)
        if len(self.log) > 5:  # Trzymaj tylko 5 ostatnich logów
            self.log.pop(0)

    def reset_stats_for_class(self, p_class="Wojownik"):
        self.player_class = p_class
        if p_class == "Wojownik":
            self.player_hp_max = 150
            self.player_atk = 20
            self.player_dex = 12
        else:  # Zwiadowca
            self.player_hp_max = 90
            self.player_atk = 15
            self.player_dex = 30  # Dużo DEX dla uników

        self.player_hp = self.player_hp_max
        self.player_exp = 0
        self.player_exp_next = 100
        self.player_lvl = 1
        self.world_level = 1
        self.total_score = 0
        self.log = [f"Wybrano klasę {p_class}. Powodzenia!"]
        self.reset_level()

    def reset_level(self):
        # 1. MECHANIKA LECZENIA (ODZYSKIWANIE 20% BRAKUJĄCEGO HP)
        missing_hp = self.player_hp_max - self.player_hp
        if missing_hp > 0:
            heal_amount = int(missing_hp * 0.20)
            self.player_hp = min(self.player_hp_max, self.player_hp + heal_amount)
            self.add_log(f"Odzyskałeś {heal_amount} HP przy przejściu.")

        # 2. GENEROWANIE SIATKI MAPY
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.monsters = {}  # (x, y): {"hp": 50, "max_hp": 50, "atk": 5, "is_boss": False}

        # 3. GENEROWANIE ŚCIAN (GWARANTOWANY START I WYJŚCIE)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if random.random() < 0.18:  # 18% szans na ścianę
                    # Sprawdź, czy pole nie jest blisko startu ([2,2])
                    is_near_start = abs(x - 2) <= 1 and abs(y - 2) <= 1
                    # Sprawdź, czy pole nie jest blisko wyjścia (rogu)
                    is_near_exit = abs(x - (GRID_SIZE - 1)) <= 1 and abs(y - (GRID_SIZE - 1)) <= 1

                    if not is_near_start and not is_near_exit:
                        self.grid[y][x] = 4  # Postaw ścianę

        # 4. MECHANIKA BOSSA (CO 5 POZIOMÓW ŚWIATA)
        is_boss_level = self.world_level % 5 == 0
        if is_boss_level:
            # Boss spawnuje się w pobliżu wyjścia
            bx, by = GRID_SIZE - 2, GRID_SIZE - 2
            self.grid[by][bx] = 1  # Potwór
            m_hp = 250 + (self.world_level * 60)
            m_atk = 15 + (self.world_level * 3)
            self.monsters[(bx, by)] = {"hp": m_hp, "max_hp": m_hp, "atk": m_atk, "is_boss": True}
            self.add_log("!!! POZIOM BOSSA !!! Pokonaj fioletowego wroga!")
        else:
            # 5. GENEROWANIE ZWYKŁYCH POTWORÓW (SILNIEJSZE Z POZIOMEM)
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if (x, y) != (self.player_pos[0], self.player_pos[1]) and self.grid[y][x] == 0:
                        # Nie stawiaj potwora na wyjściu
                        if x != GRID_SIZE - 1 or y != GRID_SIZE - 1:
                            if random.random() < 0.10:  # 10% szans na potwora
                                self.grid[y][x] = 1
                                m_hp = 30 + (self.world_level * 15)
                                m_atk = 4 + (self.world_level * 2)
                                self.monsters[(x, y)] = {"hp": m_hp, "max_hp": m_hp, "atk": m_atk, "is_boss": False}

        # 6. USTAW WYJŚCIE (ZIELONA RAMKA)
        self.grid[GRID_SIZE - 1][GRID_SIZE - 1] = 3
        # Ustaw gracza na bezpiecznym polu startowym
        self.player_pos = [2, 2]

    def check_level_up(self):
        # Sprawdzanie i obsługa awansu na kolejny poziom doświadczenia
        if self.player_exp >= self.player_exp_next:
            self.player_lvl += 1
            self.player_exp -= self.player_exp_next
            # Zwiększ wymagania na kolejny level (skalowanie EXP)
            self.player_exp_next = int(self.player_exp_next * 1.4)
            # Zwiększ statystyki gracza
            self.player_hp_max += 25
            self.player_hp = self.player_hp_max  # Pełne leczenie przy Level Up
            self.player_atk += 7
            self.add_log(f"--- AWANS! POZIOM {self.player_lvl} ---")

    def move_player(self, dx, dy):
        if self.player_hp <= 0: return  # Gracz nie może się ruszać jeśli zginął

        nx, ny = self.player_pos[0] + dx, self.player_pos[1] + dy

        # Sprawdzenie granic mapy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            cell = self.grid[ny][nx]

            # Reakcja na pole
            if cell == 4:  # Ściana
                self.add_log("To jest solidna ściana.")
                return

            elif cell == 1:  # WALKA!
                m = self.monsters[(nx, ny)]

                # ATK GRACZA
                if random.randint(1, 100) > 5:  # Mała szansa na chybienie
                    dmg = random.randint(self.player_atk - 4, self.player_atk + 6)
                    m["hp"] -= dmg
                    # Możesz tu dodać self.hit_flash = True (Dla animacji w draw())

                    if m["hp"] <= 0:
                        # Przeciwnik pokonany
                        gained_exp = 100 if m["is_boss"] else 35
                        self.add_log(f"Zabiłeś {'BOSSA' if m['is_boss'] else 'potwora'}! +{gained_exp} EXP")
                        self.grid[ny][nx] = 0
                        del self.monsters[(nx, ny)]
                        self.player_exp += gained_exp
                        self.total_score += 150 if m["is_boss"] else 50
                        self.check_level_up()
                        return  # Nie wchodzimy na pole po walce, dopóki nie ruszymy się znów

                # KONTRATAK POTWORA (Jeśli przeżył)
                # Użyj DEX gracza jako szansy na UNIK
                if random.randint(1, 100) > self.player_dex:
                    m_damage = random.randint(m["atk"] - 1, m["atk"] + 3)
                    self.player_hp -= m_damage
                    self.shake_amount = 12  # Efekt trzęsienia przy trafieniu
                    self.add_log(f"Otrzymałeś {m_damage} obrażeń!")

                    # Sprawdzenie śmierci gracza
                    if self.player_hp <= 0:
                        self.add_log("Zginąłeś! Naciśnij R, by zagrać ponownie.")
                else:
                    self.add_log("Uniknąłeś ataku potwora!")
                    self.total_score += 10  # Punkty za unik

            elif cell == 3:  # WYJŚCIE
                self.add_log(f"Poziom Świata {self.world_level} ukończony!")
                self.world_level += 1
                self.reset_level()

            else:  # Puste pole - po prostu idź
                self.player_pos = [nx, ny]

    def draw_hp_bar(self, x, y, current, maximum, is_player=False):
        # Rysuje mały pasek HP nad kafelkiem
        width = 40
        height = 6
        # Wylicz pozycję paska na kafelku
        px = x * TILE_SIZE + (TILE_SIZE - width) // 2
        py = y * TILE_SIZE - 10

        # Tło (czarne)
        pygame.draw.rect(self.screen, (50, 0, 0), (px, py, width, height), border_radius=2)
        # Wypełnienie (proporcjonalne)
        fill_ratio = max(0, min(1, current / maximum))
        fill_width = int(fill_ratio * width)
        color = GREEN if is_player else RED
        pygame.draw.rect(self.screen, color, (px, py, fill_width, height), border_radius=2)

    def draw(self):
        # Obsługa SCREEN SHAKE (Trzęsienia)
        current_shake_x = random.randint(-self.shake_amount, self.shake_amount)
        current_shake_y = random.randint(-self.shake_amount, self.shake_amount)
        # Wygaszaj trzęsienie z klatki na klatkę
        if self.shake_amount > 0: self.shake_amount -= 1

        self.screen.fill(BLACK)

        # --- EKRAN MENU (WYBÓR KOLORU) ---
        if self.state == "MENU_COLOR":
            t = self.font_main.render("WYBIERZ KOLOR BOHATERA:", True, WHITE)
            self.screen.blit(t, (WIDTH // 2 - 160, 100))

            # Lista kolorów do wyboru
            color_options = [
                ("1. Niebieski (Classic)", BLUE, pygame.K_1),
                ("2. Zielony (TibiaStyle)", GREEN, pygame.K_2),
                ("3. Czerwony (Warior)", RED, pygame.K_3),
                ("4. Złoty (RichMan)", GOLD, pygame.K_4)
            ]

            for i, (name, color, key) in enumerate(color_options):
                txt = self.font_main.render(name, True, color)
                self.screen.blit(txt, (WIDTH // 2 - 120, 200 + i * 50))

            # Krótka pomoc na dole
            txt_help = self.font_stats.render("Użyj klawiszy numerycznych [1-4], aby wybrać.", True, WHITE)
            self.screen.blit(txt_help, (WIDTH // 2 - 140, HEIGHT - 50))

        # --- EKRAN GRY ---
        elif self.state == "GAME":
            # 1. RYSUJ MAPĘ (z offsetem shake)
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    rect = pygame.Rect(x * TILE_SIZE + current_shake_x, y * TILE_SIZE + current_shake_y, TILE_SIZE - 2,
                                       TILE_SIZE - 2)
                    cell = self.grid[y][x]

                    # Grunt
                    pygame.draw.rect(self.screen, DARK_GRAY, rect, border_radius=3)

                    if cell == 4:  # Ściana
                        pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=3)
                    elif cell == 1:  # Potwór/Boss
                        m = self.monsters[(x, y)]
                        m_col = PURPLE if m["is_boss"] else RED
                        m_rect = rect.inflate(-10 if m["is_boss"] else -20, -10 if m["is_boss"] else -20)
                        pygame.draw.rect(self.screen, m_col, m_rect, border_radius=6)
                        # Pasek HP potwora
                        self.draw_hp_bar(x, y, m["hp"], m["max_hp"], False)

                    elif cell == 3:  # Wyjście (Zielona ramka)
                        pygame.draw.rect(self.screen, GREEN, rect, 3, border_radius=3)

            # 2. RYSUJ GRACZA (NA WIERZCHU)
            px, py = self.player_pos
            p_rect = pygame.Rect(px * TILE_SIZE + 7 + current_shake_x, py * TILE_SIZE + 7 + current_shake_y,
                                 TILE_SIZE - 14, TILE_SIZE - 14)
            pygame.draw.rect(self.screen, self.player_color, p_rect, border_radius=5)
            # Pasek HP Gracza
            self.draw_hp_bar(px, py, self.player_hp, self.player_hp_max, True)

            # 3. INTERFEJS UŻYTKOWNIKA (UI) NA DOLE
            ui_y = GRID_SIZE * TILE_SIZE + 10
            # Tło UI
            pygame.draw.rect(self.screen, (20, 20, 20), (10, ui_y, WIDTH - 20, 180), border_radius=10)

            # --- Paski UI (HP i EXP) ---
            # Pasek Zdrowia (Duży)
            hp_w_full = WIDTH - 40
            hp_ratio = max(0, min(1, self.player_hp / self.player_hp_max))
            pygame.draw.rect(self.screen, (80, 0, 0), (20, ui_y + 15, hp_w_full, 16), border_radius=5)
            pygame.draw.rect(self.screen, GREEN, (20, ui_y + 15, int(hp_w_full * hp_ratio), 16), border_radius=5)
            # Napis HP wewnątrz paska
            txt_hp_vals = self.font_stats.render(f"{self.player_hp} / {self.player_hp_max} HP", True, WHITE)
            self.screen.blit(txt_hp_vals, (WIDTH // 2 - 40, ui_y + 14))

            # Pasek EXP (Mały, złoty)
            exp_ratio = max(0, min(1, self.player_exp / self.player_exp_next))
            pygame.draw.rect(self.screen, (30, 30, 30), (20, ui_y + 38, hp_w_full, 8), border_radius=4)
            pygame.draw.rect(self.screen, GOLD, (20, ui_y + 38, int(hp_w_full * exp_ratio), 8), border_radius=4)

            # --- Statystyki ---
            txt_world = self.font_main.render(f"POZIOM ŚWIATA: {self.world_level}", True, GOLD)
            self.screen.blit(txt_world, (25, ui_y + 55))

            txt_chars = self.font_stats.render(
                f"BOHATER LVL: {self.player_lvl} | ATK: {self.player_atk} | DEX: {self.player_dex}% | SCORE: {self.total_score}",
                True, WHITE)
            self.screen.blit(txt_chars, (25, ui_y + 85))

            # --- Logi Walki ---
            for i, entry in enumerate(self.log):
                # Koloruj logi w zależności od treści
                log_color = (180, 180, 180)  # Domyślny gray
                if "AWANS" in entry:
                    log_color = GOLD
                elif "Otrzymałeś" in entry:
                    log_color = RED
                elif "Zabiłeś" in entry:
                    log_color = GREEN
                elif "Zginąłeś" in entry:
                    log_color = (255, 0, 0)
                elif "BOSSA" in entry:
                    log_color = PURPLE

                txt_entry = self.font_log.render(entry, True, log_color)
                self.screen.blit(txt_entry, (25, ui_y + 110 + i * 16))

            # --- Ekran Śmierci ---
            if self.player_hp <= 0:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(220)  # Półprzezroczysty
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                over_txt = self.font_main.render("GAME OVER", True, RED)
                restart_txt = self.font_main.render("Naciśnij [R], by zagrać ponownie", True, WHITE)
                score_txt = self.font_main.render(f"Twoje Punkty: {self.total_score}", True, GOLD)

                self.screen.blit(over_txt, (WIDTH // 2 - 70, HEIGHT // 2 - 60))
                self.screen.blit(restart_txt, (WIDTH // 2 - 160, HEIGHT // 2))
                self.screen.blit(score_txt, (WIDTH // 2 - 90, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            # OBSŁUGA ZDARZEŃ (Wejście użytkownika)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # --- Mechanika Menu ---
                    if self.state == "MENU_COLOR":
                        if event.key == pygame.K_1: self.player_color = BLUE; self.state = "GAME"; self.reset_stats_for_class(
                            "Wojownik")
                        if event.key == pygame.K_2: self.player_color = GREEN; self.state = "GAME"; self.reset_stats_for_class(
                            "Zwiadowca")
                        if event.key == pygame.K_3: self.player_color = RED; self.state = "GAME"; self.reset_stats_for_class(
                            "Wojownik")
                        if event.key == pygame.K_4: self.player_color = GOLD; self.state = "GAME"; self.reset_stats_for_class(
                            "Zwiadowca")

                        if self.state == "GAME":  # Jeśli kolor został wybrany
                            # Tutaj możemy przypisać statystyki bazowe raz na start
                            pass

                    # --- Mechanika Gry ---
                    elif self.state == "GAME":
                        if self.player_hp > 0:  # Możesz się ruszać tylko żywym
                            if event.key == pygame.K_UP: self.move_player(0, -1)
                            if event.key == pygame.K_DOWN: self.move_player(0, 1)
                            if event.key == pygame.K_LEFT: self.move_player(-1, 0)
                            if event.key == pygame.K_RIGHT: self.move_player(1, 0)

                        # Restart po śmierci
                        if self.player_hp <= 0 and event.key == pygame.K_r:
                            self.state = "MENU_COLOR"
                            self.shake_amount = 0

            # RYSOWANIE KWIATKI
            self.draw()

            # Ograniczenie liczby klatek na sekundę
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    Game().run()