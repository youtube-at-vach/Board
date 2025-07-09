# utils.py

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_MODERATOR = "\033[94m"  # Blue
COLOR_AGENT_A = "\033[92m"    # Green
COLOR_AGENT_B = "\033[93m"    # Yellow
COLOR_AGENT_C = "\033[95m"    # Magenta
COLOR_DEBUG = "\033[90m"      # Grey

DEBUG_MODE = False

def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print(COLOR_DEBUG, end="")
        print(*args, **kwargs)
        print(COLOR_RESET, end="")
