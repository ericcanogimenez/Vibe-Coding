"""
Mini Street Fighter - GOTY Edition
Juego de lucha 1v1 con personajes únicos, especiales, supers, rondas, IA avanzada
"""

import pygame
import sys
import random
import math
from enum import Enum

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ── Pantalla ──────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Street Fighter")
clock = pygame.time.Clock()

# ── Colores ───────────────────────────────────────────────────────────────
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
RED          = (220, 40, 40)
GREEN        = (40, 200, 80)
BLUE         = (40, 100, 220)
YELLOW       = (255, 210, 0)
ORANGE       = (255, 140, 0)
PURPLE       = (150, 50, 220)
CYAN         = (0, 200, 220)
DARK_BG      = (15, 10, 25)
GOLD         = (255, 195, 0)
FLOOR_COLOR  = (80, 60, 40)
FLOOR_LINE   = (120, 90, 60)
PINK         = (255, 80, 160)
LIME         = (100, 255, 60)

# ── Personajes definidos ──────────────────────────────────────────────────
CHARACTERS = {
    "RYU": {
        "display": "RYU",
        "color": (70, 130, 255),
        "dark": (30, 70, 160),
        "accent": CYAN,
        "special_color": (80, 160, 255),
        "super_color": (150, 220, 255),
        "hp": 180,
        "speed": 5.0,
        "punch_dmg": 18,
        "kick_dmg": 26,
        "special_dmg": 40,
        "super_dmg": 80,
        "jump_power": 17,
        "special_name": "HADOUKEN",
        "super_name": "SHORYUKEN",
        "desc": "Guerrero equilibrado",
    },
    "KEN": {
        "display": "KEN",
        "color": (255, 80, 40),
        "dark": (160, 30, 10),
        "accent": ORANGE,
        "special_color": (255, 140, 60),
        "super_color": (255, 220, 60),
        "hp": 160,
        "speed": 6.0,
        "punch_dmg": 22,
        "kick_dmg": 28,
        "special_dmg": 45,
        "super_dmg": 90,
        "jump_power": 18,
        "special_name": "HADOUKEN",
        "super_name": "DRAGON PUNCH",
        "desc": "Rápido y explosivo",
    },
    "CHUN": {
        "display": "CHUN-LI",
        "color": (100, 200, 255),
        "dark": (40, 100, 180),
        "accent": YELLOW,
        "special_color": (150, 230, 255),
        "super_color": (255, 255, 80),
        "hp": 150,
        "speed": 7.0,
        "punch_dmg": 15,
        "kick_dmg": 32,
        "special_dmg": 38,
        "super_dmg": 75,
        "jump_power": 20,
        "special_name": "KIKOKEN",
        "super_name": "SPINNING BIRD",
        "desc": "Velocidad máxima",
    },
    "ZANGIEF": {
        "display": "ZANGIEF",
        "color": (180, 60, 60),
        "dark": (100, 20, 20),
        "accent": RED,
        "special_color": (220, 80, 80),
        "super_color": (255, 120, 60),
        "hp": 220,
        "speed": 4.0,
        "punch_dmg": 28,
        "kick_dmg": 38,
        "special_dmg": 55,
        "super_dmg": 100,
        "jump_power": 14,
        "special_name": "SPINNING LARIAT",
        "super_name": "FINAL ATOMIC",
        "desc": "Tanque destructor",
    },
}

# ── Audio sintético ───────────────────────────────────────────────────────
SND_PUNCH = SND_KICK = SND_JUMP = SND_HIT = SND_KO = SND_COMBO = None
SND_SPECIAL = SND_SUPER = SND_BLOCK = SND_ROUND = None
SOUND_ON = False

def make_sound(freq, duration_ms, wave="square", volume=0.3):
    try:
        import numpy as np
        sample_rate = 44100
        n = int(sample_rate * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n, False)
        if wave == "square":
            wave_data = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave == "noise":
            wave_data = np.random.uniform(-1, 1, n)
        elif wave == "sweep":
            f_end = freq * 2
            freqs = np.linspace(freq, f_end, n)
            wave_data = np.sin(2 * np.pi * np.cumsum(freqs) / sample_rate)
        else:
            wave_data = np.sin(2 * np.pi * freq * t)
        fade = np.linspace(1, 0, n)
        wave_data = wave_data * fade * volume
        audio = np.int16(wave_data * 32767)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)
    except:
        return None

try:
    SND_PUNCH   = make_sound(180, 80, "square", 0.4)
    SND_KICK    = make_sound(120, 100, "square", 0.5)
    SND_JUMP    = make_sound(440, 60, "sine", 0.2)
    SND_HIT     = make_sound(80, 120, "noise", 0.5)
    SND_KO      = make_sound(60, 500, "square", 0.7)
    SND_COMBO   = make_sound(660, 120, "sine", 0.3)
    SND_SPECIAL = make_sound(300, 200, "sweep", 0.5)
    SND_SUPER   = make_sound(100, 400, "square", 0.8)
    SND_BLOCK   = make_sound(200, 60, "square", 0.3)
    SND_ROUND   = make_sound(523, 300, "sine", 0.5)
    SOUND_ON = True
except Exception as e:
    print("Audio desactivado:", e)

def play(snd):
    if SOUND_ON and snd:
        try: snd.play()
        except: pass

# ── Fuentes ───────────────────────────────────────────────────────────────
font_xl    = pygame.font.Font(None, 96)
font_lg    = pygame.font.Font(None, 72)
font_md    = pygame.font.Font(None, 48)
font_sm    = pygame.font.Font(None, 32)
font_xs    = pygame.font.Font(None, 24)
font_tiny  = pygame.font.Font(None, 20)

# ══════════════════════════════════════════════════════════════════════════
# PROYECTIL
# ══════════════════════════════════════════════════════════════════════════
class Projectile:
    def __init__(self, x, y, direction, owner, dmg, color, size=12, speed=10):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.owner = owner
        self.dmg = dmg
        self.color = color
        self.size = size
        self.speed = speed * direction
        self.alive = True
        self.frame = 0

    def update(self):
        self.x += self.speed
        self.frame += 1
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.size, int(self.y) - self.size,
                           self.size * 2, self.size * 2)

    def draw(self, surf):
        pulse = math.sin(self.frame * 0.4) * 3
        r1, g1, b1 = self.color
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size + pulse))
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), int(self.size // 2))
        # Aura
        for i in range(3):
            alpha_size = self.size + 4 + i * 4
            c = tuple(max(0, v // (i + 2)) for v in self.color)
            pygame.draw.circle(surf, c, (int(self.x), int(self.y)), alpha_size, 1)

projectile_list = []

# ══════════════════════════════════════════════════════════════════════════
# PARTÍCULAS
# ══════════════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color, vx, vy, life=30, size=4):
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.vx *= 0.95
        self.life -= 1

    def draw(self, surf):
        s = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), s)

class HitSpark:
    def __init__(self, x, y, color, big=False):
        self.x, self.y = x, y
        self.color = color
        self.life = 18 if big else 12
        self.max_life = self.life
        count = 12 if big else 8
        self.rays = [(random.uniform(0, 2*math.pi), random.uniform(10 if big else 8, 30 if big else 22)) for _ in range(count)]
        self.big = big

    def update(self):
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0: return
        progress = self.life / self.max_life
        for angle, length in self.rays:
            ex = self.x + math.cos(angle) * length * progress
            ey = self.y + math.sin(angle) * length * progress
            c = tuple(int(v * progress) for v in self.color)
            lw = 3 if self.big else 2
            pygame.draw.line(surf, c, (int(self.x), int(self.y)), (int(ex), int(ey)), lw)
        r = int((10 if self.big else 6) * progress)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)

