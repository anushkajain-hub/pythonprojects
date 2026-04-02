
import pygame
import cv2
import mediapipe as mp
import sys
import random
import math


pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG — Hand Controlled")
clock = pygame.time.Clock()
FPS = 60


PADDLE_W        = 16
PADDLE_H        = 110
BALL_SIZE        = 16
BALL_SPEED_INIT  = 15
BALL_SPEED_MAX   = 16
WINNING_SCORE    = 4


BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (40,  40,  40)
RED    = (220,  60,  60)
BLUE   = (60,  120, 220)
YELLOW = (255, 220,  50)
GREEN  = (60,  220, 100)


font_score = pygame.font.SysFont("Courier", 72, bold=True)
font_med   = pygame.font.SysFont("Courier", 32, bold=True)
font_small = pygame.font.SysFont("Courier", 22)


#  MEDIAPIPE HANDS SETUP 
#
#    MediaPipe gives us 21 landmarks per hand.
#    Each landmark has .x .y .z (normalized 0.0 to 1.0).
#    Landmark 0  = wrist
#    Landmark 8  = index fingertip  ← we use this for Y position
#    Landmark 12 = middle fingertip
#
#    max_num_hands=2 means it tracks up to 2 hands at once.
#    min_detection_confidence = how sure it needs to be before
#    saying "yes there's a hand here"

mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


