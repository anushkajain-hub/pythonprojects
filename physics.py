"""
SafeX - Smart Intersection Safety System
Detects pedestrians on crossings AND vehicles from blind T-junctions
Built for Pune intersection safety
"""

import cv2
import numpy as np
import time

# ─────────────────────────────────────────
# CONFIGURATION — tweak these as needed
# ─────────────────────────────────────────
USE_WEBCAM = True          # True = live webcam | False = use VIDEO_PATH
VIDEO_PATH = "pune_junction.mp4"  # your recorded Pune footage

# Zones (as % of frame) — adjust after running once
CROSSING_ZONE = (0.2, 0.6, 0.8, 0.95)    # (x1%, y1%, x2%, y2%) — zebra crossing area
BLINDSPOT_ZONE = (0.0, 0.0, 0.25, 0.8)   # left side blind T-junction entry

ALERT_COOLDOWN = 3  # seconds between repeated alerts

# ─────────────────────────────────────────
# LOAD MODELS
# ─────────────────────────────────────────
# HOG pedestrian detector (built into OpenCV — no download needed)
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Background subtractor for vehicle/motion detection from blind side
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=50, detectShadows=False
)

# ─────────────────────────────────────────
# STATE
# ─────────────────────────────────────────
last_pedestrian_alert = 0
last_blindspot_alert = 0
pedestrian_detected = False
blindspot_detected = False

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_zone_pixels(frame, zone_pct):
    """Convert % zone to pixel coordinates"""
    h, w = frame.shape[:2]
    x1 = int(zone_pct[0] * w)
    y1 = int(zone_pct[1] * h)
    x2 = int(zone_pct[2] * w)
    y2 = int(zone_pct[3] * h)
    return x1, y1, x2, y2

def box_in_zone(bx, by, bw, bh, zone_pixels):
    """Check if a detected box overlaps with the zone"""
    zx1, zy1, zx2, zy2 = zone_pixels
    cx = bx + bw // 2
    cy = by + bh // 2
    return zx1 < cx < zx2 and zy1 < cy < zy2

def draw_alert_overlay(frame, message, color):
    """Flash a colored alert overlay on the frame"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), color, -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    cv2.putText(frame, message,
                (30, frame.shape[0] // 2),
                cv2.FONT_HERSHEY_DUPLEX, 1.4, (255, 255, 255), 3)

def simulate_low_light(frame):
    """Darken frame to simulate night conditions"""
    return cv2.convertScaleAbs(frame, alpha=0.4, beta=0)

# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────
def run():
    global last_pedestrian_alert, last_blindspot_alert
    global pedestrian_detected, blindspot_detected

    # Open video source
    cap = cv2.VideoCapture(0 if USE_WEBCAM else VIDEO_PATH)
    if not cap.isOpened():
        print("Could not open video source.")
        print("If using webcam, make sure it is connected.")
        print("If using video file, check VIDEO_PATH is correct.")
        return

    print("SafeX Running — Press Q to quit | N to toggle night mode")
    night_mode = False
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop video if it ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (800, 600))
        display = frame.copy()
        frame_count += 1

        # Toggle night simulation
        if night_mode:
            display = simulate_low_light(display)

        h, w = display.shape[:2]
        now = time.time()

        # ── GET ZONE PIXELS ──
        cz = get_zone_pixels(display, CROSSING_ZONE)   # crossing zone
        bz = get_zone_pixels(display, BLINDSPOT_ZONE)  # blindspot zone

        # ── DRAW ZONES ──
        cv2.rectangle(display, (cz[0], cz[1]), (cz[2], cz[3]), (0, 255, 255), 2)
        cv2.putText(display, "CROSSING ZONE", (cz[0]+5, cz[1]-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.rectangle(display, (bz[0], bz[1]), (bz[2], bz[3]), (255, 165, 0), 2)
        cv2.putText(display, "BLIND SPOT", (bz[0]+5, bz[1]+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)

        # ── PEDESTRIAN DETECTION (every 3 frames for speed) ──
        pedestrian_detected = False
        if frame_count % 3 == 0:
            gray = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
            # Equalize histogram to improve low-light detection
            gray = cv2.equalizeHist(gray)
            boxes, _ = hog.detectMultiScale(
                gray, winStride=(8, 8), padding=(4, 4), scale=1.05
            )
            for (x, y, ww, hh) in boxes:
                if box_in_zone(x, y, ww, hh, cz):
                    pedestrian_detected = True
                    cv2.rectangle(display, (x, y), (x+ww, y+hh), (0, 0, 255), 3)
                    cv2.putText(display, "PEDESTRIAN", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # ── BLIND SPOT VEHICLE DETECTION (motion based) ──
        blindspot_detected = False
        fg_mask = bg_subtractor.apply(frame)
        # Only look at blind spot zone
        blind_region = fg_mask[bz[1]:bz[3], bz[0]:bz[2]]
        motion_pixels = cv2.countNonZero(blind_region)
        if motion_pixels > 2000:  # significant motion = vehicle
            blindspot_detected = True
            cv2.putText(display, "VEHICLE DETECTED", (bz[0]+5, bz[3]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

        # ── ALERTS ──
        if pedestrian_detected and blindspot_detected:
            # BOTH — maximum danger
            if now - max(last_pedestrian_alert, last_blindspot_alert) > ALERT_COOLDOWN:
                draw_alert_overlay(display, "DANGER! PEDESTRIAN + VEHICLE!", (0, 0, 200))
                last_pedestrian_alert = now
                last_blindspot_alert = now
                print(f"[{time.strftime('%H:%M:%S')}] MAXIMUM ALERT — Both detected!")

        elif pedestrian_detected:
            if now - last_pedestrian_alert > ALERT_COOLDOWN:
                draw_alert_overlay(display, "PEDESTRIAN ON CROSSING!", (0, 0, 180))
                last_pedestrian_alert = now
                print(f"[{time.strftime('%H:%M:%S')}] Pedestrian on crossing!")

        elif blindspot_detected:
            if now - last_blindspot_alert > ALERT_COOLDOWN:
                draw_alert_overlay(display, "VEHICLE IN BLIND SPOT!", (0, 100, 200))
                last_blindspot_alert = now
                print(f"[{time.strftime('%H:%M:%S')}] Vehicle in blind spot!")

        # ── STATUS BAR ──
        status_color = (0, 200, 0)  # green = safe
        status_text = "SAFE"
        if pedestrian_detected or blindspot_detected:
            status_color = (0, 0, 255)
            status_text = "ALERT"

        cv2.rectangle(display, (0, h-40), (w, h), (30, 30, 30), -1)
        cv2.putText(display,
                    f"SafeX | Status: {status_text} | Night: {'ON' if night_mode else 'OFF'} | N=night Q=quit",
                    (10, h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

        cv2.imshow("SafeX - Smart Intersection Safety System", display)

        # ── KEY CONTROLS ──
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            night_mode = not night_mode
            print(f"Night mode: {'ON' if night_mode else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()
    print("SafeX stopped.")

if __name__ == "__main__":
    run()