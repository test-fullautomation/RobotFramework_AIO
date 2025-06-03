import sys
import traceback

def customize_color_traceback(exc_type, exc_value, exc_traceback):
    """
    Customizes the default Python traceback with neon pink-lilac and bright red colors.

    This function replaces the system's default exception hook to display unhandled
    exceptions using colored ANSI escape sequences.

    """
    neon_pink_lilac = "\033[38;2;255;160;255m"
    bright_red = "\033[38;2;255;60;60m"
    reset = "\033[0m"

    tb = traceback.TracebackException(exc_type, exc_value, exc_traceback, capture_locals=False)

    # Print header line (no color)
    print("Traceback (most recent call last):")

    for frame in tb.stack:
        # Build file path with quotes colored
        colored_path = f'{neon_pink_lilac}"{frame.filename}"{reset}'
        colored_lineno = f'{neon_pink_lilac}{frame.lineno}{reset}'
        colored_func = f'{neon_pink_lilac}{frame.name}{reset}'
        print(f'  File {colored_path}, line {colored_lineno}, in {colored_func}')

        # Code line (bright red) if available
        if frame.line:
            print(f"{bright_red}    {frame.line.strip()}{reset}")

        # Include visual indicator line if it exists (from newer Python versions)
        if hasattr(frame, 'colno') and frame.colno is not None:
            caret_line = ' ' * (frame.colno + 3) + '^'
            print(f"{bright_red}{caret_line}{reset}")

    # Print exception type and message in lilac
    print(f"{neon_pink_lilac}{''.join(tb.format_exception_only())}{reset}")

sys.excepthook = customize_color_traceback
