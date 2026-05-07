import sys
import time
import threading
from contextlib import contextmanager


@contextmanager
def spinner(message: str = "Working"):
    """
    Simple terminal spinner for long-running background work.
    Stops automatically when the wrapped block finishes.
    """

    stop_event = threading.Event()
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def run():
        index = 0

        while not stop_event.is_set():
            frame = frames[index % len(frames)]
            sys.stdout.write(f"\r {frame} {message}...")
            sys.stdout.flush()
            index += 1
            time.sleep(0.08)

        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
        sys.stdout.flush()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    try:
        yield
    finally:
        stop_event.set()
        thread.join()