from dataclasses import dataclass, field
from time import monotonic


@dataclass(slots=True)
class GestureEvent:
    """Single gesture event emitted by a detector."""

    name: str
    confidence: float = 1.0
    timestamp: float = field(default_factory=monotonic)
    metadata: dict[str, float | str | bool] = field(default_factory=dict)
