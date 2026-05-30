"""
Mini Street Fighter - VERSIÓN SUPREMA v2.0
Mejoras: física corregida, IA más inteligente, animaciones fluidas,
colisiones mejoradas, efectos visuales, rendimiento optimizado.
"""

import pygame
import sys
import random
import math
from enum import Enum

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 680
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Street Fighter - Versión Suprema v2.0")
clock = pygame.time.Clock()

# ── Colores ───────────────────────────────────────────────────────────────
BLACK       = (0,0,0);       WHITE    = (255,255,255); RED     = (220,40,40)
GREEN       = (40,200,80);   BLUE     = (40,100,220);  YELLOW  = (255,210,0)
ORANGE      = (255,140,0);   CYAN     = (0,200,220);   GOLD    = (255,195,0)
PURPLE      = (150,50,220);  PINK     = (255,80,160);  LIME    = (100,255,60)
SKIN        = (210,160,110); SKIN_DARK= (170,110,70);  SKIN_SHADOW=(140,90,55)
HAIR_BLACK  = (20,15,10);    GI_WHITE = (230,230,240); GI_SHADOW=(180,180,200)
BELT_RED    = (200,30,30);   BELT_YELLOW=(220,180,0);  BELT_BLACK=(20,20,25)
PANTS_BLUE  = (40,60,160);   PANTS_RED = (160,30,30)

FLOOR_Y = SCREEN_HEIGHT - 130

# ── Audio (generado proceduralmente) ─────────────────────────────────────
SOUND_ON = False
SND = {}

def _make_sound(freq, ms, wave="sq", vol=0.35):
    try:
        import numpy as np
        sr = 44100; n = int(sr * ms / 1000)
        t = np.linspace(0, ms/1000, n, False)
        if wave == "sq":   w = np.sign(np.sin(2*np.pi*freq*t))
        elif wave == "no": w = np.random.uniform(-1, 1, n)
        elif wave == "sw": w = np.sin(2*np.pi*np.linspace(freq, freq*2.5, n)*t)
        else:              w = np.sin(2*np.pi*freq*t)
        env = np.linspace(1, 0, n)
        w = w * env * vol
        a = np.int16(np.clip(w, -1, 1) * 32767)
        return pygame.sndarray.make_sound(np.column_stack((a, a)))
    except:
        return None

try:
    SND = {
        "punch":   _make_sound(200, 70,  "sq",  0.4),
        "kick":    _make_sound(130, 90,  "sq",  0.5),
        "jump":    _make_sound(480, 55,  "si",  0.2),
        "hit":     _make_sound(90,  110, "no",  0.55),
        "ko":      _make_sound(65,  500, "sq",  0.7),
        "combo":   _make_sound(700, 110, "si",  0.3),
        "special": _make_sound(320, 190, "sw",  0.5),
        "super":   _make_sound(110, 380, "sq",  0.8),
        "block":   _make_sound(210, 55,  "sq",  0.3),
        "round":   _make_sound(540, 280, "si",  0.5),
    }
    SOUND_ON = True
except:
    pass

def play(k):
    if SOUND_ON and k in SND and SND[k]:
        try:
            SND[k].play()
        except:
            pass

# ── Fuentes ───────────────────────────────────────────────────────────────
fXL = pygame.font.Font(None, 100)
fLG = pygame.font.Font(None, 72)
fMD = pygame.font.Font(None, 48)
fSM = pygame.font.Font(None, 32)
fXS = pygame.font.Font(None, 24)
fTN = pygame.font.Font(None, 20)

# ── Personajes ────────────────────────────────────────────────────────────
CHARACTERS = {
    "RYU": {
        "display": "RYU", "desc": "Guerrero equilibrado",
        "body": GI_WHITE, "body_dark": GI_SHADOW,
        "pants": PANTS_BLUE, "belt": (220,60,60),
        "hair": HAIR_BLACK, "hair_style": "headband_red",
        "skin": SKIN, "accent": (220,60,60),
        "special_color": (80,160,255), "super_color": (150,220,255),
        "hp":180, "speed":5.0, "punch":18, "kick":26, "special":42, "super":85,
        "jump":17, "special_name":"HADOUKEN", "super_name":"SHORYUKEN",
    },
    "KEN": {
        "display": "KEN", "desc": "Rápido y explosivo",
        "body": GI_WHITE, "body_dark": GI_SHADOW,
        "pants": PANTS_RED, "belt": BELT_YELLOW,
        "hair": (200,130,30), "hair_style": "wild",
        "skin": SKIN, "accent": ORANGE,
        "special_color": (255,140,60), "super_color": (255,220,60),
        "hp":160, "speed":6.2, "punch":22, "kick":28, "special":46, "super":92,
        "jump":18, "special_name":"HADOUKEN", "super_name":"DRAGON PUNCH",
    },
    "CHUN": {
        "display": "CHUN-LI", "desc": "Velocidad máxima",
        "body": (80,120,220), "body_dark": (50,80,160),
        "pants": (80,120,220), "belt": BELT_YELLOW,
        "hair": HAIR_BLACK, "hair_style": "buns",
        "skin": (220,175,130), "accent": YELLOW,
        "special_color": (150,230,255), "super_color": (255,255,80),
        "hp":150, "speed":7.2, "punch":15, "kick":34, "special":38, "super":78,
        "jump":20, "special_name":"KIKOKEN", "super_name":"SPINNING BIRD",
    },
    "ZANGIEF": {
        "display": "ZANGIEF", "desc": "Tanque destructor",
        "body": (80,30,30), "body_dark": (50,15,15),
        "pants": (60,40,120), "belt": BELT_RED,
        "hair": (180,50,50), "hair_style": "mohawk",
        "skin": (180,120,90), "accent": RED,
        "special_color": (220,80,80), "super_color": (255,120,60),
        "hp":230, "speed":3.8, "punch":30, "kick":40, "special":58, "super":105,
        "jump":13, "special_name":"LARIAT", "super_name":"FINAL ATOMIC",
    },
}

# ══════════════════════════════════════════════════════════════════════════
# EFECTOS
# ══════════════════════════════════════════════════════════════════════════
class Particle:
    __slots__ = ['x','y','vx','vy','color','life','max_life','size']
    def __init__(self, x, y, color, vx, vy, life=30, size=4):
        self.x=float(x); self.y=float(y); self.color=color
        self.vx=vx; self.vy=vy; self.life=self.max_life=life; self.size=size

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.28; self.vx *= 0.94; self.life -= 1

    def draw(self, s):
        r = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), r)

class HitSpark:
    def __init__(self, x, y, color, big=False):
        self.x=x; self.y=y; self.color=color
        self.life = self.max_life = 20 if big else 14
        n = 14 if big else 9
        self.rays = [(random.uniform(0, 2*math.pi),
                      random.uniform(10 if big else 7, 32 if big else 22)) for _ in range(n)]
        self.big = big

    def update(self): self.life -= 1

    def draw(self, s):
        if self.life <= 0: return
        p = self.life / self.max_life
        for ang, l in self.rays:
            ex = self.x + math.cos(ang)*l*p
            ey = self.y + math.sin(ang)*l*p
            pygame.draw.line(s, tuple(int(v*p) for v in self.color),
                             (int(self.x), int(self.y)), (int(ex), int(ey)),
                             3 if self.big else 2)
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)),
                           int((12 if self.big else 7)*p))

