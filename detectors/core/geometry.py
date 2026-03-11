import math


def _coords(point) -> tuple[float, float, float]:
    """Return x, y, z coordinates for a landmark or tuple-like point."""
    if hasattr(point, "x"):
        return point.x, point.y, getattr(point, "z", 0.0)
    if len(point) == 2:
        return point[0], point[1], 0.0
    return point[0], point[1], point[2]


def distance_2d(a, b) -> float:
    """Return the normalized 2D distance between two points."""
    ax, ay, _ = _coords(a)
    bx, by, _ = _coords(b)
    return math.hypot(ax - bx, ay - by)


def distance_3d(a, b) -> float:
    """Return the normalized 3D distance between two points."""
    ax, ay, az = _coords(a)
    bx, by, bz = _coords(b)
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2)


def midpoint_2d(a, b) -> tuple[float, float]:
    """Return the midpoint between two points."""
    ax, ay, _ = _coords(a)
    bx, by, _ = _coords(b)
    return (ax + bx) / 2, (ay + by) / 2


def angle_degrees(a, b) -> float:
    """Return the angle from point a to point b in degrees."""
    ax, ay, _ = _coords(a)
    bx, by, _ = _coords(b)
    return math.degrees(math.atan2(by - ay, bx - ax))


def average_face_size(face_landmarks) -> float:
    """Return a face size estimate from width and height landmarks."""
    width = distance_2d(face_landmarks[234], face_landmarks[454])
    height = distance_2d(face_landmarks[10], face_landmarks[152])
    return max((width + height) / 2, 0.01)


def average_hand_size(hand_landmarks) -> float:
    """Return a hand size estimate from the wrist and middle finger base."""
    wrist_to_middle = distance_2d(hand_landmarks[0], hand_landmarks[9])
    palm_width = distance_2d(hand_landmarks[5], hand_landmarks[17])
    return max((wrist_to_middle + palm_width) / 2, 0.01)


def pose_head_size(pose_landmarks) -> float:
    """Return a head size estimate from pose nose and ear points."""
    ear_width = distance_2d(pose_landmarks[7], pose_landmarks[8])
    left_span = distance_2d(pose_landmarks[0], pose_landmarks[7])
    right_span = distance_2d(pose_landmarks[0], pose_landmarks[8])
    return max((ear_width + left_span + right_span) / 3, 0.03)