class FloatingText:
    def __init__(self, x, y, text, color, size=32):
        self.x, self.y = float(x), float(y)
        self.text = text
        self.color = color
        self.life = 60
        self.font = pygame.font.Font(None, size)

    def update(self):
        self.y -= 1.5
        self.life -= 1

    def draw(self, surf):
        txt = self.font.render(self.text, True, self.color)
        surf.blit(txt, (int(self.x) - txt.get_width()//2, int(self.y)))

particle_list = []
spark_list = []
text_list = []

def emit_particles(x, y, color, count=12, spread=4):
    for _ in range(count):
        vx = random.uniform(-spread, spread)
        vy = random.uniform(-spread, 0)
        size = random.randint(2, 6)
        particle_list.append(Particle(x, y, color, vx, vy, life=random.randint(20, 45), size=size))

def emit_hit(x, y, color, big=False):
    spark_list.append(HitSpark(x, y, color, big))
    emit_particles(x, y, color, count=20 if big else 14, spread=6 if big else 4)

def add_text(x, y, text, color, size=32):
    text_list.append(FloatingText(x, y, text, color, size))

def update_effects():
    for p in particle_list[:]:
        p.update()
        if p.life <= 0: particle_list.remove(p)
    for s in spark_list[:]:
        s.update()
        if s.life <= 0: spark_list.remove(s)
    for t in text_list[:]:
        t.update()
        if t.life <= 0: text_list.remove(t)
    for proj in projectile_list[:]:
        proj.update()
        if not proj.alive: projectile_list.remove(proj)

def draw_effects(surf):
    for proj in projectile_list: proj.draw(surf)
    for p in particle_list: p.draw(surf)
    for s in spark_list: s.draw(surf)
    for t in text_list: t.draw(surf)

# ══════════════════════════════════════════════════════════════════════════
# PANTALLA SHAKE
# ══════════════════════════════════════════════════════════════════════════
screen_shake = 0
shake_x = 0
shake_y = 0

def trigger_shake(intensity=8, duration=12):
    global screen_shake
    screen_shake = max(screen_shake, duration)

def update_shake():
    global screen_shake, shake_x, shake_y
    if screen_shake > 0:
        screen_shake -= 1
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-4, 4)
    else:
        shake_x = shake_y = 0

# ══════════════════════════════════════════════════════════════════════════
# FONDO ANIMADO
# ══════════════════════════════════════════════════════════════════════════
FLOOR_Y = SCREEN_HEIGHT - 120

class Background:
    def __init__(self):
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT - 120),
                       random.uniform(0.5, 2), random.uniform(0, math.pi * 2)) for _ in range(80)]
        self.frame = 0
        self.buildings = []
        x = 0
        while x < SCREEN_WIDTH:
            w = random.randint(60, 120)
            h = random.randint(80, 200)
            wx_count = random.randint(2, 5)
            wy_count = random.randint(3, 8)
            lit = [[random.random() > 0.4 for _ in range(wx_count)] for _ in range(wy_count)]
            self.buildings.append((x, SCREEN_HEIGHT - 120 - h, w, h, wx_count, wy_count, lit))
            x += w + random.randint(0, 10)
        # Neón signs
        self.neon_signs = [
            {"x": 200, "y": SCREEN_HEIGHT - 260, "text": "FIGHT", "color": (255, 40, 100), "phase": 0},
            {"x": 900, "y": SCREEN_HEIGHT - 280, "text": "BAR", "color": (40, 200, 255), "phase": 1.5},
            {"x": 550, "y": SCREEN_HEIGHT - 300, "text": "ARCADE", "color": (180, 40, 255), "phase": 3},
        ]

    def update(self):
        self.frame += 1

    def draw(self, surf):
        for y in range(SCREEN_HEIGHT - 120):
            t = y / (SCREEN_HEIGHT - 120)
            r = int(10 + t * 5)
            g = int(5 + t * 8)
            b = int(30 + t * 20)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        for sx, sy, size, phase in self.stars:
            brightness = int(180 + 75 * math.sin(self.frame * 0.03 + phase))
            pygame.draw.circle(surf, (brightness, brightness, brightness), (sx, sy), int(size))

        pygame.draw.circle(surf, (220, 220, 180), (100, 70), 35)
        pygame.draw.circle(surf, (15, 10, 30), (112, 62), 32)

        for bx, by, bw, bh, wx_c, wy_c, lit in self.buildings:
            pygame.draw.rect(surf, (8, 6, 15), (bx + 4, by + 4, bw, bh))
            pygame.draw.rect(surf, (25, 20, 45), (bx, by, bw, bh))
            pad_x = bw // (wx_c + 1)
            pad_y = bh // (wy_c + 1)
            for row in range(wy_c):
                for col in range(wx_c):
                    ww, wh = 8, 10
                    wx2 = bx + pad_x * (col + 1) - ww // 2
                    wy2 = by + pad_y * (row + 1) - wh // 2
                    if lit[row][col]:
                        flicker = (self.frame // 90 + row * wx_c + col) % 20 == 0
                        c = (200, 180, 80) if not flicker else (60, 50, 20)
                    else:
                        c = (15, 12, 25)
                    pygame.draw.rect(surf, c, (wx2, wy2, ww, wh))

        # Neón signs
        for sign in self.neon_signs:
            glow = abs(math.sin(self.frame * 0.05 + sign["phase"]))
            r, g, b = sign["color"]
            c = (int(r * (0.4 + 0.6 * glow)), int(g * (0.4 + 0.6 * glow)), int(b * (0.4 + 0.6 * glow)))
            txt = font_xs.render(sign["text"], True, c)
            surf.blit(txt, (sign["x"] - txt.get_width() // 2, sign["y"]))
            if glow > 0.7:
                for dx in [-1, 1, 0, 0]:
                    for dy in [-1, 1, 0, 0]:
                        outline = font_xs.render(sign["text"], True, tuple(v // 4 for v in sign["color"]))
                        surf.blit(outline, (sign["x"] - outline.get_width() // 2 + dx, sign["y"] + dy))

        floor_y = SCREEN_HEIGHT - 120
        pygame.draw.rect(surf, FLOOR_COLOR, (0, floor_y, SCREEN_WIDTH, 120))
        for i in range(0, SCREEN_WIDTH, 80):
            pygame.draw.line(surf, FLOOR_LINE, (i, floor_y), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)
        pygame.draw.line(surf, (100, 80, 60), (0, floor_y), (SCREEN_WIDTH, floor_y), 3)

        colors_neon = [(255, 40, 100), (40, 200, 255), (180, 40, 255)]
        for i, (r, g, b) in enumerate(colors_neon):
            x = SCREEN_WIDTH // 4 * (i + 1)
            for alpha_step in range(3):
                pygame.draw.line(surf, (r // 3, g // 3, b // 3),
                                 (x - 20 + alpha_step, floor_y + 5 + alpha_step),
                                 (x + 20 - alpha_step, floor_y + 5 + alpha_step), 1)


# ══════════════════════════════════════════════════════════════════════════
# FIGHTER
# ══════════════════════════════════════════════════════════════════════════
class AttackType(Enum):
    NONE    = 0
    PUNCH   = 1
    KICK    = 2
    SPECIAL = 3
    SUPER   = 4

class FighterState(Enum):
    IDLE    = 0
    WALK    = 1
    JUMP    = 2
    ATTACK  = 3
    HIT     = 4
    KO      = 5
    BLOCK   = 6
    SPECIAL = 7
    SUPER   = 8

class Fighter:
    def __init__(self, x, player_id=1, char_key="RYU", controls=None, is_ai=False):
        self.player_id = player_id
        self.is_ai = is_ai
        self.char_key = char_key
        self.char = CHARACTERS[char_key]
        self.x = float(x)
        self.y = float(FLOOR_Y - 110)
        self.w = 52
        self.h = 110
        self.controls = controls or {}

        # Stats from char
        self.max_hp = self.char["hp"]
        self.hp = self.max_hp
        self.speed = self.char["speed"]
        self.direction = 1 if player_id == 1 else -1
        self.jump_power = self.char["jump_power"]

        self.PUNCH_DMG   = self.char["punch_dmg"]
        self.KICK_DMG    = self.char["kick_dmg"]
        self.SPECIAL_DMG = self.char["special_dmg"]
        self.SUPER_DMG   = self.char["super_dmg"]
        self.PUNCH_RANGE = 75
        self.KICK_RANGE  = 100

        # Colores
        self.color      = self.char["color"]
        self.dark_color = self.char["dark"]
        self.accent     = self.char["accent"]
        self.special_color = self.char["special_color"]
        self.super_color   = self.char["super_color"]

        # Física
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True

        # Ataque
        self.atk_type = AttackType.NONE
        self.atk_cooldown = 0
        self.atk_timer = 0
        self.atk_active = False
        self.atk_hit = False

        # Estado
        self.state = FighterState.IDLE
        self.hit_stun = 0
        self.ko = False
        self.blocking = False

        # Súper medidor (0-100)
        self.super_meter = 0
        self.super_flash = 0  # frames de flash cuando se llena

        # Carga de especial (mantener botón)
        self.special_charge = 0
        self.SPECIAL_CHARGE_MAX = 45

        # Combo
        self.combo_count = 0
        self.combo_timer = 0

        # Animación
        self.anim_frame = 0
        self.walk_cycle = 0
        self.anim_state = "idle"

        # IA
        self.ai_reaction = 0
        self.ai_aggression = random.uniform(0.65, 1.0)
        self.ai_tactic = "attack"
        self.ai_tactic_timer = 0

    # ── Entrada jugador ───────────────────────────────────────────────────
    def handle_input(self, keys, other):
        if self.ko or self.hit_stun > 0:
            self.vx = 0
            return

        c = self.controls
        self.vx = 0
        self.blocking = False

        if keys[c.get('left', pygame.K_a)]:
            self.vx = -self.speed
            self.direction = -1
            if self.on_ground: self.state = FighterState.WALK
        if keys[c.get('right', pygame.K_d)]:
            self.vx = self.speed
            self.direction = 1
            if self.on_ground: self.state = FighterState.WALK

        if keys[c.get('jump', pygame.K_w)] and self.on_ground:
            self.vy = -self.jump_power
            self.on_ground = False
            self.state = FighterState.JUMP
            play(SND_JUMP)

        # Bloqueo: tecla abajo
        if keys[c.get('block', pygame.K_s)] and self.on_ground:
            self.blocking = True
            self.state = FighterState.BLOCK
            self.vx = 0

        # Carga especial
        if keys[c.get('special', pygame.K_e)]:
            self.special_charge = min(self.special_charge + 1, self.SPECIAL_CHARGE_MAX + 10)
        else:
            if self.special_charge >= self.SPECIAL_CHARGE_MAX and self.atk_cooldown <= 0:
                self._start_attack(AttackType.SPECIAL)
            self.special_charge = 0

        if self.atk_cooldown <= 0 and self.special_charge == 0:
            if keys[c.get('punch', pygame.K_SPACE)]:
                self._start_attack(AttackType.PUNCH)
            elif keys[c.get('kick', pygame.K_LSHIFT)]:
                self._start_attack(AttackType.KICK)
            elif keys[c.get('super', pygame.K_q)] and self.super_meter >= 100:
                self._start_attack(AttackType.SUPER)

        if self.vx == 0 and self.on_ground and not self.blocking and self.atk_timer <= 0:
            self.state = FighterState.IDLE

    # ── IA avanzada ────────────────────────────────────────────────────────
    def handle_ai(self, other):
        if self.ko or self.hit_stun > 0:
            self.vx = 0
            return

        self.ai_reaction -= 1
        self.ai_tactic_timer -= 1

        if self.ai_tactic_timer <= 0:
            r = random.random()
            hp_ratio = self.hp / self.max_hp
            if hp_ratio < 0.3:
                # Desesperado: agresivo o evasivo
                self.ai_tactic = "aggressive" if r < 0.6 else "evade"
            elif other.hp / other.max_hp < 0.25:
                self.ai_tactic = "aggressive"
            else:
                if r < 0.4: self.ai_tactic = "attack"
                elif r < 0.65: self.ai_tactic = "poke"
                elif r < 0.8: self.ai_tactic = "evade"
                else: self.ai_tactic = "aggressive"
            self.ai_tactic_timer = random.randint(60, 180)

        if self.ai_reaction > 0:
            return
        self.ai_reaction = random.randint(2, 5)

        dist = other.x - self.x
        abs_dist = abs(dist)
        self.direction = 1 if dist > 0 else -1
        self.blocking = False

        # Bloqueo ante combos/supers
        if (other.combo_count >= 2 or other.atk_type == AttackType.SUPER) and random.random() < 0.35:
            self.blocking = True
            self.vx = 0
            self.state = FighterState.BLOCK
            return

        if self.ai_tactic == "evade":
            if abs_dist < 150:
                self.vx = -self.direction * self.speed
            if self.on_ground and random.random() < 0.04:
                self.vy = -self.jump_power
                self.on_ground = False
                self.state = FighterState.JUMP
                play(SND_JUMP)

        elif self.ai_tactic in ("attack", "poke", "aggressive"):
            engage = 120 if self.ai_tactic == "poke" else (160 if self.ai_tactic == "aggressive" else 130)
            back_off = 35

            if abs_dist > engage:
                self.vx = self.direction * self.speed * (0.9 if self.ai_tactic == "aggressive" else 0.75)
                self.state = FighterState.WALK
            elif abs_dist < back_off:
                self.vx = -self.direction * self.speed * 0.5
            else:
                self.vx = 0
                self.state = FighterState.IDLE

            if self.atk_cooldown <= 0:
                prob = 0.05 * self.ai_aggression
                if self.ai_tactic == "aggressive": prob *= 1.5
                if random.random() < prob:
                    if self.super_meter >= 100 and random.random() < 0.3:
                        self._start_attack(AttackType.SUPER)
                    elif abs_dist < self.KICK_RANGE * 1.2:
                        if random.random() < 0.4 and self.special_charge < self.SPECIAL_CHARGE_MAX:
                            self.special_charge += 10
                        else:
                            attack = AttackType.KICK if abs_dist > 60 else AttackType.PUNCH
                            self._start_attack(attack)
                    elif abs_dist < 250 and random.random() < 0.08:
                        self._start_attack(AttackType.SPECIAL)

        if self.on_ground and random.random() < 0.005:
            self.vy = -self.jump_power
            self.on_ground = False
            self.state = FighterState.JUMP
            play(SND_JUMP)

    # ── Ataques ────────────────────────────────────────────────────────────
    def _start_attack(self, atype):
        self.atk_type = atype
        self.atk_hit = False
        self.atk_active = True

        if atype == AttackType.PUNCH:
            self.atk_timer = 14
            self.atk_cooldown = 26
            self.state = FighterState.ATTACK
            play(SND_PUNCH)
        elif atype == AttackType.KICK:
            self.atk_timer = 18
            self.atk_cooldown = 34
            self.state = FighterState.ATTACK
            play(SND_KICK)
        elif atype == AttackType.SPECIAL:
            self.atk_timer = 25
            self.atk_cooldown = 50
            self.state = FighterState.SPECIAL
            play(SND_SPECIAL)
            # Disparar proyectil
            proj_y = self.y + self.h // 2
            proj_x = self.x + self.w if self.direction > 0 else self.x
            projectile_list.append(Projectile(
                proj_x, proj_y, self.direction, self,
                self.SPECIAL_DMG, self.special_color, size=14, speed=10
            ))
            add_text(int(self.x + self.w // 2), int(self.y - 40),
                     self.char["special_name"], self.special_color, 30)
        elif atype == AttackType.SUPER:
            self.atk_timer = 50
            self.atk_cooldown = 80
            self.state = FighterState.SUPER
            self.super_meter = 0
            play(SND_SUPER)
            trigger_shake(10, 20)
            add_text(int(self.x + self.w // 2), int(self.y - 60),
                     self.char["super_name"] + "!!", self.super_color, 38)
            # Super proyectil gigante
            proj_y = self.y + self.h // 2
            proj_x = self.x + self.w if self.direction > 0 else self.x
            projectile_list.append(Projectile(
                proj_x, proj_y, self.direction, self,
                self.SUPER_DMG, self.super_color, size=24, speed=14
            ))
            emit_particles(int(self.x + self.w // 2), int(self.y + self.h // 2),
                           self.super_color, 30, 8)

    def get_attack_rect(self):
        if not self.atk_active or self.atk_type in (AttackType.SPECIAL, AttackType.SUPER):
            return None
        rng = self.PUNCH_RANGE if self.atk_type == AttackType.PUNCH else self.KICK_RANGE
        h_offset = self.h // 3 if self.atk_type == AttackType.PUNCH else self.h // 2
        if self.direction > 0:
            return pygame.Rect(self.x + self.w, self.y + h_offset, rng, 24)
        else:
            return pygame.Rect(self.x - rng, self.y + h_offset, rng, 24)

    def get_body_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    # ── Daño ──────────────────────────────────────────────────────────────
    def take_damage(self, dmg, attacker, is_super=False):
        if self.blocking:
            dmg = max(1, int(dmg * 0.15))
            add_text(int(self.x + self.w // 2), int(self.y - 20), "BLOCK!", CYAN, 28)
            play(SND_BLOCK)
        else:
            # Gana súper al recibir daño
            self.super_meter = min(100, self.super_meter + dmg // 3)
            attacker.super_meter = min(100, attacker.super_meter + dmg // 4)

        actual = max(1, dmg)
        self.hp -= actual
        if self.hp < 0: self.hp = 0

        kb = 8 if is_super else (6 if dmg > 20 else 4)
        self.vx = -attacker.direction * kb
        self.vy = -5 if is_super else -4

        self.hit_stun = 20 if is_super else (15 if dmg > 20 else 10)
        self.state = FighterState.HIT
        play(SND_HIT)

        cx = int(self.x + self.w // 2)
        cy = int(self.y + self.h // 3)
        emit_hit(cx, cy, self.color, big=is_super)
        if is_super:
            trigger_shake(8, 15)
        color_txt = ORANGE if is_super else RED
        add_text(cx, int(self.y - 20), f"-{actual}", color_txt, 36 if is_super else 30)

        if self.hp <= 0:
            self.ko = True
            self.state = FighterState.KO
            play(SND_KO)
            emit_particles(cx, cy, self.color, 40, 8)
            trigger_shake(12, 25)

    # ── Física y update ───────────────────────────────────────────────────
    def update(self):
        if self.atk_cooldown > 0: self.atk_cooldown -= 1
        if self.hit_stun > 0:
            self.hit_stun -= 1
            if self.hit_stun == 0 and not self.ko:
                self.state = FighterState.IDLE

        if self.atk_active:
            self.atk_timer -= 1
            if self.atk_timer <= 0:
                self.atk_active = False
                self.atk_type = AttackType.NONE
                if not self.ko and self.hit_stun == 0:
                    self.state = FighterState.IDLE

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0

        if self.super_flash > 0:
            self.super_flash -= 1

        self.vy += 0.6
        self.y += self.vy
        self.x += self.vx

        if self.y >= FLOOR_Y - self.h:
            self.y = float(FLOOR_Y - self.h)
            self.vy = 0
            if not self.on_ground:
                emit_particles(int(self.x + self.w // 2), FLOOR_Y, (120, 100, 60), 6, 2)
            self.on_ground = True
            if self.state == FighterState.JUMP:
                self.state = FighterState.IDLE
        else:
            self.on_ground = False

        self.x = max(0, min(SCREEN_WIDTH - self.w, self.x))

        if self.state == FighterState.WALK:
            self.walk_cycle += 0.25
        self.anim_frame += 1

    # ── Dibujo ────────────────────────────────────────────────────────────
    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        cx = ix + self.w // 2

        # Sombra
        dist_to_floor = FLOOR_Y - (iy + self.h)
        shadow_scale = max(0.3, 1 - dist_to_floor / 200)
        sw = int(self.w * shadow_scale)
        pygame.draw.ellipse(surf, (0, 0, 0), (cx - sw // 2, FLOOR_Y - 5, sw, 10))

        flash = self.hit_stun > 0 and (self.anim_frame % 4 < 2)
        body_color = WHITE if flash else self.color
        dark_color  = WHITE if flash else self.dark_color

        # KO — caído
        if self.ko:
            pygame.draw.rect(surf, self.dark_color, (ix - 10, iy + self.h - 20, self.w + 20, 22))
            pygame.draw.rect(surf, self.color, (ix - 10, iy + self.h - 20, self.w + 20, 22), 2)
            ko_txt = font_lg.render("KO", True, YELLOW)
            surf.blit(ko_txt, (cx - ko_txt.get_width() // 2, iy - 70))
            for i in range(3):
                r = 8 + i * 6
                pygame.draw.circle(surf, YELLOW, (cx, iy - 40), r, 1)
            return

        # Super aura si medidor lleno
        if self.super_meter >= 100:
            pulse = abs(math.sin(self.anim_frame * 0.1)) * 6
            aura_c = tuple(min(255, v + 40) for v in self.super_color)
            for r in [20, 30, 40]:
                pygame.draw.circle(surf, tuple(v // 4 for v in aura_c),
                                   (cx, iy + self.h // 2), r + int(pulse), 2)

        # Piernas
        leg_offset = int(math.sin(self.walk_cycle) * 6) if self.state == FighterState.WALK else 0
        leg_y = iy + int(self.h * 0.65)
        leg_h = int(self.h * 0.35)
        pygame.draw.rect(surf, dark_color, (ix + 2, leg_y + leg_offset, self.w // 2 - 2, leg_h - leg_offset))
        pygame.draw.rect(surf, dark_color, (ix + self.w // 2, leg_y - leg_offset, self.w // 2 - 2, leg_h + leg_offset))

        # Torso
        torso_h = int(self.h * 0.45)
        torso_y = iy + int(self.h * 0.2)
        pygame.draw.rect(surf, body_color, (ix, torso_y, self.w, torso_h))
        pygame.draw.rect(surf, self.accent, (ix + 4, torso_y + torso_h - 8, self.w - 8, 8))

        # Cabeza
        head_r = int(self.w * 0.42)
        head_cx = cx
        head_cy = iy + int(self.h * 0.12)
        pygame.draw.circle(surf, body_color, (head_cx, head_cy), head_r)
        pygame.draw.circle(surf, self.accent, (head_cx, head_cy), head_r, 2)

        # Ojos
        eye_offset = 7 * self.direction
        eye_x = head_cx + eye_offset
        pygame.draw.circle(surf, BLACK, (eye_x, head_cy - 2), 4)
        pygame.draw.circle(surf, WHITE, (eye_x, head_cy - 2), 2)

        # Brazo de ataque
        if self.atk_active and self.atk_type in (AttackType.PUNCH, AttackType.KICK):
            max_timer = 14 if self.atk_type == AttackType.PUNCH else 18
            progress = 1 - self.atk_timer / max_timer
            arm_ext = int((self.PUNCH_RANGE if self.atk_type == AttackType.PUNCH else self.KICK_RANGE) * 0.75)
            arm_x = cx + self.direction * int(arm_ext * min(1, progress * 2))
            arm_y = torso_y + int(torso_h * (0.35 if self.atk_type == AttackType.PUNCH else 0.65))
            arm_color = YELLOW if self.atk_type == AttackType.PUNCH else ORANGE
            pygame.draw.line(surf, arm_color, (cx, arm_y), (arm_x, arm_y), 5)
            pygame.draw.circle(surf, arm_color, (arm_x, arm_y), 8)
            for r in range(3):
                pygame.draw.circle(surf, arm_color, (arm_x, arm_y), 10 + r * 4, 1)
        elif self.state in (FighterState.SPECIAL, FighterState.SUPER):
            # Pose de especial / super
            progress = 1 - self.atk_timer / (25 if self.state == FighterState.SPECIAL else 50)
            arm_color = self.special_color if self.state == FighterState.SPECIAL else self.super_color
            arm_x = cx + self.direction * int(40 * min(1, progress * 2))
            arm_y = torso_y + int(torso_h * 0.35)
            pygame.draw.line(surf, arm_color, (cx, arm_y), (arm_x, arm_y), 5)
            for r in range(4):
                glow_r = 8 + r * 5
                pygame.draw.circle(surf, arm_color, (arm_x, arm_y), glow_r, 1)
        else:
            arm_y = torso_y + int(torso_h * 0.3)
            pygame.draw.line(surf, dark_color, (cx - self.w // 4, arm_y),
                             (cx - self.w // 4 - 8 * self.direction, arm_y + 12), 4)
            pygame.draw.line(surf, dark_color, (cx + self.w // 4, arm_y),
                             (cx + self.w // 4 + 8 * self.direction, arm_y + 12), 4)

        pygame.draw.rect(surf, self.dark_color, (ix, torso_y, self.w, torso_h), 2)

        # Escudo
        if self.blocking:
            shield_x = cx + self.direction * (self.w // 2 + 5)
            pygame.draw.rect(surf, CYAN, (shield_x - 5, torso_y, 10, torso_h + 20), 3)

        # Nombre encima
        name_txt = font_tiny.render(self.char["display"], True, self.accent)
        surf.blit(name_txt, (cx - name_txt.get_width() // 2, iy - 30))

    def _draw_health_bar(self, surf, ix, iy):
        bw = self.w + 20
        bh = 8
        bx = ix - 10
        by = iy - 18
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (40, 20, 20), (bx, by, bw, bh))
        bar_color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
        pygame.draw.rect(surf, bar_color, (bx, by, int(bw * ratio), bh))
        pygame.draw.rect(surf, WHITE, (bx, by, bw, bh), 1)


# ══════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════
def draw_hud(surf, p1, p2, frame_count, mode_2p, round_num, p1_wins, p2_wins):
    bar_w = 400
    bar_h = 30
    bar_y = 16

    # P1 bar
    p1_ratio = p1.hp / p1.max_hp
    pygame.draw.rect(surf, (30, 15, 15), (20, bar_y, bar_w, bar_h), border_radius=5)
    bar_color_p1 = GREEN if p1_ratio > 0.5 else (YELLOW if p1_ratio > 0.25 else RED)
    pygame.draw.rect(surf, bar_color_p1, (20, bar_y, int(bar_w * p1_ratio), bar_h), border_radius=5)
    pygame.draw.rect(surf, WHITE, (20, bar_y, bar_w, bar_h), 2, border_radius=5)

    label1 = font_sm.render(CHARACTERS[p1.char_key]["display"], True, p1.color)
    surf.blit(label1, (22, bar_y + bar_h + 4))
    hp1_txt = font_xs.render(f"{int(p1.hp)}/{p1.max_hp}", True, WHITE)
    surf.blit(hp1_txt, (22 + bar_w - hp1_txt.get_width(), bar_y + bar_h + 4))

    # P1 super meter
    sm_w = bar_w
    sm_h = 10
    sm_y = bar_y + bar_h + 24
    pygame.draw.rect(surf, (20, 20, 60), (20, sm_y, sm_w, sm_h), border_radius=3)
    sm_ratio = p1.super_meter / 100
    sm_color = GOLD if p1.super_meter >= 100 else (100, 100, 220)
    if p1.super_meter >= 100:
        pulse = abs(math.sin(frame_count * 0.1)) * 20
        sm_color = (int(180 + pulse), int(150 + pulse), 0)
    pygame.draw.rect(surf, sm_color, (20, sm_y, int(sm_w * sm_ratio), sm_h), border_radius=3)
    pygame.draw.rect(surf, (100, 100, 255), (20, sm_y, sm_w, sm_h), 1, border_radius=3)
    super_lbl = font_tiny.render("SUPER", True, (100, 100, 200))
    surf.blit(super_lbl, (22, sm_y + sm_h + 2))

    # P2 bar
    p2_ratio = p2.hp / p2.max_hp
    p2_x = SCREEN_WIDTH - 20 - bar_w
    pygame.draw.rect(surf, (30, 15, 15), (p2_x, bar_y, bar_w, bar_h), border_radius=5)
    bar_color_p2 = GREEN if p2_ratio > 0.5 else (YELLOW if p2_ratio > 0.25 else RED)
    filled_w = int(bar_w * p2_ratio)
    pygame.draw.rect(surf, bar_color_p2, (p2_x + bar_w - filled_w, bar_y, filled_w, bar_h), border_radius=5)
    pygame.draw.rect(surf, WHITE, (p2_x, bar_y, bar_w, bar_h), 2, border_radius=5)

    label2_text = CHARACTERS[p2.char_key]["display"] if mode_2p else f"CPU: {CHARACTERS[p2.char_key]['display']}"
    label2 = font_sm.render(label2_text, True, p2.color)
    surf.blit(label2, (p2_x + bar_w - label2.get_width(), bar_y + bar_h + 4))
    hp2_txt = font_xs.render(f"{int(p2.hp)}/{p2.max_hp}", True, WHITE)
    surf.blit(hp2_txt, (p2_x, bar_y + bar_h + 4))

    # P2 super meter
    sm_y2 = bar_y + bar_h + 24
    pygame.draw.rect(surf, (20, 20, 60), (p2_x, sm_y2, sm_w, sm_h), border_radius=3)
    sm_ratio2 = p2.super_meter / 100
    sm_color2 = GOLD if p2.super_meter >= 100 else (100, 100, 220)
    if p2.super_meter >= 100:
        pulse = abs(math.sin(frame_count * 0.1)) * 20
        sm_color2 = (int(180 + pulse), int(150 + pulse), 0)
    pygame.draw.rect(surf, sm_color2, (p2_x + bar_w - int(sm_w * sm_ratio2), sm_y2, int(sm_w * sm_ratio2), sm_h), border_radius=3)
    pygame.draw.rect(surf, (100, 100, 255), (p2_x, sm_y2, sm_w, sm_h), 1, border_radius=3)
    super_lbl2 = font_tiny.render("SUPER", True, (100, 100, 200))
    surf.blit(super_lbl2, (p2_x + bar_w - super_lbl2.get_width(), sm_y2 + sm_h + 2))

    # Centro: ronda + tiempo
    round_txt = font_sm.render(f"ROUND {round_num}", True, GOLD)
    surf.blit(round_txt, (SCREEN_WIDTH // 2 - round_txt.get_width() // 2, bar_y))

    elapsed = frame_count // FPS
    time_c = RED if elapsed > 60 else GOLD
    time_txt = font_md.render(str(elapsed), True, time_c)
    surf.blit(time_txt, (SCREEN_WIDTH // 2 - time_txt.get_width() // 2, bar_y + 28))

    # Victorias (puntos)
    for i in range(p1_wins):
        pygame.draw.circle(surf, GOLD, (SCREEN_WIDTH // 2 - 20 - i * 18, bar_y + 70), 6)
    for i in range(p2_wins):
        pygame.draw.circle(surf, ORANGE, (SCREEN_WIDTH // 2 + 20 + i * 18, bar_y + 70), 6)

    # Combos
    if p1.combo_count >= 2:
        combo_txt = font_md.render(f"{p1.combo_count} COMBO!", True, GOLD)
        surf.blit(combo_txt, (20, 110))
    if p2.combo_count >= 2:
        combo_txt2 = font_md.render(f"{p2.combo_count} COMBO!", True, ORANGE)
        surf.blit(combo_txt2, (SCREEN_WIDTH - 20 - combo_txt2.get_width(), 110))

    # Hint controles
    if mode_2p:
        hint_str = "P1: WASD+Space/Shift/E(especial)/Q(super)  |  P2: ←→↑↓+L/;/O(especial)/P(super)"
    else:
        hint_str = "WASD:Mover  Space:Puñetazo  LShift:Patada  E(mantén):Especial  Q:SUPER(barra llena)"
    hint = font_tiny.render(hint_str, True, (100, 100, 100))
    surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 16))


# ══════════════════════════════════════════════════════════════════════════
# PANTALLA SELECCIÓN DE PERSONAJE
# ══════════════════════════════════════════════════════════════════════════
def draw_char_select(surf, bg, frame, selecting_for, selected_chars, cursor):
    bg.draw(surf)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    surf.blit(overlay, (0, 0))

    title_str = f"SELECCIONA PERSONAJE - {'JUGADOR 1' if selecting_for == 1 else ('JUGADOR 2' if selecting_for == 2 else 'CPU')}"
    title = font_md.render(title_str, True, GOLD)
    surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

    chars = list(CHARACTERS.keys())
    cols = len(chars)
    box_w = 200
    box_h = 180
    start_x = SCREEN_WIDTH // 2 - (cols * box_w) // 2 + box_w // 2
    y = 150

    for i, key in enumerate(chars):
        ch = CHARACTERS[key]
        x = start_x + i * box_w
        selected = (i == cursor)

        # Caja
        border_c = GOLD if selected else (80, 80, 80)
        bg_c = (40, 30, 60) if selected else (20, 15, 35)
        pygame.draw.rect(surf, bg_c, (x - box_w // 2 + 5, y, box_w - 10, box_h), border_radius=8)
        pygame.draw.rect(surf, border_c, (x - box_w // 2 + 5, y, box_w - 10, box_h), 3, border_radius=8)

        # Mini personaje dibujado
        mini_cx = x
        mini_cy = y + box_h // 2 - 10
        scale = 0.7
        mini_w = int(52 * scale)
        mini_h = int(110 * scale)

        # Torso
        pygame.draw.rect(surf, ch["color"], (mini_cx - mini_w // 2, mini_cy - mini_h // 2 + 20, mini_w, int(mini_h * 0.45)))
        pygame.draw.rect(surf, ch["accent"], (mini_cx - mini_w // 2, mini_cy - mini_h // 2 + 20 + int(mini_h * 0.45) - 6, mini_w, 6))
        # Cabeza
        head_r = int(mini_w * 0.42)
        pygame.draw.circle(surf, ch["color"], (mini_cx, mini_cy - mini_h // 2 + 15), head_r)
        pygame.draw.circle(surf, ch["accent"], (mini_cx, mini_cy - mini_h // 2 + 15), head_r, 2)
        # Piernas
        leg_y = mini_cy - mini_h // 2 + 20 + int(mini_h * 0.45)
        pygame.draw.rect(surf, ch["dark"], (mini_cx - mini_w // 2, leg_y, mini_w // 2 - 1, int(mini_h * 0.35)))
        pygame.draw.rect(surf, ch["dark"], (mini_cx, leg_y, mini_w // 2 - 1, int(mini_h * 0.35)))

        # Nombre
        name_txt = font_sm.render(ch["display"], True, ch["color"])
        surf.blit(name_txt, (x - name_txt.get_width() // 2, y + box_h + 5))

        # Descripción
        desc_txt = font_tiny.render(ch["desc"], True, (180, 180, 180))
        surf.blit(desc_txt, (x - desc_txt.get_width() // 2, y + box_h + 28))

    # Stats del seleccionado
    sel_key = chars[cursor]
    sel = CHARACTERS[sel_key]
    stat_y = y + box_h + 60
    stats = [
        f"HP: {sel['hp']}",
        f"Velocidad: {sel['speed']}",
        f"Puño: {sel['punch_dmg']}  Patada: {sel['kick_dmg']}",
        f"Especial ({sel['special_name']}): {sel['special_dmg']}",
        f"SUPER ({sel['super_name']}): {sel['super_dmg']}",
    ]
    for i, s in enumerate(stats):
        st = font_xs.render(s, True, sel["accent"])
        surf.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, stat_y + i * 24))

    # Ya seleccionados
    if selected_chars[0]:
        p1_lbl = font_xs.render(f"P1: {CHARACTERS[selected_chars[0]]['display']}", True, CHARACTERS[selected_chars[0]]["color"])
        surf.blit(p1_lbl, (20, SCREEN_HEIGHT - 50))

    hint = font_sm.render("← → para elegir  |  ENTER / ESPACIO para confirmar", True, (180, 180, 180))
    surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 30))


# ══════════════════════════════════════════════════════════════════════════
# PANTALLA MENÚ
# ══════════════════════════════════════════════════════════════════════════
def draw_menu(surf, bg, frame):
    bg.draw(surf)

    t = math.sin(frame * 0.04) * 4
    # Sombra del título
    for dx, dy in [(4, 4), (-2, 4)]:
        shadow = font_xl.render("MINI STREET FIGHTER", True, (80, 20, 0))
        surf.blit(shadow, (SCREEN_WIDTH // 2 - shadow.get_width() // 2 + dx, 120 + int(t) + dy))
    title = font_xl.render("MINI STREET FIGHTER", True, GOLD)
    surf.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120 + int(t)))

    sub = font_sm.render("GOTY EDITION", True, CYAN)
    surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 225))

    # Línea decorativa
    pygame.draw.line(surf, GOLD, (SCREEN_WIDTH // 2 - 300, 260), (SCREEN_WIDTH // 2 + 300, 260), 2)

    options = [
        ("1  —  1 Jugador (vs CPU)", WHITE),
        ("2  —  2 Jugadores", WHITE),
        ("ESC  —  Salir", (150, 150, 150)),
    ]
    y = 290
    for text, color in options:
        pulse = abs(math.sin(frame * 0.05 + y)) if color == WHITE else 0
        c = tuple(min(255, int(v + pulse * 40)) for v in color)
        txt = font_md.render(text, True, c)
        surf.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
        y += 60

    # Personajes preview en la parte inferior
    chars = list(CHARACTERS.keys())
    for i, key in enumerate(chars):
        ch = CHARACTERS[key]
        px = SCREEN_WIDTH // (len(chars) + 1) * (i + 1)
        py = 520
        swing = math.sin(frame * 0.05 + i * 1.5) * 5
        # Mini figura
        pygame.draw.rect(surf, ch["color"], (px - 18, py - 40 + int(swing), 36, 50))
        pygame.draw.circle(surf, ch["color"], (px, py - 50 + int(swing)), 18)
        pygame.draw.circle(surf, ch["accent"], (px, py - 50 + int(swing)), 18, 2)
        name = font_tiny.render(ch["display"], True, ch["accent"])
        surf.blit(name, (px - name.get_width() // 2, py + 15))

    controls = [
        "P1: WASD + Space(puño) + LShift(patada) + E(especial) + Q(super)",
        "P2: ←→↑↓ + L(puño) + ;(patada) + O(especial) + P(super)",
    ]
    y = 600
    for line in controls:
        c = font_tiny.render(line, True, (120, 120, 120))
        surf.blit(c, (SCREEN_WIDTH // 2 - c.get_width() // 2, y))
        y += 18


# ══════════════════════════════════════════════════════════════════════════
# PANTALLA RONDA
# ══════════════════════════════════════════════════════════════════════════
def draw_round_announce(surf, round_num, timer):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    if timer > 30:
        alpha = int(255 * (60 - timer) / 30)
    else:
        alpha = int(255 * timer / 30)
    overlay.fill((0, 0, 0, min(180, alpha * 2)))
    surf.blit(overlay, (0, 0))

    scale = 1 + abs(math.sin(timer * 0.1)) * 0.2
    round_surf = font_xl.render(f"ROUND {round_num}", True, GOLD)
    fight_surf = font_lg.render("FIGHT!", True, RED) if timer < 30 else None

    surf.blit(round_surf, (SCREEN_WIDTH // 2 - round_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
    if fight_surf:
        surf.blit(fight_surf, (SCREEN_WIDTH // 2 - fight_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 10))


# ══════════════════════════════════════════════════════════════════════════
# PANTALLA RESULTADO
# ══════════════════════════════════════════════════════════════════════════
def draw_result_screen(surf, bg, winner_id, mode_2p, p1_wins, p2_wins, char1, char2, frame):
    bg.draw(surf)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))

    if winner_id == 0:
        main_text = "¡EMPATE!"
        color = YELLOW
    elif winner_id == 1:
        main_text = f"¡VICTORIA DE {CHARACTERS[char1]['display']}!" if mode_2p else "¡VICTORIA!"
        color = CHARACTERS[char1]["color"]
    else:
        main_text = f"¡VICTORIA DE {CHARACTERS[char2]['display']}!" if mode_2p else "¡DERROTA!"
        color = CHARACTERS[char2]["color"] if mode_2p else RED

    pulse = abs(math.sin(frame * 0.05)) * 20
    c = tuple(min(255, v + int(pulse)) for v in color)
    big = font_xl.render(main_text, True, c)
    surf.blit(big, (SCREEN_WIDTH // 2 - big.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    # Marcador
    score_txt = font_lg.render(f"{p1_wins}  :  {p2_wins}", True, GOLD)
    surf.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, SCREEN_HEIGHT // 2))

    sub = font_sm.render("ESPACIO — Volver al menú", True, YELLOW)
    surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 100))


# ══════════════════════════════════════════════════════════════════════════
# COLISIONES
# ══════════════════════════════════════════════════════════════════════════
def check_collisions(p1, p2):
    # Proyectiles
    for proj in projectile_list[:]:
        if proj.owner == p1 and not p1.atk_hit:
            if proj.get_rect().colliderect(p2.get_body_rect()):
                p2.take_damage(proj.dmg, p1, is_super=(proj.size >= 20))
                p1.atk_hit = True
                proj.alive = False
                p1.combo_count += 1
                p1.combo_timer = 90
                if p1.combo_count >= 3:
                    play(SND_COMBO)
                    add_text(int(p1.x + p1.w // 2), int(p1.y - 50), f"{p1.combo_count}x COMBO!", GOLD, 38)
        elif proj.owner == p2 and not p2.atk_hit:
            if proj.get_rect().colliderect(p1.get_body_rect()):
                p1.take_damage(proj.dmg, p2, is_super=(proj.size >= 20))
                p2.atk_hit = True
                proj.alive = False
                p2.combo_count += 1
                p2.combo_timer = 90
                if p2.combo_count >= 3:
                    play(SND_COMBO)
                    add_text(int(p2.x + p2.w // 2), int(p2.y - 50), f"{p2.combo_count}x COMBO!", ORANGE, 38)

    # Ataques cuerpo a cuerpo
    a1 = p1.get_attack_rect()
    b2 = p2.get_body_rect()
    if a1 and a1.colliderect(b2) and not p1.atk_hit:
        dmg = p1.PUNCH_DMG if p1.atk_type == AttackType.PUNCH else p1.KICK_DMG
        p2.take_damage(dmg, p1)
        p1.atk_hit = True
        p1.combo_count += 1
        p1.combo_timer = 90
        if p1.combo_count >= 3:
            play(SND_COMBO)
            add_text(int(p1.x + p1.w // 2), int(p1.y - 50), f"{p1.combo_count}x COMBO!", GOLD, 38)

    a2 = p2.get_attack_rect()
    b1 = p1.get_body_rect()
    if a2 and a2.colliderect(b1) and not p2.atk_hit:
        dmg = p2.PUNCH_DMG if p2.atk_type == AttackType.PUNCH else p2.KICK_DMG
        p1.take_damage(dmg, p2)
        p2.atk_hit = True
        p2.combo_count += 1
        p2.combo_timer = 90
        if p2.combo_count >= 3:
            play(SND_COMBO)
            add_text(int(p2.x + p2.w // 2), int(p2.y - 50), f"{p2.combo_count}x COMBO!", ORANGE, 38)


# ══════════════════════════════════════════════════════════════════════════
# CREACIÓN DE JUGADORES
# ══════════════════════════════════════════════════════════════════════════
def create_players(mode_2p, char1_key="RYU", char2_key="KEN"):
    c1 = {
        'left': pygame.K_a, 'right': pygame.K_d,
        'jump': pygame.K_w, 'punch': pygame.K_SPACE,
        'kick': pygame.K_LSHIFT, 'block': pygame.K_s,
        'special': pygame.K_e, 'super': pygame.K_q,
    }
    c2_human = {
        'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
        'jump': pygame.K_UP, 'punch': pygame.K_l,
        'kick': pygame.K_SEMICOLON, 'block': pygame.K_DOWN,
        'special': pygame.K_o, 'super': pygame.K_p,
    }
    p1 = Fighter(SCREEN_WIDTH // 4, player_id=1, char_key=char1_key, controls=c1, is_ai=False)
    p2 = Fighter(3 * SCREEN_WIDTH // 4, player_id=2, char_key=char2_key,
                 controls=c2_human if mode_2p else None, is_ai=not mode_2p)
    p1.direction = 1
    p2.direction = -1
    return p1, p2


# ══════════════════════════════════════════════════════════════════════════
# GAME STATE
# ══════════════════════════════════════════════════════════════════════════
class GameState(Enum):
    MENU        = 0
    CHAR_SELECT = 1
    ROUND_START = 2
    PLAYING     = 3
    ROUND_END   = 4
    RESULT      = 5


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    global screen_shake, shake_x, shake_y

    bg = Background()
    state = GameState.MENU
    mode_2p = False
    p1 = p2 = None
    frame_count = 0
    winner_id = None
    menu_frame = 0

    # Selección de personaje
    chars = list(CHARACTERS.keys())
    char_cursor = [0, 0]
    selected_chars = [None, None]
    select_phase = 0  # 0=p1, 1=p2/cpu

    # Rondas (mejor de 3)
    MAX_ROUNDS = 3
    round_num = 1
    p1_wins = 0
    p2_wins = 0
    round_announce_timer = 0
    round_end_timer = 0
    result_frame = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state in (GameState.PLAYING, GameState.CHAR_SELECT, GameState.ROUND_START):
                        state = GameState.MENU
                        particle_list.clear(); spark_list.clear()
                        text_list.clear(); projectile_list.clear()
                    else:
                        running = False

                # MENÚ
                if state == GameState.MENU:
                    if event.key == pygame.K_1:
                        mode_2p = False
                        selected_chars = [None, None]
                        char_cursor = [0, 0]
                        select_phase = 0
                        state = GameState.CHAR_SELECT
                    elif event.key == pygame.K_2:
                        mode_2p = True
                        selected_chars = [None, None]
                        char_cursor = [0, 0]
                        select_phase = 0
                        state = GameState.CHAR_SELECT

                # SELECCIÓN PERSONAJE
                elif state == GameState.CHAR_SELECT:
                    cur_player = select_phase
                    if event.key == pygame.K_LEFT:
                        char_cursor[cur_player] = (char_cursor[cur_player] - 1) % len(chars)
                    elif event.key == pygame.K_RIGHT:
                        char_cursor[cur_player] = (char_cursor[cur_player] + 1) % len(chars)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_l):
                        selected_chars[cur_player] = chars[char_cursor[cur_player]]
                        if cur_player == 0 and mode_2p:
                            select_phase = 1
                        else:
                            # Si cpu, elegir aleatorio
                            if not mode_2p:
                                ai_choices = [k for k in chars if k != selected_chars[0]]
                                selected_chars[1] = random.choice(ai_choices)
                            # Empezar juego
                            p1, p2 = create_players(mode_2p, selected_chars[0], selected_chars[1])
                            particle_list.clear(); spark_list.clear()
                            text_list.clear(); projectile_list.clear()
                            frame_count = 0
                            round_num = 1
                            p1_wins = 0
                            p2_wins = 0
                            round_announce_timer = 60
                            state = GameState.ROUND_START
                            play(SND_ROUND)

                # RESULTADO FINAL
                elif state == GameState.RESULT:
                    if event.key == pygame.K_SPACE:
                        state = GameState.MENU

        # ── Update ────────────────────────────────────────────────────────
        bg.update()
        update_shake()

        if state == GameState.ROUND_START:
            round_announce_timer -= 1
            if round_announce_timer <= 0:
                state = GameState.PLAYING
                frame_count = 0

        elif state == GameState.PLAYING:
            frame_count += 1
            keys = pygame.key.get_pressed()

            if not p1.ko and not p2.ko:
                p1.handle_input(keys, p2)
                if p2.is_ai:
                    p2.handle_ai(p1)
                else:
                    p2.handle_input(keys, p1)
                check_collisions(p1, p2)

            p1.update()
            p2.update()
            update_effects()

            # Orientar hacia rival
            if not p1.ko and not p2.ko:
                if p1.x < p2.x:
                    p1.direction = 1; p2.direction = -1
                else:
                    p1.direction = -1; p2.direction = 1

            # Fin de ronda
            if p1.ko or p2.ko:
                if p1.ko and p2.ko:
                    winner_id = 0
                elif p1.ko:
                    winner_id = 2
                    p2_wins += 1
                else:
                    winner_id = 1
                    p1_wins += 1
                round_end_timer = 90
                state = GameState.ROUND_END

        elif state == GameState.ROUND_END:
            round_end_timer -= 1
            update_effects()
            if round_end_timer <= 0:
                if p1_wins >= 2 or p2_wins >= 2 or round_num >= MAX_ROUNDS:
                    result_frame = 0
                    state = GameState.RESULT
                else:
                    round_num += 1
                    p1, p2 = create_players(mode_2p, selected_chars[0], selected_chars[1])
                    particle_list.clear(); spark_list.clear()
                    text_list.clear(); projectile_list.clear()
                    frame_count = 0
                    round_announce_timer = 60
                    state = GameState.ROUND_START
                    play(SND_ROUND)

        elif state == GameState.RESULT:
            result_frame += 1

        elif state == GameState.MENU:
            menu_frame += 1

        # ── Draw ──────────────────────────────────────────────────────────
        draw_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        if state == GameState.MENU:
            draw_menu(draw_surf, bg, menu_frame)

        elif state == GameState.CHAR_SELECT:
            cur_player = select_phase
            for_label = 1 if cur_player == 0 else (2 if mode_2p else 0)
            draw_char_select(draw_surf, bg, menu_frame, for_label, selected_chars, char_cursor[cur_player])
            menu_frame += 1

        elif state in (GameState.ROUND_START,):
            bg.draw(draw_surf)
            if p1 and p2:
                p1.draw(draw_surf)
                p2.draw(draw_surf)
                draw_effects(draw_surf)
                draw_hud(draw_surf, p1, p2, 0, mode_2p, round_num, p1_wins, p2_wins)
            draw_round_announce(draw_surf, round_num, round_announce_timer)

        elif state == GameState.PLAYING:
            bg.draw(draw_surf)
            p1.draw(draw_surf)
            p2.draw(draw_surf)
            draw_effects(draw_surf)
            draw_hud(draw_surf, p1, p2, frame_count, mode_2p, round_num, p1_wins, p2_wins)

        elif state == GameState.ROUND_END:
            bg.draw(draw_surf)
            p1.draw(draw_surf)
            p2.draw(draw_surf)
            draw_effects(draw_surf)
            draw_hud(draw_surf, p1, p2, frame_count, mode_2p, round_num, p1_wins, p2_wins)
            # Texto de fin de ronda
            if winner_id == 0:
                wt = font_lg.render("¡EMPATE!", True, YELLOW)
            elif winner_id == 1:
                wt = font_lg.render(f"¡{CHARACTERS[selected_chars[0]]['display']} GANA!", True, CHARACTERS[selected_chars[0]]["color"])
            else:
                wt = font_lg.render(f"¡{CHARACTERS[selected_chars[1]]['display']} GANA!", True, CHARACTERS[selected_chars[1]]["color"])
            draw_surf.blit(wt, (SCREEN_WIDTH // 2 - wt.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        elif state == GameState.RESULT:
            final_winner = 1 if p1_wins > p2_wins else (2 if p2_wins > p1_wins else 0)
            draw_result_screen(draw_surf, bg, final_winner, mode_2p, p1_wins, p2_wins,
                               selected_chars[0] or "RYU", selected_chars[1] or "KEN", result_frame)

        # Aplicar screen shake
        screen.blit(draw_surf, (shake_x, shake_y))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
