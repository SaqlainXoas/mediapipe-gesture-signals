"""Hand-only detector for stable multi-finger touch events."""

from dataclasses import dataclass, field
from itertools import combinations
from time import monotonic

from detectors.core.cooldown import Cooldown
from detectors.core.event_types import GestureEvent
from detectors.core.geometry import average_hand_size, distance_2d
from detectors.core.smoothing import EmaSmoother


@dataclass
class FingerTouchDetector:
    """Emit one event when the chosen fingertips cluster together."""

    finger_indices: tuple[int, ...] = (8, 12)
    threshold_ratio: float = 0.3
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
        """Return an event when the chosen fingertips cluster together."""
        # 1. Stop early when the hand or finger selection is incomplete.
        if not hand_landmarks or len(self.finger_indices) < 2:
            self._clear_pending()
            return None

        current_time = monotonic() if now is None else now
        hand_size = average_hand_size(hand_landmarks)
        touch_radius = max(hand_size * self.threshold_ratio, 0.01)

        # 2. Track the widest gap in the finger cluster and smooth the signal.
        raw_distance = max(
            distance_2d(hand_landmarks[a], hand_landmarks[b])
            for a, b in combinations(self.finger_indices, 2)
        )
        max_distance = self.distance_filter.update(raw_distance)
        if max_distance > touch_radius:
            self._clear_pending()
            return None

        # 3. Confirm the cluster across frames, then emit one cooled-down event.
        self.matched_frames += 1
        if self.matched_frames < self.confirmation_frames or not self.cooldown.is_ready(current_time):
            return None

        self.cooldown.trigger(current_time)
        self._clear_pending()
        confidence = max(0.0, 1.0 - (max_distance / touch_radius))
        return GestureEvent(
            name="finger_touch",
            confidence=confidence,
            timestamp=current_time,
            metadata={
                "distance": max_distance,
                "threshold": touch_radius,
                "fingers": ",".join(str(index) for index in self.finger_indices),
            },
        )

    def reset(self) -> None:
        """Clear pending state and reopen the cooldown."""
        self._clear_pending()
        self.cooldown.reset()

    def _clear_pending(self) -> None:
        """Drop the current confirmation streak."""
        self.matched_frames = 0
        self.distance_filter.reset()
