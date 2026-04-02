import cv2
import mediapipe as mp
import pygame
import sys
import time
import random
import math

# --- INIT ---
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
WIDTH, HEIGHT = 1280, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✊ HAND FIGHTER ✊")
clock = pygame.time.Clock()

# --- FONTS ---
font_big   = pygame.font.SysFont("Arial", 72, bold=True)
font_med   = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 22)
font_title = pygame.font.SysFont("Arial", 96, bold=True)

# --- COLORS ---
RED     = (220, 50,  50)
BLUE    = (50,  100, 220)
GREEN   = (50,  220, 100)
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
YELLOW  = (255, 220, 0)
ORANGE  = (255, 140, 0)
GRAY    = (30,  30,  30)
DGRAY   = (20,  20,  20)
PURPLE  = (150, 50,  220)

# --- SOUND GENERATION ---
def make_sound(freq, duration, volume=0.5, wave='square'):
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        t = i / sample_rate
        if wave == 'square':
            val = volume if math.sin(2 * math.pi * freq * t) > 0 else -volume
        else:
            val = volume * math.sin(2 * math.pi * freq * t)
        arr.append([int(val * 32767)] * 2)
    sound_arr = pygame.sndarray.make_sound(
        __import__('numpy').array(arr, dtype='int16'))
    return sound_arr

try:
    import numpy
    punch_sound = make_sound(180, 0.12, 0.6, 'square')
    block_sound = make_sound(300, 0.1,  0.4, 'square')
    ko_sound    = make_sound(80,  0.6,  0.8, 'square')
    sounds_ok   = True
except ImportError:
    sounds_ok = False

def play(sound):
    if sounds_ok:
        try: sound.play()
        except: pass

# --- MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --- PARTICLES ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-10, -2)
        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.size = random.randint(4, 12)

    def update(self):
        self.x += self.vx
        self.vy += 0.4
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        color = (*self.color[:3], alpha)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x)-self.size, int(self.y)-self.size))

particles = []

