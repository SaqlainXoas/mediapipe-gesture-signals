"""Face-only detector for stable nod events."""

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
class NodDetector:
    """Emit one event when the head dips down and comes back up."""

    threshold_ratio: float = 0.18
    confirm_frames: int = 2
    cooldown_seconds: float = 1.0
    smoothing_alpha: float = 0.35
    state: str = field(default="idle", init=False)
    peak_offset: float = field(default=0.0, init=False)
    recovery_frames: int = field(default=0, init=False)
    baseline_filter: EmaSmoother = field(init=False)
    position_filter: EmaSmoother = field(init=False)
    cooldown: Cooldown = field(init=False)

    def __post_init__(self) -> None:
        self.baseline_filter = EmaSmoother(0.12)
        self.position_filter = EmaSmoother(self.smoothing_alpha)
        self.cooldown = Cooldown(self.cooldown_seconds)

    def update(self, face_landmarks, now: float | None = None) -> GestureEvent | None:
        """Return a nod event after a down-and-recover motion pattern."""
        # 1. Reset when the face disappears so stale motion does not linger.
        if not face_landmarks:
            self._clear_motion()
            return None

        current_time = monotonic() if now is None else now
        face_size = average_face_size(face_landmarks)
        eye_midpoint = midpoint_2d(face_landmarks[LEFT_EYE_OUTER], face_landmarks[RIGHT_EYE_OUTER])
        nose_y = face_landmarks[NOSE_TIP].y
        motion_value = self.position_filter.update((nose_y - eye_midpoint[1]) / face_size)

        # 2. Learn a calm baseline, then watch for a clear downward dip.
        if self.state == "idle":
            baseline = self.baseline_filter.update(motion_value)
            if motion_value - baseline > self.threshold_ratio:
                self.state = "down"
                self.peak_offset = motion_value - baseline
            return None

        baseline = self.baseline_filter.value if self.baseline_filter.value is not None else motion_value
        displacement = motion_value - baseline
        self.peak_offset = max(self.peak_offset, displacement)

        # 3. Confirm recovery toward baseline before emitting one nod event.
        recovered = displacement < self.peak_offset - (self.threshold_ratio * 0.6)
        self.recovery_frames = self.recovery_frames + 1 if recovered else 0
        if self.recovery_frames >= self.confirm_frames and self.cooldown.is_ready(current_time):
            peak = self.peak_offset
            confidence = min(1.0, peak / (self.threshold_ratio * 1.8))
            self.cooldown.trigger(current_time)
            self._clear_motion()
            self.baseline_filter.update(motion_value)
            return GestureEvent(
                name="nod",
                confidence=confidence,
                timestamp=current_time,
                metadata={"peak_offset": peak},
            )

        if displacement < self.threshold_ratio * 0.15:
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
        """Forget the current nod in progress."""
        self.state = "idle"
        self.peak_offset = 0.0
        self.recovery_frames = 0
