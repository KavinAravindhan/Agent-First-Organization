import json
import time
from typing import Any, Dict, List

class TraceLogger:
    """
    Captures a chain of calls or debug events for better traceability.
    """

    def __init__(self):
        self._traces: List[Dict[str, Any]] = []
        self.active = False

    def start_trace(self, description: str = "New trace session started"):
        self.active = True
        self._log_event(description)

    def log_event(self, event: str, data: Dict[str, Any] = None):
        if not self.active:
            return
        record = {
            "timestamp": time.time(),
            "event": event,
            "data": data if data else {}
        }
        self._traces.append(record)

    def _log_event(self, event: str):
        # Internal convenience
        self.log_event(event, {})

    def end_trace(self, description: str = "Trace session ended"):
        if self.active:
            self._log_event(description)
            self.active = False

    def get_trace_records(self) -> List[Dict[str, Any]]:
        return self._traces

    def export_trace(self, filepath: str):
        """
        Write all trace records to a JSON file.
        """
        with open(filepath, "w") as f:
            json.dump(self._traces, f, indent=2)