def spawn_particles(x, y, color, count=20):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# --- HP BAR ---
class HPBar:
    def __init__(self, x, y, w, h, flip=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.flip = flip
        self.display_hp = 100
        self.shake = 0

    def update(self, target_hp):
        if self.display_hp > target_hp:
            self.display_hp = max(target_hp, self.display_hp - 2)
            self.shake = 6

        if self.shake > 0:
            self.shake -= 1

    def draw(self, surface, hp, name):
        ox = random.randint(-self.shake, self.shake) if self.shake else 0

        # Background
        pygame.draw.rect(surface, DGRAY, (self.x+ox, self.y, self.w, self.h), border_radius=8)

        # Delayed (white flash)
        dw = int(self.w * self.display_hp / 100)
        pygame.draw.rect(surface, WHITE, (self.x+ox, self.y, dw, self.h), border_radius=8)

        # Actual HP
        hw = int(self.w * hp / 100)
        ratio = hp / 100
        color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
        pygame.draw.rect(surface, color, (self.x+ox, self.y, hw, self.h), border_radius=8)

        # Border
        pygame.draw.rect(surface, WHITE, (self.x+ox, self.y, self.w, self.h), 2, border_radius=8)

        # HP text
        txt = font_small.render(f"{name}  {int(hp)} HP", True, WHITE)
        surface.blit(txt, (self.x+ox, self.y + self.h + 5))


# --- PLAYER ---
class Player:
    def __init__(self, name, color, fighter_x, hp_bar):
        self.name = name
        self.color = color
        self.fighter_x = fighter_x
        self.hp = 100
        self.gesture = "none"
        self.blocking = False
        self.action_text = ""
        self.action_timer = 0
        self.action_color = YELLOW
        self.last_punch_time = 0
        self.punch_anim = 0
        self.hp_bar = hp_bar

    def take_damage(self, dmg):
        if not self.blocking:
            self.hp = max(0, self.hp - dmg)
            return True
        return False

    def draw_fighter(self, surface):
        x, y = self.fighter_x, 220
        arm_ext = 70 if self.punch_anim > 0 else 30
        if self.punch_anim > 0:
            self.punch_anim -= 1

        body_color = GREEN if self.blocking else self.color

        # Shadow
        pygame.draw.ellipse(surface, (20,20,20), (x-35, y+125, 70, 18))

        # Body
        pygame.draw.rect(surface, body_color, (x-22, y+45, 44, 75), border_radius=10)

        # Head
        pygame.draw.circle(surface, body_color, (x, y), 38)
        # Eyes
        pygame.draw.circle(surface, WHITE, (x-12, y-8), 8)
        pygame.draw.circle(surface, WHITE, (x+12, y-8), 8)
        pygame.draw.circle(surface, BLACK, (x-12, y-8), 4)
        pygame.draw.circle(surface, BLACK, (x+12, y-8), 4)
        # Mouth
        if self.blocking:
            pygame.draw.line(surface, WHITE, (x-10, y+14), (x+10, y+14), 3)
        else:
            pygame.draw.arc(surface, WHITE,
                pygame.Rect(x-10, y+8, 20, 12), math.pi, 2*math.pi, 3)

        # Arms
        pygame.draw.rect(surface, body_color, (x-arm_ext-22, y+55, arm_ext, 14), border_radius=6)
        pygame.draw.rect(surface, body_color, (x+22, y+55, arm_ext, 14), border_radius=6)

        # Fists
        fist_color = ORANGE if self.punch_anim > 0 else body_color
        pygame.draw.circle(surface, fist_color, (x-arm_ext-22, y+62), 10)
        pygame.draw.circle(surface, fist_color, (x+arm_ext+22, y+62), 10)

        # Legs
        pygame.draw.rect(surface, body_color, (x-18, y+118, 16, 40), border_radius=6)
        pygame.draw.rect(surface, body_color, (x+2,  y+118, 16, 40), border_radius=6)

        # Name tag
        ntxt = font_small.render(self.name, True, WHITE)
        surface.blit(ntxt, (x - ntxt.get_width()//2, y + 168))

        # Gesture badge
        g_color = GREEN if self.blocking else (ORANGE if self.gesture == "fist" else GRAY)
        g_label = "🛡 BLOCK" if self.blocking else ("👊 PUNCH" if self.gesture == "fist" else "✋ IDLE")
        gtxt = font_small.render(g_label, True, g_color)
        surface.blit(gtxt, (x - gtxt.get_width()//2, y + 190))

        # Action popup
        if self.action_timer > 0:
            scale = min(1.0, (40 - self.action_timer) / 8)
            atxt = font_big.render(self.action_text, True, self.action_color)
            scaled = pygame.transform.rotozoom(atxt, 0, scale)
            surface.blit(scaled, (x - scaled.get_width()//2, y - 100))
            self.action_timer -= 1


# --- GAME STATES ---
STATE_INTRO     = "intro"
STATE_COUNTDOWN = "countdown"
STATE_FIGHT     = "fight"
STATE_WIN       = "win"

state = STATE_INTRO
countdown_val = 3
countdown_timer = 0
win_particles_spawned = False
winner_name = ""
winner_color = WHITE
intro_timer = 0

# --- PLAYERS SETUP ---
p1_bar = HPBar(40,  20, 280, 28)
p2_bar = HPBar(960, 20, 280, 28, flip=True)
p1 = Player("P1", RED,  320, p1_bar)
p2 = Player("P2", BLUE, 960, p2_bar)

PUNCH_COOLDOWN = 1.0
PUNCH_DAMAGE   = 10

# --- WEBCAM ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


def detect_gesture(lms):
    lm = lms.landmark
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    open_fingers = sum(1 for t, p in zip(tips, pips) if lm[t].y < lm[p].y)
    if open_fingers >= 3: return "open"
    if open_fingers == 0: return "fist"
    return "none"

def assign_hands(results, fw):
    p1h = p2h = None
    if results.multi_hand_landmarks:
        for lms in results.multi_hand_landmarks:
            wx = lms.landmark[0].x * fw
            if wx < fw / 2: p1h = lms
            else:           p2h = lms
    return p1h, p2h

def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + 20 * ratio)
        g = int(10 + 10 * ratio)
        b = int(30 + 20 * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_intro(surface, timer):
    draw_gradient_bg(surface)
    # Pulsing title
    scale = 1.0 + 0.05 * math.sin(timer * 0.1)
    title = font_title.render("HAND FIGHTER", True, YELLOW)
    scaled = pygame.transform.rotozoom(title, 0, scale)
    surface.blit(scaled, (WIDTH//2 - scaled.get_width()//2, 120))

    sub = font_med.render("✊  Two Players  •  One Webcam  •  Pure Gestures  ✊", True, WHITE)
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 260))

    p1t = font_med.render("P1: Left side of camera", True, RED)
    p2t = font_med.render("P2: Right side of camera", True, BLUE)
    surface.blit(p1t, (WIDTH//2 - p1t.get_width()//2, 320))
    surface.blit(p2t, (WIDTH//2 - p2t.get_width()//2, 360))

    g1 = font_small.render("✊ Closed Fist = PUNCH     🖐 Open Palm = BLOCK", True, GRAY)
    surface.blit(g1, (WIDTH//2 - g1.get_width()//2, 420))

    btn = font_med.render("[ Press SPACE to Start ]", True, YELLOW if (timer // 30) % 2 == 0 else ORANGE)
    surface.blit(btn, (WIDTH//2 - btn.get_width()//2, 460))

def draw_countdown(surface, val):
    draw_gradient_bg(surface)
    if val > 0:
        txt = font_title.render(str(val), True, YELLOW)
    else:
        txt = font_title.render("FIGHT!", True, GREEN)
    surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))

def draw_win(surface, winner, color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    wtxt = font_title.render(f"{winner} WINS!", True, color)
    surface.blit(wtxt, (WIDTH//2 - wtxt.get_width()//2, HEIGHT//2 - 80))

    rtxt = font_med.render("Press R to play again  •  ESC to quit", True, WHITE)
    surface.blit(rtxt, (WIDTH//2 - rtxt.get_width()//2, HEIGHT//2 + 60))

# --- MAIN LOOP ---
while True:
    dt = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE and state == STATE_INTRO:
                state = STATE_COUNTDOWN
                countdown_val = 3
                countdown_timer = pygame.time.get_ticks()
            if event.key == pygame.K_r and state == STATE_WIN:
                p1.hp = p2.hp = 100
                p1_bar.display_hp = p2_bar.display_hp = 100
                particles.clear()
                win_particles_spawned = False
                state = STATE_COUNTDOWN
                countdown_val = 3
                countdown_timer = pygame.time.get_ticks()

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(frame_rgb)

    # --- INTRO ---
    if state == STATE_INTRO:
        intro_timer += 1
        draw_intro(screen, intro_timer)
        pygame.display.flip()
        continue

    # --- COUNTDOWN ---
    if state == STATE_COUNTDOWN:
        elapsed = (pygame.time.get_ticks() - countdown_timer) / 1000
        val = 3 - int(elapsed)
        draw_countdown(screen, max(val, 0))
        if elapsed > 4:
            state = STATE_FIGHT
        pygame.display.flip()
        continue

    # --- FIGHT ---
    # Draw webcam
    frame_surf = pygame.surfarray.make_surface(
        cv2.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    screen.blit(frame_surf, (0, 0))

    # Gradient overlay (bottom)
    grad = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
    for i in range(120):
        pygame.draw.line(grad, (0, 0, 0, int(180 * i/120)), (0, i), (WIDTH, i))
    screen.blit(grad, (0, HEIGHT-120))

    # Divider
    pygame.draw.line(screen, (255,255,255,100), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

    # Detect hands
    p1h, p2h = assign_hands(results, frame.shape[1])
    p1.gesture = detect_gesture(p1h) if p1h else "none"
    p2.gesture = detect_gesture(p2h) if p2h else "none"
    p1.blocking = p1.gesture == "open"
    p2.blocking = p2.gesture == "open"

    now = time.time()

    if state == STATE_FIGHT:
        # P1 punches
        if p1.gesture == "fist" and now - p1.last_punch_time > PUNCH_COOLDOWN:
            hit = p2.take_damage(PUNCH_DAMAGE)
            p1.last_punch_time = now
            p1.punch_anim = 10
            if hit:
                play(punch_sound)
                p1.action_text = "PUNCH!"
                p1.action_color = ORANGE
                p1.action_timer = 35
                spawn_particles(p2.fighter_x, 280, RED)
            else:
                play(block_sound)
                p2.action_text = "BLOCKED!"
                p2.action_color = GREEN
                p2.action_timer = 35

        # P2 punches
        if p2.gesture == "fist" and now - p2.last_punch_time > PUNCH_COOLDOWN:
            hit = p1.take_damage(PUNCH_DAMAGE)
            p2.last_punch_time = now
            p2.punch_anim = 10
            if hit:
                play(punch_sound)
                p2.action_text = "PUNCH!"
                p2.action_color = ORANGE
                p2.action_timer = 35
                spawn_particles(p1.fighter_x, 280, BLUE)
            else:
                play(block_sound)
                p1.action_text = "BLOCKED!"
                p1.action_color = GREEN
                p1.action_timer = 35

        # Check KO
        if p1.hp <= 0:
            state = STATE_WIN
            winner_name = "P2"
            winner_color = BLUE
            play(ko_sound)
        elif p2.hp <= 0:
            state = STATE_WIN
            winner_name = "P1"
            winner_color = RED
            play(ko_sound)

    # Update & draw particles
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    # Draw fighters
    p1.draw_fighter(screen)
    p2.draw_fighter(screen)

    # HP bars
    p1_bar.update(p1.hp)
    p2_bar.update(p2.hp)
    p1_bar.draw(screen, p1.hp, "P1")
    p2_bar.draw(screen, p2.hp, "P2")

    # VS
    vs = font_big.render("VS", True, YELLOW)
    screen.blit(vs, (WIDTH//2 - vs.get_width()//2, 20))

    # Win screen
    if state == STATE_WIN:
        if not win_particles_spawned:
            for _ in range(8):
                spawn_particles(
                    random.randint(100, WIDTH-100),
                    random.randint(100, 300),
                    random.choice([RED, BLUE, YELLOW, GREEN, PURPLE, ORANGE]),
                    count=15
                )
            win_particles_spawned = True
        draw_win(screen, winner_name, winner_color)

    pygame.display.flip()