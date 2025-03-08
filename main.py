import sys
import threading
from memory_reader import MemoryReader
from combat_log_parser import CombatLogParser
from aggregator import Aggregator
from dps_window import DPSWindow
from worker import combat_log_worker

def main():
    try:
        reader = MemoryReader()
    except Exception as e:
        print("Error initializing MemoryReader:", e)
        sys.exit(1)

    parser = CombatLogParser()
    aggregator = Aggregator()

    # Create and reset the UI
    app = DPSWindow(aggregator)
    app.reset_meter()
    aggregator.reset()

    stop_event = threading.Event()
    worker_thread = threading.Thread(
        target=combat_log_worker,
        args=(reader, parser, aggregator, stop_event),
        daemon=True
    )
    worker_thread.start()

    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        print("Exiting Combat Log service.")

if __name__ == "__main__":
    main()