p1 = pygame.Rect(40,              HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
p2 = pygame.Rect(WIDTH - 40 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)


ball_vx    = 0.0
ball_vy    = 0.0
score_p1   = 0
score_p2   = 0
state      = "playing"   
winner     = ""

# Smooth paddle movement
# we lerp (linear interpolate) toward it each frame.
# This makes movement feel smooth instead of jittery.
p1_target_y = HEIGHT // 2   
p2_target_y = HEIGHT // 2   
LERP_SPEED  = 0.18          


def launch_ball():
    """Reset ball to center with a random angled launch."""
    global ball_vx, ball_vy
    ball.center = (WIDTH // 2, HEIGHT // 2)
    angle = random.uniform(-35, 35)
    direction = random.choice([-1, 1])
    rad = math.radians(angle)
    ball_vx = direction * BALL_SPEED_INIT * math.cos(rad)
    ball_vy = BALL_SPEED_INIT * math.sin(rad)


def lerp(current, target, speed):
     return current + (target - current) * speed


def assign_hands(results, frame_width):
    
    p1_hand = None
    p2_hand = None

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            
            wrist_x = hand_lms.landmark[0].x * frame_width
            if wrist_x < frame_width / 2:
                p1_hand = hand_lms   
            else:
                p2_hand = hand_lms   

    return p1_hand, p2_hand


def get_hand_y(hand_lms, frame_height):
    
    fingertip_y_normalized = hand_lms.landmark[8].y  
    return int(fingertip_y_normalized * frame_height)


def draw_dashed_line(surface, color, x, y1, y2, dash=14, gap=10):
    y = y1
    while y < y2:
        pygame.draw.rect(surface, color, (x - 2, y, 4, dash))
        y += dash + gap


def draw_no_hand_indicator(surface, side, active):
    
    if side == "left":
        x = 80
        color = RED
        label = "P1"
    else:
        x = WIDTH - 80
        color = BLUE
        label = "P2"

    dot_color = GREEN if active else GRAY
    pygame.draw.circle(surface, dot_color, (x, 30), 10)
    txt = font_small.render(f"{label} {'✓' if active else 'NO HAND'}", True, dot_color)
    surface.blit(txt, (x - txt.get_width() // 2, 45))



launch_ball()


#  MAIN GAME LOOP
#  Each frame:
#   A) Read webcam frame
#   B) Run MediaPipe hand detection on it
#   C) Handle pygame events (quit, restart)
#   D) Update paddle targets from hand positions
#   E) Update ball position + collisions + scoring
#   F) Draw: webcam -> overlay -> paddles -> ball -> UI

while True:

      
    ret, frame = cap.read()
    if not ret:
        continue  

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    
    results = hands_detector.process(frame_rgb)
    p1_hand, p2_hand = assign_hands(results, frame_w)

   
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
            if event.key == pygame.K_q:   
                cap.release()
                pygame.quit()
                sys.exit()


            if event.key == pygame.K_r and state == "win":
                score_p1 = score_p2 = 0
                winner = ""
                state = "playing"
                launch_ball()

   
    if p1_hand:
        hand_y = get_hand_y(p1_hand, frame_h)
        p1_target_y = hand_y - PADDLE_H // 2  
    if p2_hand:
        hand_y = get_hand_y(p2_hand, frame_h)
        p2_target_y = hand_y - PADDLE_H // 2

    # Smooth movement via lerp
    p1.y = int(lerp(p1.y, p1_target_y, LERP_SPEED))
    p2.y = int(lerp(p2.y, p2_target_y, LERP_SPEED))

   
    p1.y = max(0, min(HEIGHT - PADDLE_H, p1.y))
    p2.y = max(0, min(HEIGHT - PADDLE_H, p2.y))

    
    if state == "playing":

        ball.x += int(ball_vx)
        ball.y += int(ball_vy)

        
        if ball.top <= 0:
            ball.top = 0
            ball_vy = abs(ball_vy)
        if ball.bottom >= HEIGHT:
            ball.bottom = HEIGHT
            ball_vy = -abs(ball_vy)

        
        if ball.colliderect(p1) and ball_vx < 0:
            hit_pos = (ball.centery - p1.centery) / (PADDLE_H / 2)
            angle   = hit_pos * 55
            speed   = min(math.hypot(ball_vx, ball_vy) + 0.5, BALL_SPEED_MAX)
            rad     = math.radians(angle)
            ball_vx =  abs(speed * math.cos(rad))
            ball_vy =       speed * math.sin(rad)
            ball.left = p1.right

       
        if ball.colliderect(p2) and ball_vx > 0:
            hit_pos = (ball.centery - p2.centery) / (PADDLE_H / 2)
            angle   = hit_pos * 55
            speed   = min(math.hypot(ball_vx, ball_vy) + 0.5, BALL_SPEED_MAX)
            rad     = math.radians(angle)
            ball_vx = -abs(speed * math.cos(rad))
            ball_vy =       speed * math.sin(rad)
            ball.right = p2.left

        
        if ball.right < 0:
            score_p2 += 1
            if score_p2 >= WINNING_SCORE:
                state = "win"
                winner = "P2"
            else:
                launch_ball()

        
        if ball.left > WIDTH:
            score_p1 += 1
            if score_p1 >= WINNING_SCORE:
                state = "win"
                winner = "P1"
            else:
                launch_ball()

    
    frame_surface = pygame.surfarray.make_surface(
        cv2.transpose(frame_rgb)
    )
    screen.blit(frame_surface, (0, 0))

    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))  
    screen.blit(overlay, (0, 0))

    
    draw_dashed_line(screen, GRAY, WIDTH // 2, 0, HEIGHT)

   
    pygame.draw.rect(screen, RED,  p1, border_radius=8)
    pygame.draw.rect(screen, BLUE, p2, border_radius=8)

    
    pygame.draw.rect(screen, WHITE, ball, border_radius=5)

    
    s1 = font_score.render(str(score_p1), True, RED)
    s2 = font_score.render(str(score_p2), True, BLUE)
    screen.blit(s1, (WIDTH // 2 - 140 - s1.get_width(), 20))
    screen.blit(s2, (WIDTH // 2 + 140, 20))

    
    draw_no_hand_indicator(screen, "left",  p1_hand is not None)
    draw_no_hand_indicator(screen, "right", p2_hand is not None)

    
    if p1_hand:
        tip_x = int(p1_hand.landmark[8].x * frame_w)
        tip_y = int(p1_hand.landmark[8].y * frame_h)
        pygame.draw.circle(screen, RED,  (tip_x, tip_y), 10)
        pygame.draw.circle(screen, WHITE,(tip_x, tip_y), 10, 2)

    if p2_hand:
        tip_x = int(p2_hand.landmark[8].x * frame_w)
        tip_y = int(p2_hand.landmark[8].y * frame_h)
        pygame.draw.circle(screen, BLUE, (tip_x, tip_y), 10)
        pygame.draw.circle(screen, WHITE,(tip_x, tip_y), 10, 2)

    
    if state == "win":
        win_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        win_overlay.fill((0, 0, 0, 180))
        screen.blit(win_overlay, (0, 0))

        color = RED if winner == "P1" else BLUE
        wtxt = font_score.render(f"{winner}  WINS!", True, color)
        screen.blit(wtxt, (WIDTH // 2 - wtxt.get_width() // 2, HEIGHT // 2 - 60))

        rtxt = font_med.render("Press R to play again  |  Q to quit", True, WHITE)
        screen.blit(rtxt, (WIDTH // 2 - rtxt.get_width() // 2, HEIGHT // 2 + 40))

    pygame.display.flip()
    clock.tick(FPS)
