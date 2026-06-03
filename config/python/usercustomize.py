import sys
import traceback

try:
    import readline
    if not hasattr(readline, "backend"):
        readline.backend = "pyreadline3"
except ImportError:
    pass

def customize_color_traceback(exc_type, exc_value, exc_traceback):
    """
    Customizes the default Python traceback with dark lilac and bright red colors.

    This function replaces the system's default exception hook to display unhandled
    exceptions using colored ANSI escape sequences.

    """
    dark_lilac = "\033[38;2;228;39;255m"
    bright_red = "\033[38;2;255;60;60m"
    reset = "\033[0m"

    tb = traceback.TracebackException(exc_type, exc_value, exc_traceback, capture_locals=False)

    # Print header line (no color)
    print("Traceback (most recent call last):")

    for frame in tb.stack:
        # Build file path with quotes colored
        colored_path = f'{dark_lilac}"{frame.filename}"{reset}'
        colored_lineno = f'{dark_lilac}{frame.lineno}{reset}'
        colored_func = f'{dark_lilac}{frame.name}{reset}'
        print(f'  File {colored_path}, line {colored_lineno}, in {colored_func}')

        # Code line (bright red) if available
        if frame.line:
            print(f"{bright_red}    {frame.line.strip()}{reset}")

        # Include visual indicator line if it exists (from newer Python versions)
        if hasattr(frame, 'colno') and frame.colno is not None:
            caret_line = ' ' * (frame.colno + 3) + '^'
            print(f"{bright_red}{caret_line}{reset}")

    # Print exception type and message in lilac
    print(f"{dark_lilac}{''.join(tb.format_exception_only())}{reset}")

sys.excepthook = customize_color_traceback
