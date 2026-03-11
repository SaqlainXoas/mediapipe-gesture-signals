"""Face-only detectors."""

from detectors.face.nod import NodDetector
from detectors.face.shake_head import ShakeHeadDetector
from detectors.face.tilt import TiltDetector

__all__ = ["NodDetector", "ShakeHeadDetector", "TiltDetector"]
