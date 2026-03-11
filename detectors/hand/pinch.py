"""Hand-only detector for stable pinch events."""

from dataclasses import dataclass, field
from time import monotonic

from detectors.core.cooldown import Cooldown
from detectors.core.event_types import GestureEvent
from detectors.core.geometry import average_hand_size, distance_2d
from detectors.core.smoothing import EmaSmoother

THUMB_TIP = 4
INDEX_TIP = 8


@dataclass
class PinchDetector:
    """Emit one event when the thumb and index finger pinch together."""

    threshold_ratio: float = 0.24
    confirmation_frames: int = 2
    cooldown_seconds: float = 0.5
    smoothing_alpha: float = 0.35
    matched_frames: int = field(default=0, init=False)
    cooldown: Cooldown = field(init=False)
    distance_filter: EmaSmoother = field(init=False)

    def __post_init__(self) -> None:
        self.cooldown = Cooldown(self.cooldown_seconds)
        self.distance_filter = EmaSmoother(self.smoothing_alpha)

    def update(self, hand_landmarks, now: float | None = None) -> GestureEvent | None:
        """Return a pinch event after the fingertips stay together."""
        # 1. Stop early when a hand is not available.
        if not hand_landmarks:
            self._clear_pending()
            return None

        current_time = monotonic() if now is None else now
        hand_size = average_hand_size(hand_landmarks)
        pinch_radius = max(hand_size * self.threshold_ratio, 0.01)

        # 2. Measure the thumb-to-index distance and smooth short jitter.
        raw_distance = distance_2d(hand_landmarks[THUMB_TIP], hand_landmarks[INDEX_TIP])
        pinch_distance = self.distance_filter.update(raw_distance)
        if pinch_distance > pinch_radius:
            self._clear_pending()
            return None

        # 3. Confirm the pinch across frames, then emit one cooled-down event.
        self.matched_frames += 1
        if self.matched_frames < self.confirmation_frames or not self.cooldown.is_ready(current_time):
            return None

        self.cooldown.trigger(current_time)
        self._clear_pending()
        confidence = max(0.0, 1.0 - (pinch_distance / pinch_radius))
        return GestureEvent(
            name="pinch",
            confidence=confidence,
            timestamp=current_time,
            metadata={"distance": pinch_distance, "threshold": pinch_radius},
        )

    def reset(self) -> None:
        """Clear pending state and reopen the cooldown."""
        self._clear_pending()
        self.cooldown.reset()

    def _clear_pending(self) -> None:
        """Drop the current confirmation streak."""
        self.matched_frames = 0
        self.distance_filter.reset()
