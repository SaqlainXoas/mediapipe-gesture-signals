from dataclasses import dataclass, field
from time import monotonic


@dataclass
class Cooldown:
    """Allow one event, then block until the cooldown expires."""

    seconds: float
    ready_at: float = field(default=0.0, init=False)

    def is_ready(self, now: float | None = None) -> bool:
        """Return True when the cooldown window has expired."""
        current_time = monotonic() if now is None else now
        return current_time >= self.ready_at

    def trigger(self, now: float | None = None) -> None:
        """Start a new cooldown window from the current time."""
        current_time = monotonic() if now is None else now
        self.ready_at = current_time + self.seconds

    def reset(self) -> None:
        """Allow the next event immediately."""
        self.ready_at = 0.0
