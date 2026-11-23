"""
utils.py - small helpers shared by every module (works on Windows, Linux, macOS)
"""
import os
import sys

if os.name == "nt":
    os.system("")          # lets the Windows console understand colour codes

# ---------- colours ----------
RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
RED, GREEN, YELLOW = "\033[91m", "\033[92m", "\033[93m"
BLUE, CYAN, WHITE, GRAY = "\033[94m", "\033[96m", "\033[97m", "\033[90m"


def color(text, *codes):
    """Wrap text in colour codes:  color('hi', GREEN, BOLD)"""
    return "".join(codes) + str(text) + RESET


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg="\nPress Enter to continue..."):
    input(msg)


def header(title, width=76):
    print(color("=" * width, CYAN))
    print(color(title.center(width), CYAN, BOLD))
    print(color("=" * width, CYAN))


def ask_int(prompt, lo, hi, default=None):
    """Ask until the user types an integer in [lo, hi]. Enter = default."""
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
            if lo <= value <= hi:
                return value
        except ValueError:
            pass
        print(f"  Please enter a whole number between {lo} and {hi}.")


def ask_menu(title, options):
    """
    options: list of strings. Shows 1..n and returns the chosen number (1-based).
    """
    print(color(f"\n{title}", BOLD))
    for i, text in enumerate(options, start=1):
        print(f"  {i}) {text}")
    return ask_int("\nChoose > ", 1, len(options))


def bar(value, max_value, width=28, fill="█"):
    """Text bar, e.g. ██████████░░░░"""
    if max_value <= 0:
        filled = 0
    else:
        filled = max(1 if value > 0 else 0, round(width * value / max_value))
    return fill * filled + "░" * (width - filled)


def get_key():
    """
    Read ONE key press without waiting for Enter.
    Returns 'left', 'right', or a lower-case character.
    """
    if os.name == "nt":
        import msvcrt
        key = msvcrt.getch()
        if key in (b"\x00", b"\xe0"):
            arrow = msvcrt.getch()
            return {b"K": "left", b"M": "right"}.get(arrow, "")
        if key == b"\x03":
            raise KeyboardInterrupt
        try:
            return key.decode("utf-8").lower()
        except UnicodeDecodeError:
            return ""
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch == "\x1b":
            rest = sys.stdin.read(2)
            return {"[C": "right", "[D": "left"}.get(rest, "")
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
