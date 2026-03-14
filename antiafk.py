import time
import random
import threading
import sys

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController, Listener
    from pynput.mouse import Controller as MouseController
except ImportError:
    print("pynput is required. Install it with:")
    print("  pip install pynput")
    sys.exit(1)

keyboard = KeyboardController()
mouse = MouseController()

# === Configuration ===
TOGGLE_KEY = Key.f6           # Press F6 to toggle on/off
INTERVAL_MIN = 3.0            # Min seconds between actions
INTERVAL_MAX = 7.0            # Max seconds between actions
MOUSE_MOVE_RANGE = 60         # Max pixels to move mouse
ENABLE_JUMP = True
ENABLE_SNEAK = False
ENABLE_SWING = True           # Left click (swing hand)
ENABLE_MOUSE_MOVE = True
ENABLE_MOVEMENT = True
ENABLE_HOTBAR_SWITCH = True
# =====================

running = False
stop_event = threading.Event()


def random_sleep(min_s, max_s):
    """Sleep for a random duration, checking stop_event frequently."""
    duration = random.uniform(min_s, max_s)
    end = time.time() + duration
    while time.time() < end and not stop_event.is_set():
        time.sleep(0.1)


def tap_key(key, hold=0.05):
    """Press and release a key."""
    keyboard.press(key)
    time.sleep(hold)
    keyboard.release(key)


def do_jump():
    tap_key(Key.space)


def do_sneak():
    tap_key(Key.shift_l, hold=random.uniform(0.1, 0.5))


def do_swing():
    from pynput.mouse import Button
    mouse.click(Button.left)


def do_mouse_move():
    dx = random.randint(-MOUSE_MOVE_RANGE, MOUSE_MOVE_RANGE)
    dy = random.randint(-MOUSE_MOVE_RANGE // 2, MOUSE_MOVE_RANGE // 2)
    # Smooth movement in small steps
    steps = random.randint(5, 15)
    for i in range(steps):
        mouse.move(dx // steps, dy // steps)
        time.sleep(0.01)


def do_movement():
    keys = ['w', 'a', 's', 'd']
    key = random.choice(keys)
    hold_time = random.uniform(0.3, 1.0)
    keyboard.press(key)
    time.sleep(hold_time)
    keyboard.release(key)


def do_hotbar_switch():
    slot = str(random.randint(1, 9))
    tap_key(slot)


def antiafk_loop():
    global running
    print("[AntiAFK] Started! Press F6 to stop.")

    while not stop_event.is_set():
        actions = []
        if ENABLE_JUMP:
            actions.append(("Jump", do_jump))
        if ENABLE_SNEAK:
            actions.append(("Sneak", do_sneak))
        if ENABLE_SWING:
            actions.append(("Swing", do_swing))
        if ENABLE_MOUSE_MOVE:
            actions.append(("Mouse Move", do_mouse_move))
        if ENABLE_MOVEMENT:
            actions.append(("Movement", do_movement))
        if ENABLE_HOTBAR_SWITCH:
            actions.append(("Hotbar Switch", do_hotbar_switch))

        if actions:
            name, action = random.choice(actions)
            try:
                action()
            except Exception:
                pass

        random_sleep(INTERVAL_MIN, INTERVAL_MAX)

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
    print(f"  Interval: {INTERVAL_MIN}-{INTERVAL_MAX}s")
    print(f"  Jump: {ENABLE_JUMP}")
    print(f"  Sneak: {ENABLE_SNEAK}")
    print(f"  Swing: {ENABLE_SWING}")
    print(f"  Mouse Move: {ENABLE_MOUSE_MOVE}")
    print(f"  Movement: {ENABLE_MOVEMENT}")
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