class Projectile:
    def __init__(self, x, y, dir_, owner, dmg, color, size=14, spd=10):
        self.x=float(x); self.y=float(y); self.dir=dir_; self.owner=owner
        self.dmg=dmg; self.color=color; self.size=size
        self.spd=spd*dir_; self.alive=True; self.frame=0

    def update(self):
        self.x += self.spd; self.frame += 1
        if self.x < -80 or self.x > SCREEN_WIDTH+80:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(int(self.x)-self.size, int(self.y)-self.size,
                           self.size*2, self.size*2)

    def draw(self, s):
        p = abs(math.sin(self.frame*0.35))*3
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), int(self.size+p))
        pygame.draw.circle(s, WHITE, (int(self.x), int(self.y)), self.size//2)
        for i in range(4):
            pygame.draw.circle(s, tuple(v//(i+2) for v in self.color),
                               (int(self.x), int(self.y)), self.size+4+i*5, 1)
        # Estela de energía
        for i in range(1, 5):
            tx = int(self.x - self.dir*i*6)
            tc = tuple(int(v*(1-i/5)*0.5) for v in self.color)
            pygame.draw.circle(s, tc, (tx, int(self.y)), max(2, self.size-i*2))

class FloatingText:
    def __init__(self, x, y, text, color, size=32):
        self.x=float(x); self.y=float(y); self.text=text; self.color=color
        self.life=65; self.font=pygame.font.Font(None, size)

    def update(self): self.y -= 1.4; self.life -= 1

    def draw(self, s):
        t = self.font.render(self.text, True, self.color)
        ts = self.font.render(self.text, True, BLACK)
        s.blit(ts, (int(self.x)-t.get_width()//2+2, int(self.y)+2))
        s.blit(t,  (int(self.x)-t.get_width()//2,   int(self.y)))

# Listas globales de efectos
particles  = []
sparks     = []
texts      = []
projectiles = []
screen_shake = 0
shake_x = shake_y = 0

def emit_particles(x, y, color, n=12, sp=4):
    for _ in range(n):
        particles.append(Particle(x, y, color,
            random.uniform(-sp, sp), random.uniform(-sp, 0),
            life=random.randint(22, 48), size=random.randint(2, 6)))

def emit_hit(x, y, color, big=False):
    sparks.append(HitSpark(x, y, color, big))
    emit_particles(x, y, color, 20 if big else 14, 6 if big else 4)

def add_text(x, y, text, color, sz=32):
    texts.append(FloatingText(x, y, text, color, sz))

def do_shake(dur=12):
    global screen_shake
    screen_shake = max(screen_shake, dur)

def update_effects():
    global screen_shake, shake_x, shake_y
    for item in particles[:]:
        item.update()
        if item.life <= 0: particles.remove(item)
    for item in sparks[:]:
        item.update()
        if item.life <= 0: sparks.remove(item)
    for item in texts[:]:
        item.update()
        if item.life <= 0: texts.remove(item)
    for item in projectiles[:]:
        item.update()
        if not item.alive: projectiles.remove(item)
    if screen_shake > 0:
        screen_shake -= 1
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-4, 4)
    else:
        shake_x = shake_y = 0

def draw_effects(s):
    for obj in projectiles: obj.draw(s)
    for obj in particles:   obj.draw(s)
    for obj in sparks:      obj.draw(s)
    for obj in texts:       obj.draw(s)

# ══════════════════════════════════════════════════════════════════════════
# FONDO ARCADE
# ══════════════════════════════════════════════════════════════════════════
class Background:
    def __init__(self):
        self.frame = 0
        rng = random.Random(42)
        # Edificios
        self.buildings = []
        x = 0
        while x < SCREEN_WIDTH:
            w = rng.randint(55, 110); h = rng.randint(90, 210)
            wc = rng.randint(2, 5);   wr = rng.randint(3, 9)
            lit = [[rng.random() > 0.35 for _ in range(wc)] for _ in range(wr)]
            self.buildings.append((x, SCREEN_HEIGHT-130-h, w, h, wc, wr, lit))
            x += w + rng.randint(0, 8)
        # Multitud
        self.crowd = []
        crowd_y = SCREEN_HEIGHT - 130
        for _ in range(60):
            cx_ = rng.randint(20, SCREEN_WIDTH-20)
            cy_ = crowd_y - rng.randint(10, 50)
            r   = rng.randint(8, 14)
            skin_colors    = [(210,150,90),(180,110,60),(240,200,160),(140,80,50),(220,180,140)]
            clothes_colors = [(200,30,30),(30,80,180),(50,150,50),(150,30,150),(180,120,30),(30,30,30)]
            self.crowd.append((cx_, cy_, r,
                               rng.choice(skin_colors), rng.choice(clothes_colors),
                               rng.uniform(0, 2*math.pi)))
        # Neones
        self.neons = [
            {"x":180,  "y":SCREEN_HEIGHT-270, "text":"FIGHT!",  "color":(255,40,100),  "ph":0.0},
            {"x":880,  "y":SCREEN_HEIGHT-290, "text":"BAR",     "color":(40,200,255),  "ph":1.6},
            {"x":540,  "y":SCREEN_HEIGHT-310, "text":"ARCADE",  "color":(180,40,255),  "ph":3.1},
        ]
        # Antorchas
        self.torches = [
            {"x": SCREEN_WIDTH//4,    "y": FLOOR_Y-40},
            {"x": SCREEN_WIDTH//2,    "y": FLOOR_Y-60},
            {"x": 3*SCREEN_WIDTH//4,  "y": FLOOR_Y-40},
        ]
        # Pre-render cielo (no cambia)
        self._sky_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT-130))
        for y in range(SCREEN_HEIGHT-130):
            t = y / (SCREEN_HEIGHT-130)
            self._sky_surf.fill((int(8+t*6), int(4+t*9), int(28+t*22)),
                                (0, y, SCREEN_WIDTH, 1))

    def update(self):
        self.frame += 1

    def draw(self, s):
        f = self.frame
        # Cielo
        s.blit(self._sky_surf, (0, 0))

        # Luna
        pygame.draw.circle(s, (225,225,185), (SCREEN_WIDTH-140, 65), 38)
        pygame.draw.circle(s, (12,8,28),     (SCREEN_WIDTH-126, 57), 34)

        # Estrellas (semilla fija, rápido)
        rng2 = random.Random(99)
        for _ in range(70):
            sx = rng2.randint(0, SCREEN_WIDTH)
            sy = rng2.randint(0, SCREEN_HEIGHT-160)
            br = int(160 + 95*math.sin(f*0.025 + rng2.uniform(0, 6)))
            pygame.draw.circle(s, (br, br, br), (sx, sy), rng2.randint(1, 2))

        # Edificios
        for bx, by, bw, bh, wc, wr, lit in self.buildings:
            pygame.draw.rect(s, (6,5,12),   (bx+5, by+5, bw, bh))
            pygame.draw.rect(s, (22,18,42), (bx,   by,   bw, bh))
            pw = bw // (wc+1); ph = bh // (wr+1)
            for row in range(wr):
                for col in range(wc):
                    wx_ = bx + pw*(col+1) - 4
                    wy_ = by + ph*(row+1) - 5
                    if lit[row][col]:
                        flk = (f//80 + row*wc + col) % 22 == 0
                        c = (195,175,75) if not flk else (55,45,18)
                    else:
                        c = (12,10,22)
                    pygame.draw.rect(s, c, (wx_, wy_, 8, 10))

        # Neones
        for n in self.neons:
            glow = abs(math.sin(f*0.05 + n["ph"]))
            r_, g_, b_ = n["color"]
            c_ = (int(r_*(0.3+0.7*glow)), int(g_*(0.3+0.7*glow)), int(b_*(0.3+0.7*glow)))
            t_ = fXS.render(n["text"], True, c_)
            s.blit(t_, (n["x"] - t_.get_width()//2, n["y"]))

        # Suelo
        floor_y = FLOOR_Y
        pygame.draw.rect(s, (65,50,35), (0, floor_y, SCREEN_WIDTH, 130))
        for i in range(0, SCREEN_WIDTH, 60):
            pygame.draw.line(s, (80,62,45), (i, floor_y), (i, floor_y+130), 1)
        pygame.draw.line(s, (90,72,52), (0, floor_y), (SCREEN_WIDTH, floor_y), 3)
        for i in range(0, SCREEN_WIDTH, 90):
            pygame.draw.line(s, (75,58,40), (i, floor_y), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 1)

        # Valla
        rail_y = floor_y - 18
        pygame.draw.rect(s, (45,35,25), (0, rail_y, SCREEN_WIDTH, 6))
        for px in range(0, SCREEN_WIDTH, 22):
            pygame.draw.rect(s, (55,42,30), (px, rail_y-30, 5, 36))

        # Multitud
        for cx_, cy_, r_, skin_, clothes_, ph_ in self.crowd:
            bob_ = int(math.sin(f*0.08 + ph_)*3)
            pygame.draw.circle(s, clothes_, (cx_, cy_+r_+bob_), r_+4)
            pygame.draw.circle(s, skin_,    (cx_, cy_+bob_),    r_)
            if math.sin(f*0.1 + ph_) > 0.7:
                pygame.draw.ellipse(s, (60,20,20), (cx_-3, cy_+3+bob_, 6, 5))

        # Antorchas
        for tor in self.torches:
            tx, ty = tor["x"], tor["y"]
            pygame.draw.rect(s, (80,55,30), (tx-3, ty, 6, 35))
            for fi in range(6):
                fa = f*0.18 + fi*1.0
                fx_ = tx + int(math.sin(fa)*5)
                fy_ = ty - fi*5
                fr_ = max(1, 8-fi)
                fc_g = max(0, 180-fi*30)
                pygame.draw.circle(s, (255, fc_g, 0), (fx_, fy_), fr_)

        # Reflejos neón en el suelo
        neon_colors = [(255,40,100),(40,200,255),(180,40,255),(255,160,0)]
        for i, (r_, g_, b_) in enumerate(neon_colors):
            x_ = SCREEN_WIDTH // (len(neon_colors)+1) * (i+1)
            gw = abs(math.sin(f*0.04 + i))
            for step in range(4):
                lw = max(1, 4-step)
                pygame.draw.line(s,
                    (int(r_*gw//(step+2)), int(g_*gw//(step+2)), int(b_*gw//(step+2))),
                    (x_-25+step, floor_y+4+step),
                    (x_+25-step, floor_y+4+step), lw)


# ══════════════════════════════════════════════════════════════════════════
# DIBUJAR PERSONAJE DETALLADO
# ══════════════════════════════════════════════════════════════════════════
class AttackType(Enum):
    NONE=0; PUNCH=1; KICK=2; SPECIAL=3; SUPER=4

class FighterState(Enum):
    IDLE=0; WALK=1; JUMP=2; ATTACK=3; HIT=4; KO=5; BLOCK=6; SPECIAL=7; SUPER=8


def draw_fighter_sprite(surf, fighter, ix, iy, flash=False):
    ch  = fighter.char
    cx  = ix + fighter.w // 2

    skin_c  = WHITE if flash else ch["skin"]
    body_c  = WHITE if flash else ch["body"]
    body_dk = WHITE if flash else ch["body_dark"]
    pants_c = WHITE if flash else ch["pants"]
    hair_c  = WHITE if flash else ch["hair"]
    belt_c  = WHITE if flash else ch.get("belt", (200,60,60))

    w  = fighter.w
    h  = fighter.h
    is_zangief = (fighter.char_key == "ZANGIEF")
    w_scale = 1.3 if is_zangief else 1.0
    ww = int(w * w_scale)

    state    = fighter.state
    walk_c   = fighter.walk_cycle
    atk      = fighter.atk_type
    anim     = fighter.anim_frame

    # Posiciones base
    head_cy   = iy + int(h * 0.11)
    head_r    = int(w * 0.44) + (3 if is_zangief else 0)
    torso_top = iy + int(h * 0.20)
    torso_bot = iy + int(h * 0.58)
    torso_w   = int(ww * 0.88)
    torso_h   = torso_bot - torso_top
    waist_y   = torso_bot
    hip_top   = waist_y
    hip_bot   = iy + int(h * 0.70)
    leg_top   = hip_bot
    leg_bot   = iy + h
    leg_w     = int(ww * 0.32)
    leg_gap   = int(ww * 0.06)
    foot_h    = int(h * 0.06)

    bob      = int(math.sin(walk_c) * 3) if state == FighterState.WALK else 0
    leg_l_off = int(math.sin(walk_c) * 8)        if state == FighterState.WALK else 0
    leg_r_off = int(math.sin(walk_c + math.pi)*8) if state == FighterState.WALK else 0

    # Pose de bloqueo: ligero agachado
    if fighter.blocking:
        bob = 6
        leg_l_off = leg_r_off = 4

    lx = cx - leg_gap//2 - leg_w
    rx = cx + leg_gap//2

    # ── PIERNAS ───────────────────────────────────────────────────────────
    pygame.draw.rect(surf, pants_c,
                     (lx, leg_top+leg_l_off, leg_w, (leg_bot-leg_top)-leg_l_off),
                     border_radius=4)
    pygame.draw.rect(surf, pants_c,
                     (rx, leg_top+leg_r_off, leg_w, (leg_bot-leg_top)-leg_r_off),
                     border_radius=4)
    shade_pants = tuple(max(0, v-40) for v in pants_c)
    pygame.draw.rect(surf, shade_pants, (lx, leg_top+leg_l_off, leg_w, 8), border_radius=4)
    pygame.draw.rect(surf, shade_pants, (rx, leg_top+leg_r_off, leg_w, 8), border_radius=4)

    foot_c = (50,40,35)
    pygame.draw.ellipse(surf, foot_c,
        (lx-3, leg_bot-foot_h+leg_l_off, leg_w+6, foot_h+4))
    pygame.draw.ellipse(surf, foot_c,
        (rx-3+8*fighter.direction, leg_bot-foot_h+leg_r_off, leg_w+6, foot_h+4))

    # ── CADERA ────────────────────────────────────────────────────────────
    pygame.draw.rect(surf, body_c,
                     (cx-ww//2+2, hip_top+bob, ww-4, hip_bot-hip_top), border_radius=3)

    # ── CINTURÓN ──────────────────────────────────────────────────────────
    belt_y = waist_y + bob - 3
    belt_h = int(h * 0.05)
    pygame.draw.rect(surf, belt_c, (cx-ww//2+2, belt_y, ww-4, belt_h))
    buckle_c = GOLD if belt_c != BELT_YELLOW else WHITE
    pygame.draw.rect(surf, buckle_c, (cx-6, belt_y+1, 12, belt_h-2), border_radius=2)

    # ── TORSO ─────────────────────────────────────────────────────────────
    pygame.draw.rect(surf, body_c,
                     (cx-ww//2, torso_top+bob, ww, torso_h), border_radius=5)
    for fx in [cx-ww//4, cx, cx+ww//4]:
        pygame.draw.line(surf, body_dk,
                         (cx, torso_top+bob), (fx, torso_bot+bob), 1)
    pygame.draw.polygon(surf, skin_c, [
        (cx,           torso_top+6+bob),
        (cx-int(ww*0.18), torso_top+int(torso_h*0.5)+bob),
        (cx+int(ww*0.18), torso_top+int(torso_h*0.5)+bob),
    ])
    pygame.draw.rect(surf, body_dk,
                     (cx-ww//2, torso_top+bob, 6, torso_h), border_radius=5)
    pygame.draw.rect(surf, body_dk,
                     (cx+ww//2-6, torso_top+bob, 6, torso_h), border_radius=5)

    # ── BRAZOS ────────────────────────────────────────────────────────────
    arm_top  = torso_top + int(torso_h * 0.08) + bob
    arm_h    = int(torso_h * 0.65)
    arm_w    = int(ww * 0.22)
    forearm_w = int(arm_w * 0.85)

    if state in (FighterState.ATTACK, FighterState.SPECIAL, FighterState.SUPER) and \
       atk != AttackType.NONE:
        _draw_attack_arm(surf, fighter, cx, arm_top, arm_h, arm_w,
                         skin_c, body_c, belt_c, flash, is_zangief, ww)
    else:
        swing = int(math.sin(walk_c) * 5) if state == FighterState.WALK else 0
        # Brazo izquierdo
        larm_x = cx - ww//2 - arm_w + 4
        pygame.draw.rect(surf, body_c,
                         (larm_x, arm_top+swing, arm_w, arm_h//2), border_radius=4)
        pygame.draw.rect(surf, skin_c,
                         (larm_x+2, arm_top+arm_h//2+swing, forearm_w, arm_h//2-4), border_radius=4)
        # Brazo derecho
        rarm_x = cx + ww//2 - 4
        pygame.draw.rect(surf, body_c,
                         (rarm_x, arm_top-swing, arm_w, arm_h//2), border_radius=4)
        pygame.draw.rect(surf, skin_c,
                         (rarm_x+2, arm_top+arm_h//2-swing, forearm_w, arm_h//2-4), border_radius=4)
        # Manos
        pygame.draw.circle(surf, skin_c, (larm_x+forearm_w//2, arm_top+arm_h-4+swing), 6)
        pygame.draw.circle(surf, skin_c, (rarm_x+forearm_w//2, arm_top+arm_h-4-swing), 6)

    # ── CUELLO ────────────────────────────────────────────────────────────
    neck_w = int(ww * 0.22); neck_h = int(h * 0.07)
    pygame.draw.rect(surf, skin_c,
                     (cx-neck_w//2, torso_top-neck_h+bob, neck_w, neck_h+3), border_radius=2)

    # ── CABEZA ────────────────────────────────────────────────────────────
    head_y = head_cy + bob
    pygame.draw.circle(surf, skin_c, (cx, head_y), head_r)
    jaw_pts = [
        (cx-head_r+3,            head_y),
        (cx-head_r+2,            head_y+int(head_r*0.6)),
        (cx-int(head_r*0.55),    head_y+head_r+2),
        (cx+int(head_r*0.55),    head_y+head_r+2),
        (cx+head_r-2,            head_y+int(head_r*0.6)),
        (cx+head_r-3,            head_y),
    ]
    pygame.draw.polygon(surf, skin_c, jaw_pts)
    pygame.draw.line(surf, SKIN_SHADOW,
                     (cx-int(head_r*0.55), head_y+head_r+2),
                     (cx+int(head_r*0.55), head_y+head_r+2), 2)

    # Ojos / cejas
    eye_y   = head_y - int(head_r * 0.1)
    eye_off = int(head_r * 0.38)
    brow_y  = eye_y - int(head_r * 0.35)
    angle_sign = 1 if fighter.direction > 0 else -1
    for side in [-1, 1]:
        ex = cx + side * eye_off
        pygame.draw.line(surf, hair_c if not flash else WHITE,
                         (ex-6, brow_y+side*angle_sign*2),
                         (ex+6, brow_y-side*angle_sign*2), 3)
    for side in [-1, 1]:
        ex = cx + side * eye_off
        pygame.draw.ellipse(surf, WHITE, (ex-6, eye_y-4, 12, 9))
        iris_off = 2 * fighter.direction
        pygame.draw.ellipse(surf, (40,60,160), (ex-3+iris_off, eye_y-3, 6, 7))
        pygame.draw.circle(surf, BLACK, (ex+iris_off, eye_y), 2)
        pygame.draw.circle(surf, WHITE, (ex+iris_off+1, eye_y-1), 1)

    mouth_y = head_y + int(head_r * 0.45)
    if state == FighterState.HIT:
        pygame.draw.ellipse(surf, (100,30,30), (cx-6, mouth_y-3, 12, 8))
    elif state in (FighterState.ATTACK, FighterState.SUPER):
        pygame.draw.arc(surf, SKIN_SHADOW, (cx-8, mouth_y-4, 16, 8), 0, math.pi, 2)
    else:
        pygame.draw.line(surf, SKIN_SHADOW, (cx-6, mouth_y), (cx+6, mouth_y), 2)

    # Nariz
    pygame.draw.circle(surf, SKIN_SHADOW, (cx, head_y+int(head_r*0.18)), 2)

    # ── PELO ──────────────────────────────────────────────────────────────
    _draw_hair(surf, fighter, cx, head_y, head_r, hair_c, flash)

    # ── Aura de super ─────────────────────────────────────────────────────
    if fighter.super_meter >= 50:
        alpha_r = (fighter.super_meter - 50) / 50.0
        pulse   = abs(math.sin(anim * 0.12)) * 8
        aura_c  = ch["super_color"]
        for rr in [25, 38, 52]:
            c_ = tuple(int(v * alpha_r * 0.35) for v in aura_c)
            if any(v > 0 for v in c_):
                pygame.draw.circle(surf, c_, (cx, iy+h//2), rr+int(pulse), 2)

    # ── Escudo visual ─────────────────────────────────────────────────────
    if fighter.blocking:
        sx = cx + fighter.direction * (ww//2 + 4)
        sh = int(h * 0.7)
        sy = torso_top - 10
        for bi in range(4):
            ba = 200 - bi*40
            pygame.draw.rect(surf,
                (0, int(180*ba/200), int(220*ba/200)),
                (sx-6+bi, sy+bi, 12-bi*2, sh-bi*2), border_radius=4)

    # Nombre
    name_surf = fTN.render(ch["display"], True, ch["accent"])
    surf.blit(name_surf, (cx-name_surf.get_width()//2, iy-26))


def _draw_attack_arm(surf, fighter, cx, arm_top, arm_h, arm_w,
                     skin_c, body_c, belt_c, flash, is_zangief, ww):
    ch   = fighter.char
    atk  = fighter.atk_type
    anim = fighter.anim_frame
    dir_ = fighter.direction

    if atk == AttackType.PUNCH:
        max_t = 14; rng_ = 70; arm_y_ratio = 0.35
        arm_color_end = skin_c
    elif atk == AttackType.KICK:
        max_t = 18; rng_ = 95; arm_y_ratio = 0.65
        arm_color_end = skin_c
    elif atk == AttackType.SPECIAL:
        max_t = 25; rng_ = 55; arm_y_ratio = 0.3
        arm_color_end = ch["special_color"] if not flash else WHITE
    else:  # SUPER
        max_t = 50; rng_ = 70; arm_y_ratio = 0.3
        arm_color_end = ch["super_color"] if not flash else WHITE

    progress = max(0.1, 1 - fighter.atk_timer / max_t)
    ext = int(rng_ * min(1, progress * 1.8))
    arm_start_y = int(arm_top + arm_h * arm_y_ratio)

    if atk == AttackType.KICK:
        kick_ext = ext
        knee_x = cx + dir_ * kick_ext//2
        knee_y = arm_start_y - 15
        foot_x = cx + dir_ * kick_ext
        foot_y = arm_start_y + 10
        pygame.draw.line(surf, fighter.char["pants"],
                         (cx, arm_start_y), (knee_x, knee_y), 10)
        pygame.draw.line(surf, fighter.char["pants"],
                         (knee_x, knee_y), (foot_x, foot_y), 8)
        pygame.draw.ellipse(surf, (50,40,35),
                            (foot_x-10, foot_y-5, 20, 10))
        if progress > 0.6:
            ec = (255, 180, 40)
            pygame.draw.circle(surf, ec, (foot_x, foot_y), 12, 2)
            pygame.draw.circle(surf, ec, (foot_x, foot_y), 18, 1)
    else:
        arm_end_x = cx + dir_ * ext
        arm_end_y = arm_start_y
        pygame.draw.line(surf, body_c,
                         (cx+dir_*int(ww*0.44), arm_start_y),
                         (cx+dir_*(ext//2+5), arm_start_y), arm_w)
        pygame.draw.line(surf, skin_c,
                         (cx+dir_*(ext//2+5), arm_start_y),
                         (arm_end_x, arm_end_y), int(arm_w*0.85))
        fist_r = 9 if not is_zangief else 12
        pygame.draw.circle(surf, skin_c, (arm_end_x, arm_end_y), fist_r)
        for i in range(3):
            pygame.draw.circle(surf, SKIN_SHADOW,
                               (arm_end_x - dir_*i*3, arm_end_y-3+i*3), 2)

        if atk in (AttackType.SPECIAL, AttackType.SUPER):
            ec = ch["special_color"] if atk == AttackType.SPECIAL else ch["super_color"]
            for ri in range(4):
                rr = int((fist_r+4+ri*5)*progress)
                pygame.draw.circle(surf, ec, (arm_end_x, arm_end_y), rr, 2)
            if anim % 3 == 0:
                for _ in range(3):
                    px_ = arm_end_x + random.randint(-15, 15)
                    py_ = arm_end_y + random.randint(-15, 15)
                    pygame.draw.circle(surf, ec, (px_, py_), random.randint(2, 5))

    # Brazo de reposo opuesto
    idle_side = -dir_
    idle_arm_x = cx + idle_side * int(ww * 0.48)
    pygame.draw.line(surf, body_c,
                     (idle_arm_x, arm_top),
                     (idle_arm_x+idle_side*6, arm_top+arm_h//2), arm_w)
    pygame.draw.line(surf, skin_c,
                     (idle_arm_x+idle_side*6, arm_top+arm_h//2),
                     (idle_arm_x+idle_side*4, arm_top+arm_h-4), int(arm_w*0.85))


def _draw_hair(surf, fighter, cx, head_cy, head_r, hair_c, flash):
    style = fighter.char.get("hair_style", "headband_red")
    hc    = hair_c if not flash else WHITE
    anim  = fighter.anim_frame

    if style == "headband_red":
        pts = [
            (cx-head_r+2,           head_cy-int(head_r*0.3)),
            (cx-int(head_r*0.5),    head_cy-head_r-6),
            (cx+int(head_r*0.1),    head_cy-head_r-10),
            (cx+int(head_r*0.7),    head_cy-head_r-4),
            (cx+head_r-2,           head_cy-int(head_r*0.3)),
        ]
        pygame.draw.polygon(surf, hc, pts)
        band_y = head_cy - int(head_r * 0.25)
        pygame.draw.rect(surf, (210,30,30) if not flash else WHITE,
                         (cx-head_r+1, band_y, head_r*2-2, 5))
        pygame.draw.rect(surf, (210,30,30) if not flash else WHITE,
                         (cx+head_r-5, band_y-3, 6, 11), border_radius=2)

    elif style == "wild":
        for i in range(7):
            angle = -math.pi*0.9 + i*math.pi*0.3
            r_end = head_r + 12 + i*3
            bx = cx + int(math.cos(angle)*head_r)
            by = head_cy + int(math.sin(angle)*head_r)
            ex = cx + int(math.cos(angle)*r_end)
            ey = head_cy + int(math.sin(angle)*r_end)
            pygame.draw.line(surf, hc, (bx, by), (ex, ey), 3+(i%2))
        pygame.draw.arc(surf, hc,
                        (cx-head_r-4, head_cy-head_r-8, (head_r+4)*2, head_r+12),
                        0.1, math.pi-0.1, 6)

    elif style == "buns":
        bun_r = int(head_r * 0.42)
        for side in [-1, 1]:
            bun_cx = cx + side*int(head_r*0.88)
            bun_cy = head_cy - int(head_r*0.6)
            pygame.draw.circle(surf, hc, (bun_cx, bun_cy), bun_r)
            pygame.draw.circle(surf, tuple(max(0, v-40) for v in hc),
                               (bun_cx, bun_cy), bun_r, 2)
            pygame.draw.line(surf, GOLD if not flash else WHITE,
                             (bun_cx-bun_r+2, bun_cy), (bun_cx+bun_r-2, bun_cy), 2)
        pygame.draw.arc(surf, hc,
                        (cx-head_r+2, head_cy-head_r-2, (head_r-2)*2, head_r*2),
                        0.2, math.pi-0.2, 5)

    elif style == "mohawk":
        mohawk_pts = [
            (cx-8, head_cy-head_r+2),
            (cx-5, head_cy-head_r-18),
            (cx,   head_cy-head_r-26),
            (cx+5, head_cy-head_r-18),
            (cx+8, head_cy-head_r+2),
        ]
        pygame.draw.polygon(surf, hc, mohawk_pts)
        beard_pts = [
            (cx-head_r+5,          head_cy+int(head_r*0.4)),
            (cx-int(head_r*0.6),   head_cy+head_r+8),
            (cx,                   head_cy+head_r+12),
            (cx+int(head_r*0.6),   head_cy+head_r+8),
            (cx+head_r-5,          head_cy+int(head_r*0.4)),
        ]
        pygame.draw.polygon(surf, hc, beard_pts)
        for side in [-1, 1]:
            ex = cx + side*int(head_r*0.38)
            pygame.draw.rect(surf, hc, (ex-8, head_cy-int(head_r*0.45), 16, 5))


# ══════════════════════════════════════════════════════════════════════════
# FIGHTER
# ══════════════════════════════════════════════════════════════════════════
class Fighter:
    def __init__(self, x, pid=1, char_key="RYU", controls=None, is_ai=False):
        self.player_id = pid
        self.is_ai     = is_ai
        self.char_key  = char_key
        self.char      = CHARACTERS[char_key]
        self.x         = float(x)
        self.y         = float(FLOOR_Y - 115)
        self.w         = 54
        self.h         = 115
        self.controls  = controls or {}

        ch = self.char
        self.max_hp        = ch["hp"]
        self.hp            = self.max_hp
        self.speed         = ch["speed"]
        self.direction     = 1 if pid == 1 else -1
        self.jump_power    = ch["jump"]
        self.PUNCH_DMG     = ch["punch"]
        self.KICK_DMG      = ch["kick"]
        self.SPECIAL_DMG   = ch["special"]
        self.SUPER_DMG     = ch["super"]
        self.PUNCH_RANGE   = 76
        self.KICK_RANGE    = 102

        self.vx            = 0.0
        self.vy            = 0.0
        self.on_ground     = True
        self.atk_type      = AttackType.NONE
        self.atk_cooldown  = 0
        self.atk_timer     = 0
        self.atk_active    = False
        self.atk_hit       = False
        self.state         = FighterState.IDLE
        self.hit_stun      = 0
        self.ko            = False
        self.blocking      = False

        self.super_meter      = 0
        self.SUPER_THRESHOLD  = 50   # disponible desde 50%

        self.special_charge    = 0
        self.SPECIAL_CHARGE_MAX = 40
        self.combo_count       = 0
        self.combo_timer       = 0
        self.anim_frame        = 0
        self.walk_cycle        = 0.0

        # IA
        self.ai_timer          = 0
        self.ai_tactic         = "neutral"
        self.ai_tactic_timer   = 0
        self.ai_aggression     = random.uniform(0.75, 1.0)
        self.ai_memory         = []   # historial de acciones del jugador
        self.ai_reaction_delay = 0    # delay de reacción para hacer la IA más humana

    # ── Input del jugador ─────────────────────────────────────────────────
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
            play("jump")

        if keys[c.get('block', pygame.K_s)] and self.on_ground:
            self.blocking = True
            self.state = FighterState.BLOCK
            self.vx = 0

        # Especial: mantener tecla → cargar → soltar
        if keys[c.get('special', pygame.K_e)]:
            self.special_charge = min(self.special_charge+1, self.SPECIAL_CHARGE_MAX+15)
        else:
            if self.special_charge >= self.SPECIAL_CHARGE_MAX and self.atk_cooldown <= 0:
                self._attack(AttackType.SPECIAL)
            self.special_charge = 0

        if self.atk_cooldown <= 0 and self.special_charge == 0:
            if keys[c.get('punch', pygame.K_SPACE)]:
                self._attack(AttackType.PUNCH)
            elif keys[c.get('kick', pygame.K_LSHIFT)]:
                self._attack(AttackType.KICK)
            elif keys[c.get('super', pygame.K_q)] and \
                 self.super_meter >= self.SUPER_THRESHOLD:
                self._attack(AttackType.SUPER)

        if self.vx == 0 and self.on_ground and not self.blocking and self.atk_timer <= 0:
            self.state = FighterState.IDLE

    # ── IA mejorada ───────────────────────────────────────────────────────
    def handle_ai(self, player):
        if self.ko or self.hit_stun > 0:
            self.vx = 0
            return

        self.ai_timer        -= 1
        self.ai_tactic_timer -= 1
        self.ai_reaction_delay = max(0, self.ai_reaction_delay - 1)
        self.blocking = False

        # Predicción de posición del jugador
        predict_x = player.x + player.vx * 8 if player.vx != 0 else player.x

        # Memoria: registrar estado del jugador
        if player.state == FighterState.JUMP:
            self.ai_memory.append("jump")
        elif player.atk_active:
            self.ai_memory.append("attack")
        elif player.blocking:
            self.ai_memory.append("block")
        else:
            self.ai_memory.append("idle")
        if len(self.ai_memory) > 30:
            self.ai_memory.pop(0)

        jump_freq   = self.ai_memory.count("jump")   / max(1, len(self.ai_memory))
        attack_freq = self.ai_memory.count("attack") / max(1, len(self.ai_memory))

        # Cambiar táctica según estado del combate
        if self.ai_tactic_timer <= 0:
            hp_ratio  = self.hp / self.max_hp
            opp_ratio = player.hp / player.max_hp
            r = random.random()
            if hp_ratio < 0.20:
                self.ai_tactic = "desperate"
            elif opp_ratio < 0.25:
                self.ai_tactic = "finish"
            elif hp_ratio > opp_ratio + 0.3 and r < 0.4:
                self.ai_tactic = "pressure"
            elif r < 0.30: self.ai_tactic = "aggressive"
            elif r < 0.50: self.ai_tactic = "poke"
            elif r < 0.65: self.ai_tactic = "defensive"
            else:           self.ai_tactic = "neutral"
            self.ai_tactic_timer = random.randint(50, 160)

        # Reacción con delay para ser más humana
        if self.ai_timer > 0:
            return
        self.ai_timer = random.randint(2, 5)

        dist     = player.x - self.x
        abs_dist = abs(dist)
        self.direction = 1 if dist > 0 else -1

        # ── Respuesta a proyectiles ───────────────────────────────────────
        for proj in projectiles:
            if proj.owner == player:
                proj_dist = abs(proj.x - self.x)
                if 0 < proj_dist < 220:
                    # Saltar si hay tiempo
                    if proj_dist > 80 and self.on_ground and random.random() < 0.60:
                        self.vy = -self.jump_power
                        self.on_ground = False
                        self.state = FighterState.JUMP
                        play("jump")
                        return
                    # Bloquear si cerca
                    elif proj_dist <= 80 and random.random() < 0.55:
                        self.blocking = True
                        self.vx = 0
                        self.state = FighterState.BLOCK
                        return

        # ── Bloquear ante ataque inminente ────────────────────────────────
        if player.atk_active and abs_dist < 140:
            block_chance = 0.35 + attack_freq * 0.2
            if random.random() < block_chance:
                self.blocking = True
                self.vx = 0
                self.state = FighterState.BLOCK
                return

        # ── Táctica principal ─────────────────────────────────────────────
        tactic = self.ai_tactic

        if tactic in ("aggressive", "finish", "desperate", "pressure"):
            engage = 160; retreat = 35
            speed_mult = 1.15 if tactic == "pressure" else 1.0

            if abs_dist > engage:
                self.vx = self.direction * self.speed * speed_mult
                self.state = FighterState.WALK
            elif abs_dist < retreat:
                self.vx = -self.direction * self.speed * 0.55
            else:
                self.vx = 0
                self.state = FighterState.IDLE

            if self.atk_cooldown <= 0:
                finish_mult = 1.5 if tactic == "finish" else 1.0
                if self.super_meter >= self.SUPER_THRESHOLD and \
                   abs_dist < 190 and random.random() < 0.22 * self.ai_aggression:
                    self._attack(AttackType.SUPER)
                elif abs_dist < self.KICK_RANGE * 1.1:
                    prob = 0.09 * self.ai_aggression * finish_mult
                    if random.random() < prob:
                        a = AttackType.KICK if abs_dist > 60 else AttackType.PUNCH
                        self._attack(a)
                elif abs_dist < 290 and random.random() < 0.065 * self.ai_aggression:
                    self._attack(AttackType.SPECIAL)

        elif tactic == "poke":
            engage = 150
            if abs_dist > engage:
                self.vx = self.direction * self.speed * 0.75
                self.state = FighterState.WALK
            elif abs_dist < 65:
                self.vx = -self.direction * self.speed * 0.5
            else:
                self.vx = 0
            if self.atk_cooldown <= 0 and abs_dist < self.PUNCH_RANGE * 1.3:
                if random.random() < 0.07:
                    self._attack(AttackType.PUNCH)

        elif tactic == "defensive":
            if abs_dist < 110:
                self.vx = -self.direction * self.speed * 0.65
            elif abs_dist > 260:
                self.vx = self.direction * self.speed * 0.45
            else:
                self.vx = 0
            # Contraataque si el jugador está en animación de ataque
            if self.super_meter >= self.SUPER_THRESHOLD and \
               abs_dist < 170 and random.random() < 0.18:
                self._attack(AttackType.SUPER)
            elif not player.atk_active and self.atk_cooldown <= 0 and \
                 abs_dist < self.PUNCH_RANGE and random.random() < 0.05:
                self._attack(AttackType.PUNCH)

        else:  # neutral
            engage = 140
            if abs_dist > engage:
                self.vx = self.direction * self.speed * 0.72
                self.state = FighterState.WALK
            elif abs_dist < 55:
                self.vx = -self.direction * self.speed * 0.45
            else:
                self.vx = 0
            if self.atk_cooldown <= 0:
                if abs_dist < self.KICK_RANGE and random.random() < 0.045:
                    self._attack(random.choice([AttackType.PUNCH, AttackType.KICK]))
                elif abs_dist < 310 and random.random() < 0.030:
                    self._attack(AttackType.SPECIAL)

        # Salto aleatorio / táctico
        if self.on_ground and self.ai_tactic in ("aggressive", "pressure"):
            if jump_freq > 0.15 and random.random() < 0.01:  # No "mirror" saltos
                pass
            elif random.random() < 0.003:
                self.vy = -self.jump_power
                self.on_ground = False
                self.state = FighterState.JUMP
                play("jump")

    # ── Ejecutar ataque ───────────────────────────────────────────────────
    def _attack(self, atype):
        if self.atk_cooldown > 0 or self.hit_stun > 0 or self.ko:
            return
        self.atk_type   = atype
        self.atk_hit    = False
        self.atk_active = True

        if atype == AttackType.PUNCH:
            self.atk_timer    = 14
            self.atk_cooldown = 22
            self.state        = FighterState.ATTACK
            play("punch")

        elif atype == AttackType.KICK:
            self.atk_timer    = 18
            self.atk_cooldown = 30
            self.state        = FighterState.ATTACK
            play("kick")

        elif atype == AttackType.SPECIAL:
            self.atk_timer    = 24
            self.atk_cooldown = 46
            self.state        = FighterState.SPECIAL
            play("special")
            py  = self.y + self.h//2 - 10
            px  = self.x + self.w if self.direction > 0 else self.x
            projectiles.append(Projectile(px, py, self.direction, self,
                                          self.SPECIAL_DMG, self.char["special_color"],
                                          14, 10))
            add_text(int(self.x+self.w//2), int(self.y-45),
                     self.char["special_name"], self.char["special_color"], 30)

        elif atype == AttackType.SUPER:
            self.atk_timer    = 48
            self.atk_cooldown = 72
            self.state        = FighterState.SUPER
            self.super_meter  = 0
            play("super")
            do_shake(20)
            add_text(int(self.x+self.w//2), int(self.y-65),
                     self.char["super_name"]+"!!", self.char["super_color"], 40)
            py  = self.y + self.h//2 - 10
            px  = self.x + self.w if self.direction > 0 else self.x
            projectiles.append(Projectile(px, py, self.direction, self,
                                          self.SUPER_DMG, self.char["super_color"],
                                          26, 14))
            emit_particles(int(self.x+self.w//2), int(self.y+self.h//2),
                           self.char["super_color"], 35, 9)

    def get_attack_rect(self):
        """Hitbox de ataque cuerpo a cuerpo (solo punch y kick)."""
        if not self.atk_active or self.atk_type in (AttackType.NONE,
                                                     AttackType.SPECIAL,
                                                     AttackType.SUPER):
            return None
        rng_  = self.PUNCH_RANGE if self.atk_type == AttackType.PUNCH else self.KICK_RANGE
        hoff  = self.h//3       if self.atk_type == AttackType.PUNCH else self.h//2
        if self.direction > 0:
            return pygame.Rect(self.x + self.w, self.y + hoff, rng_, 26)
        else:
            return pygame.Rect(self.x - rng_,   self.y + hoff, rng_, 26)

    def get_body_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def take_damage(self, dmg, attacker, is_super=False):
        if self.ko: return   # FIX: no procesar daño si ya está KO

        if self.blocking:
            dmg = max(1, int(dmg * 0.12))
            add_text(int(self.x+self.w//2), int(self.y-25), "BLOCK!", CYAN, 30)
            play("block")
        else:
            # Cargar super al recibir daño
            self.super_meter    = min(100, self.super_meter + dmg//3)
            attacker.super_meter = min(100, attacker.super_meter + dmg//4)

        self.hp = max(0, self.hp - dmg)
        # Knockback
        kb = 9 if is_super else (7 if dmg > 25 else 4)
        self.vx = -attacker.direction * kb
        self.vy = -5 if is_super else -3
        self.hit_stun = 22 if is_super else (16 if dmg > 25 else 11)
        self.state    = FighterState.HIT
        play("hit")

        cx_ = int(self.x + self.w//2)
        cy_ = int(self.y + self.h//3)
        emit_hit(cx_, cy_, self.char["accent"], big=is_super)
        if is_super: do_shake(16)
        add_text(cx_, int(self.y-25),
                 f"-{dmg}", ORANGE if is_super else RED,
                 38 if is_super else 30)

        if self.hp <= 0:
            self.ko    = True
            self.state = FighterState.KO
            play("ko")
            emit_particles(cx_, cy_, self.char["body"], 40, 9)
            do_shake(28)

    def update(self):
        if self.atk_cooldown > 0:
            self.atk_cooldown -= 1

        if self.hit_stun > 0:
            self.hit_stun -= 1
            if self.hit_stun == 0 and not self.ko:
                self.state = FighterState.IDLE

        if self.atk_active:
            self.atk_timer -= 1
            if self.atk_timer <= 0:
                self.atk_active = False
                self.atk_type   = AttackType.NONE
                if not self.ko and self.hit_stun == 0:
                    self.state = FighterState.IDLE

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0

        # Física
        self.vy += 0.62          # gravedad
        self.y  += self.vy
        self.x  += self.vx

        # Aterrizaje
        ground_y = float(FLOOR_Y - self.h)
        if self.y >= ground_y:
            self.y = ground_y
            if self.vy > 2:     # sólo emitir partículas si cayó con velocidad
                emit_particles(int(self.x+self.w//2), FLOOR_Y,
                               (110,90,55), 5, 2)
            self.vy = 0
            was_jumping = not self.on_ground
            self.on_ground = True
            if self.state == FighterState.JUMP:
                self.state = FighterState.IDLE
        else:
            self.on_ground = False

        # Límites de pantalla (con pequeño margen)
        self.x = max(5.0, min(float(SCREEN_WIDTH - self.w - 5), self.x))

        # Push-apart: evitar que los personajes se superpongan
        # (se resuelve en check_collisions)

        # Animaciones
        if self.state == FighterState.WALK:
            self.walk_cycle += 0.22

        self.anim_frame += 1

    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        cx = ix + self.w//2

        # Sombra en el suelo
        dist = FLOOR_Y - (iy + self.h)
        sw   = max(20, int(self.w * (1 - dist/250) * 1.3))
        pygame.draw.ellipse(surf, (0,0,0), (cx-sw//2, FLOOR_Y-6, sw, 12))

        flash = self.hit_stun > 0 and (self.anim_frame % 4 < 2)

        if self.ko:
            ko_w = int(self.w * 1.6)
            ko_h = int(self.h * 0.25)
            ko_x = ix - ko_w//4
            pygame.draw.ellipse(surf, self.char["body"],
                                (ko_x, FLOOR_Y-ko_h, ko_w, ko_h))
            pygame.draw.ellipse(surf, self.char["skin"],
                                (ko_x+ko_w-30, FLOOR_Y-ko_h-8, 24, 20))
            ko_t = fLG.render("KO", True, YELLOW)
            surf.blit(ko_t, (cx-ko_t.get_width()//2, iy-75))
            for rr in range(1, 5):
                pygame.draw.circle(surf, YELLOW, (cx, iy-40), rr*7, 1)
            return

        draw_fighter_sprite(surf, self, ix, iy, flash)


# ══════════════════════════════════════════════════════════════════════════
# SEPARACIÓN entre personajes (push-apart)
# ══════════════════════════════════════════════════════════════════════════
def push_apart(p1, p2):
    """Evita que los personajes se superpongan."""
    overlap = (p1.w + p2.w) * 0.45   # distancia mínima
    dist = p2.x - p1.x
    if abs(dist) < overlap:
        push = (overlap - abs(dist)) / 2 + 1
        if dist >= 0:
            p1.x -= push; p2.x += push
        else:
            p1.x += push; p2.x -= push
    p1.x = max(5.0, min(float(SCREEN_WIDTH-p1.w-5), p1.x))
    p2.x = max(5.0, min(float(SCREEN_WIDTH-p2.w-5), p2.x))


# ══════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════
def draw_hud(surf, p1, p2, frame, mode2p, rnd, w1, w2):
    bw = 420; bh = 32; by = 14

    # P1 HP
    r1  = p1.hp / p1.max_hp
    pygame.draw.rect(surf, (30,12,12), (18, by, bw, bh), border_radius=6)
    bc1 = GREEN if r1 > 0.5 else (YELLOW if r1 > 0.25 else RED)
    pygame.draw.rect(surf, bc1, (18, by, int(bw*r1), bh), border_radius=6)
    for seg in range(0, bw, bw//10):
        pygame.draw.line(surf, (0,0,0), (18+seg, by), (18+seg, by+bh), 1)
    pygame.draw.rect(surf, WHITE, (18, by, bw, bh), 2, border_radius=6)
    n1 = fSM.render(CHARACTERS[p1.char_key]["display"], True, p1.char["accent"])
    surf.blit(n1, (20, by+bh+4))
    hp1 = fXS.render(f"{int(p1.hp)}/{p1.max_hp}", True, WHITE)
    surf.blit(hp1, (20+bw-hp1.get_width(), by+bh+4))

    # P1 Super
    sm_y = by+bh+22; smw = bw; smh = 12
    pygame.draw.rect(surf, (15,15,55), (18, sm_y, smw, smh), border_radius=4)
    sr1   = p1.super_meter / 100
    pulse = abs(math.sin(frame*0.1))*25 if p1.super_meter >= p1.SUPER_THRESHOLD else 0
    sm_c1 = GOLD if p1.super_meter >= 100 else \
            ((80,200,80) if p1.super_meter >= p1.SUPER_THRESHOLD else (80,80,200))
    sm_c1 = tuple(min(255, int(v+pulse)) for v in sm_c1)
    pygame.draw.rect(surf, sm_c1, (18, sm_y, int(smw*sr1), smh), border_radius=4)
    # Línea del umbral 50%
    tx1 = 18 + smw//2
    pygame.draw.line(surf, WHITE, (tx1, sm_y-1), (tx1, sm_y+smh+1), 2)
    pygame.draw.rect(surf, (80,80,255), (18, sm_y, smw, smh), 1, border_radius=4)
    ready1 = p1.super_meter >= p1.SUPER_THRESHOLD
    slbl = fTN.render(f"SUPER (Q) {'▶ LISTO!' if ready1 else ''}", True,
                      (100,200,100) if ready1 else (80,80,180))
    surf.blit(slbl, (20, sm_y+smh+3))

    # P2 HP
    r2  = p2.hp / p2.max_hp
    p2x = SCREEN_WIDTH - 20 - bw
    pygame.draw.rect(surf, (30,12,12), (p2x, by, bw, bh), border_radius=6)
    bc2 = GREEN if r2 > 0.5 else (YELLOW if r2 > 0.25 else RED)
    fw2 = int(bw * r2)
    pygame.draw.rect(surf, bc2, (p2x+bw-fw2, by, fw2, bh), border_radius=6)
    for seg in range(0, bw, bw//10):
        pygame.draw.line(surf, (0,0,0), (p2x+seg, by), (p2x+seg, by+bh), 1)
    pygame.draw.rect(surf, WHITE, (p2x, by, bw, bh), 2, border_radius=6)
    n2_str = CHARACTERS[p2.char_key]["display"] if mode2p else \
             f"CPU: {CHARACTERS[p2.char_key]['display']}"
    n2 = fSM.render(n2_str, True, p2.char["accent"])
    surf.blit(n2, (p2x+bw-n2.get_width(), by+bh+4))
    hp2 = fXS.render(f"{int(p2.hp)}/{p2.max_hp}", True, WHITE)
    surf.blit(hp2, (p2x, by+bh+4))

    # P2 Super
    sm_y2 = by+bh+22
    pygame.draw.rect(surf, (15,15,55), (p2x, sm_y2, smw, smh), border_radius=4)
    sr2   = p2.super_meter / 100
    pulse2 = abs(math.sin(frame*0.1))*25 if p2.super_meter >= p2.SUPER_THRESHOLD else 0
    sm_c2 = GOLD if p2.super_meter >= 100 else \
            ((80,200,80) if p2.super_meter >= p2.SUPER_THRESHOLD else (80,80,200))
    sm_c2 = tuple(min(255, int(v+pulse2)) for v in sm_c2)
    pygame.draw.rect(surf, sm_c2, (p2x+bw-int(smw*sr2), sm_y2, int(smw*sr2), smh), border_radius=4)
    tx2 = p2x + smw//2
    pygame.draw.line(surf, WHITE, (tx2, sm_y2-1), (tx2, sm_y2+smh+1), 2)
    pygame.draw.rect(surf, (80,80,255), (p2x, sm_y2, smw, smh), 1, border_radius=4)

    # Centro: ronda y tiempo
    rt = fSM.render(f"ROUND {rnd}", True, GOLD)
    surf.blit(rt, (SCREEN_WIDTH//2 - rt.get_width()//2, by))
    el = frame // FPS
    tc = RED if el > 75 else GOLD
    tt = fMD.render(str(el), True, tc)
    surf.blit(tt, (SCREEN_WIDTH//2 - tt.get_width()//2, by+30))

    # Victorias (puntos)
    for i in range(w1):
        pygame.draw.circle(surf, GOLD,   (SCREEN_WIDTH//2-20-i*22, by+72), 7)
        pygame.draw.circle(surf, YELLOW, (SCREEN_WIDTH//2-20-i*22, by+72), 7, 2)
    for i in range(w2):
        pygame.draw.circle(surf, ORANGE, (SCREEN_WIDTH//2+20+i*22, by+72), 7)
        pygame.draw.circle(surf, RED,    (SCREEN_WIDTH//2+20+i*22, by+72), 7, 2)

    # Combo counter
    if p1.combo_count >= 2:
        ct = fMD.render(f"{p1.combo_count}x COMBO!", True, GOLD)
        surf.blit(ct, (20, 115))
    if p2.combo_count >= 2:
        ct2 = fMD.render(f"{p2.combo_count}x COMBO!", True, ORANGE)
        surf.blit(ct2, (SCREEN_WIDTH-20-ct2.get_width(), 115))

    # Controles (pie de pantalla)
    if mode2p:
        h_str = "P1: WASD+Space/Shift/E(especial)/Q(super≥50%)  |  P2: ←→↑↓+L/;/O/P"
    else:
        h_str = "WASD:Mover  Space:Puño  LShift:Patada  E(mantén):Especial  Q:SUPER  ↓:Bloquear"
    ht = fTN.render(h_str, True, (90,90,90))
    surf.blit(ht, (SCREEN_WIDTH//2 - ht.get_width()//2, SCREEN_HEIGHT-16))


# ══════════════════════════════════════════════════════════════════════════
# COLISIONES
# ══════════════════════════════════════════════════════════════════════════
def check_collisions(p1, p2):
    # Proyectiles
    for proj in projectiles[:]:
        target   = p2 if proj.owner is p1 else p1
        attacker = p1 if proj.owner is p1 else p2
        if not proj.alive: continue
        if proj.get_rect().colliderect(target.get_body_rect()):
            is_big = proj.size >= 22
            target.take_damage(proj.dmg, attacker, is_super=is_big)
            proj.alive = False
            # Combo
            attacker.combo_count += 1
            attacker.combo_timer  = 90
            if attacker.combo_count >= 3:
                play("combo")
                add_text(int(attacker.x+attacker.w//2), int(attacker.y-55),
                         f"{attacker.combo_count}x COMBO!", GOLD, 40)

    # Cuerpo a cuerpo
    for att_owner, bod_target in [(p1, p2), (p2, p1)]:
        att_rect = att_owner.get_attack_rect()
        if att_rect is None: continue
        if not att_owner.atk_hit and att_rect.colliderect(bod_target.get_body_rect()):
            dmg = att_owner.PUNCH_DMG if att_owner.atk_type == AttackType.PUNCH \
                  else att_owner.KICK_DMG
            bod_target.take_damage(dmg, att_owner)
            att_owner.atk_hit     = True
            att_owner.combo_count += 1
            att_owner.combo_timer  = 90
            if att_owner.combo_count >= 3:
                play("combo")
                c = GOLD if att_owner.player_id == 1 else ORANGE
                add_text(int(att_owner.x+att_owner.w//2), int(att_owner.y-55),
                         f"{att_owner.combo_count}x COMBO!", c, 40)


# ══════════════════════════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════════════════════════
def draw_menu(surf, bg, f):
    bg.draw(surf)
    t = math.sin(f * 0.04) * 5
    for dx, dy, c in [(3,3,(80,20,0)), (-2,3,(60,15,0)), (0,0,GOLD)]:
        ti = fXL.render("MINI STREET FIGHTER", True, c)
        surf.blit(ti, (SCREEN_WIDTH//2 - ti.get_width()//2 + dx, 115+int(t)+dy))
    sub = fSM.render("VERSIÓN SUPREMA v2.0", True, CYAN)
    surf.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 225))
    pygame.draw.line(surf, GOLD, (SCREEN_WIDTH//2-320, 262), (SCREEN_WIDTH//2+320, 262), 2)

    opts = [("1  —  1 Jugador (vs CPU)", WHITE),
            ("2  —  2 Jugadores",        WHITE),
            ("ESC  —  Salir",            (130,130,130))]
    oy = 285
    for txt, col in opts:
        p = abs(math.sin(f*0.05+oy))*35 if col == WHITE else 0
        c_ = tuple(min(255, int(v+p)) for v in col)
        t2 = fMD.render(txt, True, c_)
        surf.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, oy))
        oy += 58

    # Previsualización de personajes en el menú
    chars = list(CHARACTERS.keys())
    for i, k in enumerate(chars):
        ch = CHARACTERS[k]
        px = SCREEN_WIDTH // (len(chars)+1) * (i+1)
        sw = int(math.sin(f*0.06 + i*1.5) * 6)
        pygame.draw.rect(surf, ch["body"],  (px-20, 510+sw, 40, 52), border_radius=3)
        pygame.draw.rect(surf, ch["pants"], (px-18, 562+sw, 16, 30), border_radius=3)
        pygame.draw.rect(surf, ch["pants"], (px+2,  562+sw, 16, 30), border_radius=3)
        pygame.draw.circle(surf, ch["skin"], (px, 498+sw), 19)
        pygame.draw.circle(surf, ch["hair"], (px, 488+sw), 14)
        nm = fTN.render(ch["display"], True, ch["accent"])
        surf.blit(nm, (px-nm.get_width()//2, 598))

    ctrls = [
        "P1: WASD + Space(puño) + LShift(patada) + E(especial) + Q(super al 50%)",
        "P2: ←→↑↓ + L(puño) + ;(patada) + O(especial) + P(super)",
    ]
    cy2 = 620
    for line in ctrls:
        ct = fTN.render(line, True, (110,110,110))
        surf.blit(ct, (SCREEN_WIDTH//2 - ct.get_width()//2, cy2))
        cy2 += 18


def draw_char_select(surf, bg, f, sel_for, sel_chars, cursor):
    bg.draw(surf)
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 130))
    surf.blit(ov, (0, 0))

    lbl = {0: "JUGADOR 1", 1: "JUGADOR 2", 2: "CPU"}
    ti = fMD.render(f"ELIGE PERSONAJE — {lbl.get(sel_for,'?')}", True, GOLD)
    surf.blit(ti, (SCREEN_WIDTH//2 - ti.get_width()//2, 28))

    chars = list(CHARACTERS.keys())
    bw = 210; bh = 200
    sx = SCREEN_WIDTH//2 - (len(chars)*bw)//2 + bw//2
    y  = 130
    for i, k in enumerate(chars):
        ch  = CHARACTERS[k]
        x_  = sx + i*bw
        sel = (i == cursor)
        bc  = GOLD if sel else (70,70,70)
        bg2 = (45,30,65) if sel else (18,14,32)
        pygame.draw.rect(surf, bg2, (x_-bw//2+5, y, bw-10, bh), border_radius=10)
        pygame.draw.rect(surf, bc,  (x_-bw//2+5, y, bw-10, bh), 3, border_radius=10)
        mx = x_; my = y + bh//2
        pygame.draw.rect(surf, ch["body"],  (mx-22, my-30, 44, 55), border_radius=4)
        pygame.draw.rect(surf, ch["pants"], (mx-20, my+25, 18, 28), border_radius=3)
        pygame.draw.rect(surf, ch["pants"], (mx+2,  my+25, 18, 28), border_radius=3)
        pygame.draw.rect(surf, ch.get("belt",(200,60,60)), (mx-22, my+18, 44, 8))
        pygame.draw.circle(surf, ch["skin"], (mx, my-42), 18)
        pygame.draw.circle(surf, ch["hair"], (mx, my-54), 12)
        pygame.draw.circle(surf, WHITE, (mx-6, my-42), 3)
        pygame.draw.circle(surf, WHITE, (mx+6, my-42), 3)
        pygame.draw.circle(surf, BLACK, (mx-5, my-42), 2)
        pygame.draw.circle(surf, BLACK, (mx+6, my-42), 2)
        nm = fSM.render(ch["display"], True, ch["accent"])
        surf.blit(nm, (x_-nm.get_width()//2, y+bh+5))
        dc = fTN.render(ch["desc"], True, (160,160,160))
        surf.blit(dc, (x_-dc.get_width()//2, y+bh+28))

    # Stats del personaje seleccionado
    sk = chars[cursor]; sc = CHARACTERS[sk]
    sy2 = y + bh + 60
    for i, st in enumerate([
        f"HP: {sc['hp']}",
        f"Velocidad: {sc['speed']}",
        f"Puño: {sc['punch']}  Patada: {sc['kick']}",
        f"{sc['special_name']}: {sc['special']}",
        f"SUPER {sc['super_name']}: {sc['super']}",
    ]):
        t2 = fXS.render(st, True, sc["accent"])
        surf.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, sy2+i*23))

    if sel_chars[0]:
        p1l = fXS.render(f"P1: {CHARACTERS[sel_chars[0]]['display']}", True,
                          CHARACTERS[sel_chars[0]]["accent"])
        surf.blit(p1l, (20, SCREEN_HEIGHT-50))

    hi = fSM.render("← → para elegir   |   ENTER / ESPACIO para confirmar", True, (170,170,170))
    surf.blit(hi, (SCREEN_WIDTH//2 - hi.get_width()//2, SCREEN_HEIGHT-28))


def draw_round_announce(surf, rnd, timer):
    rt = fXL.render(f"ROUND {rnd}", True, GOLD)
    surf.blit(rt, (SCREEN_WIDTH//2 - rt.get_width()//2, SCREEN_HEIGHT//2 - 80))
    if timer < 35:
        ft = fLG.render("FIGHT!", True, RED)
        surf.blit(ft, (SCREEN_WIDTH//2 - ft.get_width()//2, SCREEN_HEIGHT//2 + 20))


def draw_result(surf, bg, winner, mode2p, w1, w2, c1, c2, f):
    bg.draw(surf)
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 155))
    surf.blit(ov, (0, 0))

    if winner == 0:
        txt = "¡EMPATE!"; col = YELLOW
    elif winner == 1:
        txt = f"¡{CHARACTERS[c1]['display']} GANA!" if mode2p else "¡VICTORIA!"
        col = CHARACTERS[c1]["accent"]
    else:
        txt = f"¡{CHARACTERS[c2]['display']} GANA!" if mode2p else "¡DERROTA!"
        col = CHARACTERS[c2]["accent"] if mode2p else RED

    pulse = abs(math.sin(f * 0.05)) * 22
    c_ = tuple(min(255, int(v+pulse)) for v in col)
    big = fXL.render(txt, True, c_)
    surf.blit(big, (SCREEN_WIDTH//2 - big.get_width()//2, SCREEN_HEIGHT//2 - 110))
    sc = fLG.render(f"{w1}  :  {w2}", True, GOLD)
    surf.blit(sc, (SCREEN_WIDTH//2 - sc.get_width()//2, SCREEN_HEIGHT//2 + 10))
    sub = fSM.render("ESPACIO — Volver al menú", True, YELLOW)
    surf.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 110))


# ══════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════
class GS(Enum):
    MENU=0; SELECT=1; RSTART=2; PLAY=3; REND=4; RESULT=5

def make_players(mode2p, c1k, c2k):
    ctrl1 = {
        'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
        'punch': pygame.K_SPACE, 'kick': pygame.K_LSHIFT, 'block': pygame.K_s,
        'special': pygame.K_e, 'super': pygame.K_q,
    }
    ctrl2 = {
        'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
        'punch': pygame.K_l, 'kick': pygame.K_SEMICOLON, 'block': pygame.K_DOWN,
        'special': pygame.K_o, 'super': pygame.K_p,
    }
    p1 = Fighter(SCREEN_WIDTH//4,   pid=1, char_key=c1k,
                 controls=ctrl1, is_ai=False)
    p2 = Fighter(3*SCREEN_WIDTH//4, pid=2, char_key=c2k,
                 controls=ctrl2 if mode2p else None, is_ai=not mode2p)
    p1.direction =  1
    p2.direction = -1
    return p1, p2

def main():
    bg     = Background()
    state  = GS.MENU
    mode2p = False
    p1 = p2 = None
    frame  = 0; winner = None; menu_f = 0
    chars  = list(CHARACTERS.keys())
    cursors = [0, 0]; sel = [None, None]; sel_phase = 0
    rnd = 1; w1 = 0; w2 = 0
    ra_timer = 0; re_timer = 0; res_f = 0

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if state in (GS.PLAY, GS.SELECT, GS.RSTART, GS.REND):
                        state = GS.MENU
                        for lst in (particles, sparks, texts, projectiles):
                            lst.clear()
                    else:
                        running = False

                # ── MENÚ ──────────────────────────────────────────────────
                if state == GS.MENU:
                    if ev.key == pygame.K_1:
                        mode2p = False; sel = [None,None]; cursors = [0,0]
                        sel_phase = 0; state = GS.SELECT
                    elif ev.key == pygame.K_2:
                        mode2p = True;  sel = [None,None]; cursors = [0,0]
                        sel_phase = 0; state = GS.SELECT

                # ── SELECCIÓN ─────────────────────────────────────────────
                elif state == GS.SELECT:
                    cp = sel_phase
                    if ev.key == pygame.K_LEFT:
                        cursors[cp] = (cursors[cp]-1) % len(chars)
                    elif ev.key == pygame.K_RIGHT:
                        cursors[cp] = (cursors[cp]+1) % len(chars)
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_l):
                        sel[cp] = chars[cursors[cp]]
                        if cp == 0 and mode2p:
                            sel_phase = 1
                        else:
                            if not mode2p:
                                # CPU elige personaje diferente al del jugador
                                ai_opts = [k for k in chars if k != sel[0]]
                                sel[1] = random.choice(ai_opts)
                            p1, p2 = make_players(mode2p, sel[0], sel[1])
                            for lst in (particles, sparks, texts, projectiles):
                                lst.clear()
                            frame = 0; rnd = 1; w1 = 0; w2 = 0
                            ra_timer = 65; state = GS.RSTART
                            play("round")

                # ── RESULTADO ─────────────────────────────────────────────
                elif state == GS.RESULT:
                    if ev.key == pygame.K_SPACE:
                        state = GS.MENU

        # ── UPDATE ────────────────────────────────────────────────────────
        bg.update()

        if state == GS.RSTART:
            ra_timer -= 1
            if ra_timer <= 0:
                state = GS.PLAY; frame = 0

        elif state == GS.PLAY:
            frame += 1
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
            push_apart(p1, p2)     # FIX: separar personajes superpuestos
            update_effects()

            # Auto-dirección cara al oponente
            if not p1.ko and not p2.ko:
                if p1.x < p2.x:
                    p1.direction =  1; p2.direction = -1
                else:
                    p1.direction = -1; p2.direction =  1

            # Detectar fin de ronda
            if p1.ko or p2.ko:
                if   p1.ko and p2.ko: winner = 0
                elif p1.ko:           winner = 2; w2 += 1
                else:                 winner = 1; w1 += 1
                re_timer = 110; state = GS.REND

        elif state == GS.REND:
            re_timer -= 1
            update_effects()
            if re_timer <= 0:
                if w1 >= 2 or w2 >= 2 or rnd >= 3:
                    res_f = 0; state = GS.RESULT
                else:
                    rnd += 1
                    p1, p2 = make_players(mode2p, sel[0], sel[1])
                    for lst in (particles, sparks, texts, projectiles):
                        lst.clear()
                    frame = 0; ra_timer = 65; state = GS.RSTART
                    play("round")

        elif state == GS.RESULT:
            res_f += 1
        elif state == GS.MENU:
            menu_f += 1

        # ── DRAW ──────────────────────────────────────────────────────────
        ds = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        if state == GS.MENU:
            draw_menu(ds, bg, menu_f)

        elif state == GS.SELECT:
            draw_char_select(ds, bg, menu_f,
                             0 if sel_phase == 0 else (1 if mode2p else 2),
                             sel, cursors[sel_phase])
            menu_f += 1

        elif state == GS.RSTART:
            bg.draw(ds)
            if p1 and p2:
                p1.draw(ds); p2.draw(ds)
                draw_effects(ds)
                draw_hud(ds, p1, p2, 0, mode2p, rnd, w1, w2)
            draw_round_announce(ds, rnd, ra_timer)

        elif state == GS.PLAY:
            bg.draw(ds)
            p1.draw(ds); p2.draw(ds)
            draw_effects(ds)
            draw_hud(ds, p1, p2, frame, mode2p, rnd, w1, w2)

        elif state == GS.REND:
            bg.draw(ds)
            p1.draw(ds); p2.draw(ds)
            draw_effects(ds)
            draw_hud(ds, p1, p2, frame, mode2p, rnd, w1, w2)
            wn = None
            if winner != 0:
                wn = CHARACTERS[sel[0 if winner==1 else 1]]["display"]
                wt = fLG.render(f"¡{wn} GANA!", True,
                                CHARACTERS[sel[0 if winner==1 else 1]]["accent"])
            else:
                wt = fLG.render("¡EMPATE!", True, YELLOW)
            ds.blit(wt, (SCREEN_WIDTH//2 - wt.get_width()//2, SCREEN_HEIGHT//2 - 55))

        elif state == GS.RESULT:
            fw = 1 if w1 > w2 else (2 if w2 > w1 else 0)
            draw_result(ds, bg, fw, mode2p, w1, w2,
                        sel[0] or "RYU", sel[1] or "KEN", res_f)

        screen.blit(ds, (shake_x, shake_y))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
