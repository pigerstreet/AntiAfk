import time
import random
import threading
import sys

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController, Listener
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    print("pynput is required. Install it with:")
    print("  pip install pynput")
    sys.exit(1)

keyboard = KeyboardController()
mouse = MouseController()

# === Configuration ===
TOGGLE_KEY = Key.f6           # Press F6 to toggle on/off
ENABLE_JUMP = True
ENABLE_SNEAK = False
ENABLE_HOTBAR_SWITCH = False

# Movement settings
WALK_DURATION = 5.0           # Seconds to walk in each direction
PAUSE_DURATION = 0.3          # Brief pause between directions
MOVEMENT_KEYS = ['w', 'a', 's', 'd']

# Mouse settings (horizontal only)
MOUSE_SPEED = 3               # Pixels per tick to move
MOUSE_DIRECTION_MIN = 2.0     # Min seconds before changing direction
MOUSE_DIRECTION_MAX = 5.0     # Max seconds before changing direction

# Clicking settings
CLICK_INTERVAL_MIN = 1.0      # Min seconds between clicks
CLICK_INTERVAL_MAX = 4.0      # Max seconds between clicks

# Jump/action interval
ACTION_INTERVAL_MIN = 3.0
ACTION_INTERVAL_MAX = 7.0

# Your hotbar keybinds (slots 1-9)
HOTBAR_KEYS = ['q', 'f', '3', '4', Key.backspace, 'z', 'x', 'c', 'v']
# =====================

running = False
stop_event = threading.Event()


def tap_key(key, hold=0.05):
    keyboard.press(key)
    time.sleep(hold)
    keyboard.release(key)


def continuous_movement():
    """Continuously walk in a square pattern with longer strides."""
    direction_index = 0

    while not stop_event.is_set():
        key = MOVEMENT_KEYS[direction_index]
        walk_time = WALK_DURATION + random.uniform(-1.0, 1.0)

        keyboard.press(key)
        end = time.time() + walk_time
        while time.time() < end and not stop_event.is_set():
            time.sleep(0.05)
        keyboard.release(key)

        if stop_event.is_set():
            break

        time.sleep(PAUSE_DURATION)
        direction_index = (direction_index + 1) % 4

    for key in MOVEMENT_KEYS:
        keyboard.release(key)


def continuous_mouse():
    """Continuously move mouse left and right smoothly."""
    direction = 1  # 1 = right, -1 = left

    while not stop_event.is_set():
        # Pick how long to move in this direction
        duration = random.uniform(MOUSE_DIRECTION_MIN, MOUSE_DIRECTION_MAX)
        speed = MOUSE_SPEED + random.randint(-1, 1)
        end = time.time() + duration

        while time.time() < end and not stop_event.is_set():
            mouse.move(direction * speed, 0)
            time.sleep(0.02)  # ~50 ticks/sec for smooth movement

        # Reverse direction
        direction *= -1


def continuous_clicking():
    """Continuously left click at random intervals."""
    while not stop_event.is_set():
        mouse.click(Button.left)
        # Random wait between clicks
        wait = random.uniform(CLICK_INTERVAL_MIN, CLICK_INTERVAL_MAX)
        end = time.time() + wait
        while time.time() < end and not stop_event.is_set():
            time.sleep(0.1)


def random_actions():
    """Periodically jump, sneak, or switch hotbar."""
    while not stop_event.is_set():
        actions = []
        if ENABLE_JUMP:
            actions.append(lambda: tap_key(Key.space))
        if ENABLE_SNEAK:
            actions.append(lambda: tap_key(Key.shift_l, hold=random.uniform(0.1, 0.5)))
        if ENABLE_HOTBAR_SWITCH:
            actions.append(lambda: tap_key(random.choice(HOTBAR_KEYS)))

        if actions:
            try:
                random.choice(actions)()
            except Exception:
                pass

        wait = random.uniform(ACTION_INTERVAL_MIN, ACTION_INTERVAL_MAX)
        end = time.time() + wait
        while time.time() < end and not stop_event.is_set():
            time.sleep(0.1)


def antiafk_loop():
    global running
    print("[AntiAFK] Started! Press F6 to stop.")

    threads = [
        threading.Thread(target=continuous_movement, daemon=True),
        threading.Thread(target=continuous_mouse, daemon=True),
        threading.Thread(target=continuous_clicking, daemon=True),
        threading.Thread(target=random_actions, daemon=True),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("[AntiAFK] Stopped.")
    running = False


def on_press(key):
    global running
    if key == TOGGLE_KEY:
        if not running:
            running = True
            stop_event.clear()
            thread = threading.Thread(target=antiafk_loop, daemon=True)
            thread.start()
        else:
            stop_event.set()


def main():
    print("=" * 40)
    print("  Minecraft AntiAFK Script")
    print("=" * 40)
    print(f"  Toggle: F6")
    print(f"  Movement: Continuous square pattern ({WALK_DURATION}s/dir)")
    print(f"  Mouse: Continuous left/right panning")
    print(f"  Clicking: Continuous ({CLICK_INTERVAL_MIN}-{CLICK_INTERVAL_MAX}s)")
    print(f"  Jump: {ENABLE_JUMP}")
    print(f"  Sneak: {ENABLE_SNEAK}")
    print(f"  Hotbar Switch: {ENABLE_HOTBAR_SWITCH}")
    print("=" * 40)
    print("Focus your Minecraft window and press F6 to start.")
    print("Press Ctrl+C here to quit.\n")

    with Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            stop_event.set()
            print("\nExiting.")


if __name__ == "__main__":
    main()
