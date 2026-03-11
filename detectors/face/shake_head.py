"""Face-only detector for stable shake-head events."""

from dataclasses import dataclass, field
from time import monotonic

from detectors.core.cooldown import Cooldown
from detectors.core.event_types import GestureEvent
from detectors.core.geometry import average_face_size, midpoint_2d
from detectors.core.smoothing import EmaSmoother

LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
NOSE_TIP = 1


@dataclass
class ShakeHeadDetector:
    """Emit one event when the head moves to one side and back across center."""

    threshold_ratio: float = 0.12
    opposite_side_ratio: float = 0.06
    cooldown_seconds: float = 1.0
    smoothing_alpha: float = 0.35
    direction: int = field(default=0, init=False)
    peak_offset: float = field(default=0.0, init=False)
    baseline_filter: EmaSmoother = field(init=False)
    position_filter: EmaSmoother = field(init=False)
    cooldown: Cooldown = field(init=False)

    def __post_init__(self) -> None:
        self.baseline_filter = EmaSmoother(0.12)
        self.position_filter = EmaSmoother(self.smoothing_alpha)
        self.cooldown = Cooldown(self.cooldown_seconds)

    def update(self, face_landmarks, now: float | None = None) -> GestureEvent | None:
        """Return a shake event after a side-to-side head motion."""
        # 1. Reset when the face disappears so stale motion does not linger.
        if not face_landmarks:
            self._clear_motion()
            return None

        current_time = monotonic() if now is None else now
        face_size = average_face_size(face_landmarks)
        eye_midpoint = midpoint_2d(face_landmarks[LEFT_EYE_OUTER], face_landmarks[RIGHT_EYE_OUTER])
        nose_x = face_landmarks[NOSE_TIP].x
        motion_value = self.position_filter.update((nose_x - eye_midpoint[0]) / face_size)

        # 2. Learn a calm baseline, then lock onto the first strong direction.
        if self.direction == 0:
            baseline = self.baseline_filter.update(motion_value)
            displacement = motion_value - baseline
            if abs(displacement) > self.threshold_ratio:
                self.direction = 1 if displacement > 0 else -1
                self.peak_offset = abs(displacement)
            return None

        baseline = self.baseline_filter.value if self.baseline_filter.value is not None else motion_value
        displacement = motion_value - baseline
        self.peak_offset = max(self.peak_offset, abs(displacement))

        # 3. Wait for a clear cross back through center before emitting.
        crossed_center = displacement * self.direction < -self.opposite_side_ratio
        if crossed_center and self.cooldown.is_ready(current_time):
            confidence = min(1.0, self.peak_offset / (self.threshold_ratio * 2.0))
            self.cooldown.trigger(current_time)
            peak = self.peak_offset
            self._clear_motion()
            self.baseline_filter.update(motion_value)
            return GestureEvent(
                name="shake_head",
                confidence=confidence,
                timestamp=current_time,
                metadata={"peak_offset": peak},
            )

        if abs(displacement) < self.threshold_ratio * 0.2:
            self._clear_motion()
            self.baseline_filter.update(motion_value)
        return None

    def reset(self) -> None:
        """Clear motion state, smoothing state, and cooldown state."""
        self._clear_motion()
        self.baseline_filter.reset()
        self.position_filter.reset()
        self.cooldown.reset()

    def _clear_motion(self) -> None:
        """Forget the current shake in progress."""
        self.direction = 0
        self.peak_offset = 0.0
