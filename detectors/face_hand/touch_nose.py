"""Face-and-hand detector for stable touch-nose events."""

from dataclasses import dataclass, field
from time import monotonic

from detectors.core.cooldown import Cooldown
from detectors.core.event_types import GestureEvent
from detectors.core.geometry import average_face_size, distance_3d
from detectors.core.smoothing import EmaSmoother

NOSE_LANDMARKS = (1, 4, 5, 6, 19, 20, 94, 125)
INDEX_FINGER_TIP = 8


@dataclass
class TouchNoseDetector:
    """Emit one event when the index fingertip stays near the nose."""

    threshold_ratio: float = 0.18
    confirmation_frames: int = 3
    cooldown_seconds: float = 0.6
    smoothing_alpha: float = 0.35
    matched_frames: int = field(default=0, init=False)
    cooldown: Cooldown = field(init=False)
    distance_filter: EmaSmoother = field(init=False)

    def __post_init__(self) -> None:
        self.cooldown = Cooldown(self.cooldown_seconds)
        self.distance_filter = EmaSmoother(self.smoothing_alpha)

    def update(self, face_landmarks, hand_landmarks, now: float | None = None) -> GestureEvent | None:
        """Return a touch event after the fingertip stays near the nose."""
        # 1. Stop early when either landmark stream is missing.
        if not face_landmarks or not hand_landmarks:
            self._clear_pending()
            return None

        current_time = monotonic() if now is None else now
        finger_tip = hand_landmarks[INDEX_FINGER_TIP]
        face_size = average_face_size(face_landmarks)
        touch_radius = max(face_size * self.threshold_ratio, 0.01)

        # 2. Measure the closest fingertip-to-nose distance and smooth it.
        raw_distance = min(
            distance_3d(finger_tip, face_landmarks[landmark_index])
            for landmark_index in NOSE_LANDMARKS
        )
        closest_distance = self.distance_filter.update(raw_distance)

        if closest_distance > touch_radius:
            self._clear_pending()
            return None

        # 3. Confirm the touch across frames, then emit one cooled-down event.
        self.matched_frames += 1
        if self.matched_frames < self.confirmation_frames:
            return None
        if not self.cooldown.is_ready(current_time):
            return None

        self.cooldown.trigger(current_time)
        self._clear_pending()
        confidence = max(0.0, 1.0 - (closest_distance / touch_radius))
        return GestureEvent(
            name="touch_nose",
            confidence=confidence,
            timestamp=current_time,
            metadata={
                "distance": closest_distance,
                "threshold": touch_radius,
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
