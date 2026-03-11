"""Face-only detector for continuous head-tilt state."""

from dataclasses import dataclass, field

from detectors.core.geometry import angle_degrees
from detectors.core.smoothing import EmaSmoother

LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263


@dataclass
class TiltDetector:
    """Return left/right tilt state from the eye line angle."""

    threshold_degrees: float = 12.0
    smoothing_alpha: float = 0.3
    angle_filter: EmaSmoother = field(init=False)

    def __post_init__(self) -> None:
        self.angle_filter = EmaSmoother(self.smoothing_alpha)

    def update(self, face_landmarks) -> dict[str, bool]:
        """Return left and right tilt flags from the smoothed eye-line angle."""
        if not face_landmarks:
            self.angle_filter.reset()
            return {"tilt_left": False, "tilt_right": False}

        angle = self.angle_filter.update(
            angle_degrees(face_landmarks[LEFT_EYE_OUTER], face_landmarks[RIGHT_EYE_OUTER])
        )
        return {
            "tilt_left": angle < -self.threshold_degrees,
            "tilt_right": angle > self.threshold_degrees,
        }

    def reset(self) -> None:
        """Clear the smoothed tilt angle."""
        self.angle_filter.reset()
