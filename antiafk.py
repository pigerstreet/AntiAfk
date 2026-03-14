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
ACTION_INTERVAL_MIN = 3.0     # Min seconds between random actions
ACTION_INTERVAL_MAX = 7.0     # Max seconds between random actions
MOUSE_MOVE_RANGE = 60         # Max pixels to move mouse
ENABLE_JUMP = True
ENABLE_SNEAK = False
ENABLE_SWING = True           # Left click (swing hand)
ENABLE_MOUSE_MOVE = True
ENABLE_HOTBAR_SWITCH = False  # Disabled by default - uses custom keys

# Movement settings
WALK_DURATION = 2.0           # Seconds to walk in each direction
PAUSE_DURATION = 0.5          # Seconds to pause between directions
MOVEMENT_KEYS = ['w', 'a', 's', 'd']  # Forward, Left, Back, Right

# Your hotbar keybinds (slots 1-9)
HOTBAR_KEYS = ['q', 'f', '3', '4', Key.backspace, 'z', 'x', 'c', 'v']
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
    steps = random.randint(5, 15)
    for i in range(steps):
        if stop_event.is_set():
            return
        mouse.move(dx // steps, dy // steps)
        time.sleep(0.01)


def do_hotbar_switch():
    key = random.choice(HOTBAR_KEYS)
    tap_key(key)


def continuous_movement():
    """Continuously walk in a square pattern: forward -> right -> back -> left."""
    direction_index = 0

    while not stop_event.is_set():
        key = MOVEMENT_KEYS[direction_index]
        walk_time = WALK_DURATION + random.uniform(-0.5, 0.5)

        # Hold the movement key
        keyboard.press(key)
        end = time.time() + walk_time
        while time.time() < end and not stop_event.is_set():
            time.sleep(0.05)
        keyboard.release(key)

        if stop_event.is_set():
            break

        # Brief pause between directions
        time.sleep(PAUSE_DURATION)

        # Next direction
        direction_index = (direction_index + 1) % 4

    # Make sure all movement keys are released
    for key in MOVEMENT_KEYS:
        keyboard.release(key)


def random_actions():
    """Periodically perform random actions (jump, swing, look around, etc.)."""
    while not stop_event.is_set():
        actions = []
        if ENABLE_JUMP:
            actions.append(do_jump)
        if ENABLE_SNEAK:
            actions.append(do_sneak)
        if ENABLE_SWING:
            actions.append(do_swing)
        if ENABLE_MOUSE_MOVE:
            actions.append(do_mouse_move)
        if ENABLE_HOTBAR_SWITCH:
            actions.append(do_hotbar_switch)

        if actions:
            action = random.choice(actions)
            try:
                action()
            except Exception:
                pass

        random_sleep(ACTION_INTERVAL_MIN, ACTION_INTERVAL_MAX)


def antiafk_loop():
    global running
    print("[AntiAFK] Started! Press F6 to stop.")

    # Run continuous movement and random actions in parallel
    move_thread = threading.Thread(target=continuous_movement, daemon=True)
    action_thread = threading.Thread(target=random_actions, daemon=True)

    move_thread.start()
    action_thread.start()

    move_thread.join()
    action_thread.join()

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
    print(f"  Action Interval: {ACTION_INTERVAL_MIN}-{ACTION_INTERVAL_MAX}s")
    print(f"  Movement: Continuous (square pattern)")
    print(f"  Walk Duration: {WALK_DURATION}s per direction")
    print(f"  Jump: {ENABLE_JUMP}")
    print(f"  Sneak: {ENABLE_SNEAK}")
    print(f"  Swing: {ENABLE_SWING}")
    print(f"  Mouse Move: {ENABLE_MOUSE_MOVE}")
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
