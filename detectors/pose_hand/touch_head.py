"""Pose-and-hand detector for stable touch-head events."""

from dataclasses import dataclass, field
from time import monotonic

from detectors.core.cooldown import Cooldown
from detectors.core.event_types import GestureEvent
from detectors.core.geometry import distance_2d, pose_head_size
from detectors.core.smoothing import EmaSmoother

HEAD_LANDMARKS = (0, 2, 5, 7, 8)
INDEX_FINGER_TIP = 8


@dataclass
class TouchHeadDetector:
    """Emit one event when the index fingertip reaches the head zone."""

    threshold_ratio: float = 0.7
    confirmation_frames: int = 3
    cooldown_seconds: float = 0.8
    smoothing_alpha: float = 0.35
    matched_frames: int = field(default=0, init=False)
    cooldown: Cooldown = field(init=False)
    distance_filter: EmaSmoother = field(init=False)

    def __post_init__(self) -> None:
        self.cooldown = Cooldown(self.cooldown_seconds)
        self.distance_filter = EmaSmoother(self.smoothing_alpha)

    def update(self, pose_landmarks, hand_landmarks, now: float | None = None) -> GestureEvent | None:
        """Return a touch event after the fingertip stays near the head zone."""
        # 1. Stop early when either landmark stream is missing.
        if not pose_landmarks or not hand_landmarks:
            self._clear_pending()
            return None

        current_time = monotonic() if now is None else now
        finger_tip = hand_landmarks[INDEX_FINGER_TIP]
        head_size = pose_head_size(pose_landmarks)
        touch_radius = max(head_size * self.threshold_ratio, 0.03)

        # 2. Measure the closest fingertip-to-head distance and smooth it.
        raw_distance = min(
            distance_2d(finger_tip, pose_landmarks[landmark_index])
            for landmark_index in HEAD_LANDMARKS
        )
        closest_distance = self.distance_filter.update(raw_distance)
        if closest_distance > touch_radius:
            self._clear_pending()
            return None

        # 3. Confirm the touch across frames, then emit one cooled-down event.
        self.matched_frames += 1
        if self.matched_frames < self.confirmation_frames or not self.cooldown.is_ready(current_time):
            return None

        self.cooldown.trigger(current_time)
        self._clear_pending()
        confidence = max(0.0, 1.0 - (closest_distance / touch_radius))
        return GestureEvent(
            name="touch_head",
            confidence=confidence,
            timestamp=current_time,
            metadata={"distance": closest_distance, "threshold": touch_radius},
        )

    def reset(self) -> None:
        """Clear pending state and reopen the cooldown."""
        self._clear_pending()
        self.cooldown.reset()

    def _clear_pending(self) -> None:
        """Drop the current confirmation streak."""
        self.matched_frames = 0
        self.distance_filter.reset()
